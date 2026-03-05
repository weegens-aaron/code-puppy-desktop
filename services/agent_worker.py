"""Worker thread for agent execution with streaming support."""

import asyncio
import json
import logging
import signal
import threading
from contextlib import contextmanager
from typing import Any, Optional
from unittest.mock import patch

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


@contextmanager
def _disable_signal_handlers():
    """Disable signal.signal() when running in a non-main thread.

    The agent's run_with_mcp() tries to set up SIGINT handlers, but this
    only works in the main thread. When running in a QThread, we need to
    patch signal.signal to be a no-op.
    """
    if threading.current_thread() is threading.main_thread():
        yield
    else:
        def noop_signal(signum, handler):
            return signal.SIG_DFL
        with patch.object(signal, 'signal', noop_signal):
            yield


class AgentWorker(QObject):
    """Worker that runs agent in a separate thread with asyncio event loop.

    This worker receives streaming events via the Code Puppy callback system
    and emits Qt signals for thread-safe UI updates.
    """

    # Signals for streaming events (main agent)
    token_received = Signal(str)  # Text content delta
    thinking_started = Signal()
    thinking_content = Signal(str)  # Thinking content delta
    thinking_complete = Signal()
    tool_call_started = Signal(str, str)  # tool_name, tool_args
    tool_call_args_delta = Signal(str, str)  # tool_name, args_delta
    tool_call_complete = Signal(str)  # tool_name
    tool_output_received = Signal(str, str, dict)  # tool_name, output_type, metadata
    diff_received = Signal(str, str, str)  # filepath, operation, diff_text
    response_complete = Signal(str)  # Full response text
    error_occurred = Signal(str)  # Error message
    agent_busy = Signal(bool)  # True when agent is running

    # Signals for subagent events
    subagent_started = Signal(str, str, str)  # session_id, agent_name, prompt
    subagent_token = Signal(str, str)  # session_id, content_delta
    subagent_thinking_started = Signal(str)  # session_id
    subagent_thinking_content = Signal(str, str)  # session_id, content_delta
    subagent_thinking_complete = Signal(str)  # session_id
    subagent_tool_started = Signal(str, str, str)  # session_id, tool_name, tool_args
    subagent_tool_args_delta = Signal(str, str, str)  # session_id, tool_name, args_delta
    subagent_tool_complete = Signal(str, str)  # session_id, tool_name
    subagent_tool_output = Signal(str, str, str, dict)  # session_id, tool_name, output_type, metadata
    subagent_complete = Signal(str, str, str)  # session_id, agent_name, response

    # Signal for ask_user_question tool
    ask_user_question_requested = Signal(str)  # questions_json

    def __init__(self):
        super().__init__()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._cancelled = False
        self._running = False
        self._current_response = ""
        self._agent = None  # Cached agent reference
        self._current_task: Optional[asyncio.Task] = None  # Track current task for cancellation

        # Track active parts for proper event handling (main agent)
        self._thinking_parts: set[int] = set()
        self._text_parts: set[int] = set()
        self._tool_parts: dict[int, str] = {}  # index -> tool_name

        # Track active subagents and their parts
        self._active_subagents: set[str] = set()  # session_ids
        self._subagent_thinking_parts: dict[str, set[int]] = {}  # session_id -> indices
        self._subagent_text_parts: dict[str, set[int]] = {}  # session_id -> indices
        self._subagent_tool_parts: dict[str, dict[int, str]] = {}  # session_id -> {index: tool_name}
        self._pending_subagent_prompts: dict[str, str] = {}  # agent_name -> prompt

        # Ask user question synchronization
        self._question_event = threading.Event()
        self._question_response: Optional[dict] = None

    def start_worker(self):
        """Start the worker thread with its own event loop."""
        if self._thread is not None and self._thread.is_alive():
            return

        # Patch ask_user_question handler to use GUI
        self._patch_ask_user_question()

        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()

    def _patch_ask_user_question(self):
        """Patch the ask_user_question tool to use our GUI handler."""
        try:
            from code_puppy.tools.ask_user_question import registration as auq_registration

            # Store original for potential restoration
            self._original_ask_user_question = auq_registration._ask_user_question_impl

            # Create a wrapper that uses our GUI handler
            def gui_handler_wrapper(questions, timeout=300):
                logger.info(f"GUI ask_user_question called with {len(questions)} questions")
                return self._gui_ask_user_question(questions)

            # Patch the implementation reference in the registration module
            auq_registration._ask_user_question_impl = gui_handler_wrapper
            logger.info("Patched ask_user_question to use GUI handler")

        except ImportError as e:
            logger.warning(f"Could not patch ask_user_question: {e}")
        except Exception as e:
            logger.error(f"Error patching ask_user_question: {e}", exc_info=True)

    def prewarm(self):
        """Pre-initialize agent and MCP connections to reduce first-message latency."""
        if self._loop is None:
            return

        asyncio.run_coroutine_threadsafe(self._prewarm_async(), self._loop)

    async def _prewarm_async(self):
        """Async prewarm - initialize agent and connect MCP servers."""
        try:
            # Initialize the agent
            agent = self.get_agent()
            if agent:
                # Clear any history from previous sessions
                agent.clear_message_history()
                logger.info("Cleared agent history from previous session")

                # Pre-connect MCP servers if the agent supports it
                if hasattr(agent, 'ensure_mcp_connected'):
                    await agent.ensure_mcp_connected()
                elif hasattr(agent, 'mcp_manager') and agent.mcp_manager:
                    # Try to initialize MCP connections
                    if hasattr(agent.mcp_manager, 'ensure_connected'):
                        await agent.mcp_manager.ensure_connected()
            logger.info("Agent pre-warmed successfully")
        except Exception as e:
            logger.warning(f"Prewarm failed (non-fatal): {e}")

    def _run_event_loop(self):
        """Run the asyncio event loop in the worker thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            self._loop.run_forever()
        finally:
            self._loop.close()
            self._loop = None

    def stop_worker(self):
        """Stop the worker thread."""
        if self._loop is not None:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None

    def run_agent(self, prompt: str, attachments: Optional[list] = None):
        """Queue an agent run in the worker thread."""
        if self._loop is None:
            self.error_occurred.emit("Worker thread not started")
            return

        if self._running:
            self.error_occurred.emit("Agent is already running")
            return

        attachments = attachments or []

        # Schedule the async task wrapper in the worker's event loop
        asyncio.run_coroutine_threadsafe(
            self._run_agent_task(prompt, attachments),
            self._loop
        )

    async def _run_agent_task(self, prompt: str, attachments: list):
        """Wrapper to create and track the agent task for cancellation."""
        self._current_task = asyncio.current_task()
        try:
            await self._execute_agent(prompt, attachments)
        finally:
            self._current_task = None

    def get_agent(self):
        """Get or create the cached agent instance."""
        from code_puppy.agents import get_current_agent
        if self._agent is None:
            self._agent = get_current_agent()
        return self._agent

    def clear_agent(self):
        """Clear the cached agent (for new chat or agent switch).

        This clears the message history and forces a fresh agent reference
        on the next call to get_agent().
        """
        if self._agent:
            self._agent.clear_message_history()
            logger.info("Cleared agent message history")
        self._agent = None

    def set_question_response(self, response: dict):
        """Set the response to an ask_user_question request (called from main thread).

        Args:
            response: Dict with structure matching QuestionDialog.get_results()
        """
        self._question_response = response
        self._question_event.set()
        logger.info(f"Question response set: cancelled={response.get('cancelled', False)}")

    def _gui_ask_user_question(self, questions: list[dict]) -> Any:
        """Custom ask_user_question handler for GUI mode.

        Emits a signal to show the dialog and blocks until response is received.
        """
        from code_puppy.tools.ask_user_question.models import (
            AskUserQuestionOutput,
            QuestionAnswer,
        )

        # Clear any previous state
        self._question_event.clear()
        self._question_response = None

        # Emit signal with questions (will be handled in main thread)
        questions_json = json.dumps(questions)
        self.ask_user_question_requested.emit(questions_json)
        logger.info(f"Emitted ask_user_question_requested with {len(questions)} questions")

        # Wait for response from main thread (with timeout to allow cancellation checks)
        while not self._cancelled:
            if self._question_event.wait(timeout=0.1):
                break

        if self._cancelled:
            return AskUserQuestionOutput.cancelled_response()

        response = self._question_response
        if response is None or response.get("cancelled", False):
            return AskUserQuestionOutput.cancelled_response()

        # Convert response to AskUserQuestionOutput format
        answers = []
        for answer_data in response.get("answers", []):
            answers.append(QuestionAnswer(
                question_header=answer_data.get("question_header", ""),
                selected_options=answer_data.get("selected_options", []),
                other_text=answer_data.get("other_text"),
            ))

        return AskUserQuestionOutput(answers=answers)

    def _convert_attachments(self, file_paths: list) -> list:
        """Convert file paths to BinaryContent objects."""
        from pydantic_ai import BinaryContent
        import mimetypes
        from pathlib import Path

        binary_attachments = []
        for file_path in file_paths:
            try:
                path = Path(file_path)
                if not path.exists() or not path.is_file():
                    continue

                # Determine media type
                mime_type, _ = mimetypes.guess_type(str(path))
                if not mime_type:
                    mime_type = "application/octet-stream"

                # Load file data
                data = path.read_bytes()
                binary_attachments.append(BinaryContent(data=data, media_type=mime_type))
            except Exception as e:
                logger.warning(f"Failed to load attachment {file_path}: {e}")

        return binary_attachments

    async def _execute_agent(self, prompt: str, attachments: list):
        """Execute agent asynchronously in the worker thread."""
        from code_puppy import callbacks
        from code_puppy.messaging import (
            get_message_bus, DiffMessage,
            SubAgentInvocationMessage, SubAgentResponseMessage,
        )

        self._running = True
        self._cancelled = False
        self._current_response = ""
        self.agent_busy.emit(True)

        # Convert file paths to BinaryContent
        binary_attachments = self._convert_attachments(attachments)
        logger.info(f"Sending prompt with {len(binary_attachments)} attachments (from {len(attachments)} paths)")

        # Track registered callbacks for cleanup
        stream_callback_registered = False
        pre_tool_callback_registered = False
        tool_callback_registered = False

        # Set up message bus for diff messages and subagent events
        message_bus = get_message_bus()
        # Mark renderer active so messages are queued instead of buffered
        message_bus.mark_renderer_active()
        logger.info(f"MessageBus marked active, has_active_renderer={message_bus.has_active_renderer}")

        # Retry configuration
        max_retries = 3
        retry_delay = 2.0  # seconds

        poll_count = 0
        async def poll_message_bus():
            """Poll message bus for DiffMessage and SubAgent events."""
            nonlocal poll_count
            while self._running and not self._cancelled:
                poll_count += 1
                if poll_count % 100 == 0:  # Log every 100 polls (~1 second)
                    logger.debug(f"MessageBus poll #{poll_count}, queue_size={message_bus.outgoing_qsize}")
                msg = message_bus.get_message_nowait()
                if msg is not None:
                    logger.info(f"MessageBus received: {type(msg).__name__}")
                    if isinstance(msg, DiffMessage):
                        # Extract diff text from diff_lines
                        diff_text = "\n".join(
                            (("+" if line.type == "add" else "-" if line.type == "remove" else " ") + line.content)
                            for line in msg.diff_lines
                        )
                        self.diff_received.emit(msg.path, msg.operation, diff_text)
                    elif isinstance(msg, SubAgentInvocationMessage):
                        # Subagent is starting
                        session_id = msg.session_id
                        self._active_subagents.add(session_id)
                        self._subagent_thinking_parts[session_id] = set()
                        self._subagent_text_parts[session_id] = set()
                        self._subagent_tool_parts[session_id] = {}
                        self.subagent_started.emit(session_id, msg.agent_name, msg.prompt)
                        logger.info(f"Subagent started: {msg.agent_name} ({session_id})")
                    elif isinstance(msg, SubAgentResponseMessage):
                        # Subagent completed
                        session_id = msg.session_id
                        self._active_subagents.discard(session_id)
                        self._subagent_thinking_parts.pop(session_id, None)
                        self._subagent_text_parts.pop(session_id, None)
                        self._subagent_tool_parts.pop(session_id, None)
                        self.subagent_complete.emit(session_id, msg.agent_name, msg.response)
                        logger.info(f"Subagent completed: {msg.agent_name} ({session_id})")
                await asyncio.sleep(0.01)

        # Start message bus polling task
        poll_task = asyncio.create_task(poll_message_bus())

        try:
            # Register callback for streaming events
            callbacks.register_callback("stream_event", self._handle_stream_event)
            stream_callback_registered = True

            # Register callback for pre-tool to detect subagent invocations
            callbacks.register_callback("pre_tool_call", self._handle_pre_tool_call)
            pre_tool_callback_registered = True

            # Register callback for tool outputs
            callbacks.register_callback("post_tool_call", self._handle_post_tool_call)
            tool_callback_registered = True

            agent = self.get_agent()
            if not agent:
                self.error_occurred.emit("No agent available")
                return

            # Run the agent with retry logic
            last_error = None
            for attempt in range(1, max_retries + 1):
                if self._cancelled:
                    return

                try:
                    # Disable signal handlers since we're not in main thread
                    with _disable_signal_handlers():
                        result = await agent.run_with_mcp(prompt, attachments=binary_attachments)

                    if self._cancelled:
                        return

                    # Extract response text
                    if result and hasattr(result, 'output'):
                        response_text = str(result.output) if result.output else self._current_response
                    else:
                        response_text = self._current_response

                    self.response_complete.emit(response_text)
                    return  # Success, exit retry loop

                except asyncio.CancelledError:
                    raise  # Don't retry on cancellation
                except Exception as e:
                    last_error = e
                    if attempt < max_retries:
                        logger.warning(f"Agent request failed (attempt {attempt}/{max_retries}): {e}")
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        # Clear partial response for retry
                        self._current_response = ""
                    else:
                        logger.error(f"Agent request failed after {max_retries} attempts: {e}", exc_info=True)

            # All retries exhausted
            if last_error:
                self.error_occurred.emit(f"Failed after {max_retries} attempts: {last_error}")

        except asyncio.CancelledError:
            logger.info("Agent execution cancelled")
        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            self.error_occurred.emit(str(e))
        finally:
            # Stop message bus polling
            poll_task.cancel()
            try:
                await poll_task
            except asyncio.CancelledError:
                pass

            # Mark renderer inactive
            message_bus.mark_renderer_inactive()

            # Unregister callbacks
            if stream_callback_registered:
                callbacks.unregister_callback("stream_event", self._handle_stream_event)
            if pre_tool_callback_registered:
                callbacks.unregister_callback("pre_tool_call", self._handle_pre_tool_call)
            if tool_callback_registered:
                callbacks.unregister_callback("post_tool_call", self._handle_post_tool_call)

            self._running = False
            self.agent_busy.emit(False)

            # Clean up tracking state
            self._thinking_parts.clear()
            self._text_parts.clear()
            self._tool_parts.clear()
            self._active_subagents.clear()
            self._subagent_thinking_parts.clear()
            self._subagent_text_parts.clear()
            self._subagent_tool_parts.clear()
            self._pending_subagent_prompts.clear()

    async def _handle_stream_event(
        self, event_type: str, event_data: Any, agent_session_id: str | None = None
    ):
        """Handle streaming events from the agent callback system.

        Routes events to main agent or subagent based on agent_session_id.
        """
        if self._cancelled:
            return

        try:
            # Check if this is a subagent event (has a session_id)
            if agent_session_id:
                # If we haven't seen this subagent yet, register it
                if agent_session_id not in self._active_subagents:
                    self._register_new_subagent(agent_session_id)

                # Route to subagent handler
                if event_type == "part_start":
                    self._on_subagent_part_start(agent_session_id, event_data)
                elif event_type == "part_delta":
                    self._on_subagent_part_delta(agent_session_id, event_data)
                elif event_type == "part_end":
                    self._on_subagent_part_end(agent_session_id, event_data)
            else:
                # Main agent event
                if event_type == "part_start":
                    self._on_part_start(event_data)
                elif event_type == "part_delta":
                    self._on_part_delta(event_data)
                elif event_type == "part_end":
                    self._on_part_end(event_data)
        except Exception as e:
            logger.error(f"Error handling stream event: {e}", exc_info=True)

    def _register_new_subagent(self, session_id: str):
        """Register a new subagent when we first see its stream events."""
        # Parse agent name from session_id (e.g., "qa-expert-session-a3f2b1" -> "qa-expert")
        agent_name = session_id
        if "-session-" in session_id:
            agent_name = session_id.rsplit("-session-", 1)[0]

        # Initialize tracking for this subagent
        self._active_subagents.add(session_id)
        self._subagent_thinking_parts[session_id] = set()
        self._subagent_text_parts[session_id] = set()
        self._subagent_tool_parts[session_id] = {}

        logger.info(f"Registered new subagent: {agent_name} ({session_id})")
        # Get the prompt from pending invocations if available
        prompt = self._pending_subagent_prompts.pop(agent_name, "")
        self.subagent_started.emit(session_id, agent_name, prompt)

    def _on_part_start(self, event_data: dict):
        """Handle part_start event."""
        index = event_data.get("index", 0)
        part_type = event_data.get("part_type", "")
        part = event_data.get("part")

        if part_type == "ThinkingPart":
            self._thinking_parts.add(index)
            self.thinking_started.emit()
            # If there's initial content, emit it
            if part and hasattr(part, 'content') and part.content:
                self.thinking_content.emit(part.content)
        elif part_type == "TextPart":
            self._text_parts.add(index)
            # If there's initial content, emit it
            if part and hasattr(part, 'content') and part.content:
                self.token_received.emit(part.content)
                self._current_response += part.content
        elif part_type == "ToolCallPart":
            tool_name = part.tool_name if part and hasattr(part, 'tool_name') else "unknown"
            self._tool_parts[index] = tool_name
            # Get args if available
            tool_args = ""
            if part and hasattr(part, 'args'):
                if isinstance(part.args, dict):
                    import json
                    tool_args = json.dumps(part.args, indent=2)
                else:
                    tool_args = str(part.args) if part.args else ""
            self.tool_call_started.emit(tool_name, tool_args)

    def _on_part_delta(self, event_data: dict):
        """Handle part_delta event."""
        index = event_data.get("index", 0)
        delta = event_data.get("delta")

        if delta is None:
            return

        # Get content delta
        content_delta = getattr(delta, 'content_delta', None)

        if index in self._thinking_parts:
            if content_delta:
                self.thinking_content.emit(content_delta)
        elif index in self._text_parts:
            if content_delta:
                self.token_received.emit(content_delta)
                self._current_response += content_delta
        elif index in self._tool_parts:
            # Tool call deltas - update args display
            args_delta = getattr(delta, 'args_delta', None)
            if args_delta:
                tool_name = self._tool_parts.get(index, "unknown")
                self.tool_call_args_delta.emit(tool_name, args_delta)

    def _on_part_end(self, event_data: dict):
        """Handle part_end event."""
        index = event_data.get("index", 0)

        if index in self._thinking_parts:
            self._thinking_parts.discard(index)
            self.thinking_complete.emit()
        elif index in self._text_parts:
            self._text_parts.discard(index)
        elif index in self._tool_parts:
            tool_name = self._tool_parts.pop(index, "unknown")
            self.tool_call_complete.emit(tool_name)

    # -------------------------------------------------------------------------
    # Subagent event handlers
    # -------------------------------------------------------------------------

    def _on_subagent_part_start(self, session_id: str, event_data: dict):
        """Handle part_start event for a subagent."""
        index = event_data.get("index", 0)
        part_type = event_data.get("part_type", "")
        part = event_data.get("part")

        thinking_parts = self._subagent_thinking_parts.get(session_id, set())
        text_parts = self._subagent_text_parts.get(session_id, set())
        tool_parts = self._subagent_tool_parts.get(session_id, {})

        if part_type == "ThinkingPart":
            thinking_parts.add(index)
            self._subagent_thinking_parts[session_id] = thinking_parts
            self.subagent_thinking_started.emit(session_id)
            if part and hasattr(part, 'content') and part.content:
                self.subagent_thinking_content.emit(session_id, part.content)
        elif part_type == "TextPart":
            text_parts.add(index)
            self._subagent_text_parts[session_id] = text_parts
            if part and hasattr(part, 'content') and part.content:
                self.subagent_token.emit(session_id, part.content)
        elif part_type == "ToolCallPart":
            # Extract tool name with multiple fallbacks
            tool_name = "unknown"
            if part:
                if hasattr(part, 'tool_name') and part.tool_name:
                    tool_name = part.tool_name
                elif hasattr(part, 'name') and part.name:
                    tool_name = part.name
                elif isinstance(part, dict):
                    tool_name = part.get('tool_name', part.get('name', 'unknown'))

            tool_parts[index] = tool_name
            self._subagent_tool_parts[session_id] = tool_parts

            # Extract tool args
            tool_args = ""
            if part:
                args = None
                if hasattr(part, 'args'):
                    args = part.args
                elif hasattr(part, 'arguments'):
                    args = part.arguments
                elif isinstance(part, dict):
                    args = part.get('args', part.get('arguments'))

                if args:
                    if isinstance(args, dict):
                        tool_args = json.dumps(args, indent=2)
                    elif isinstance(args, str):
                        tool_args = args
                    else:
                        tool_args = str(args)

            self.subagent_tool_started.emit(session_id, tool_name, tool_args)
            logger.debug(f"Subagent {session_id} tool call: {tool_name}")

    def _on_subagent_part_delta(self, session_id: str, event_data: dict):
        """Handle part_delta event for a subagent."""
        index = event_data.get("index", 0)
        delta = event_data.get("delta")

        if delta is None:
            return

        content_delta = getattr(delta, 'content_delta', None)
        thinking_parts = self._subagent_thinking_parts.get(session_id, set())
        text_parts = self._subagent_text_parts.get(session_id, set())
        tool_parts = self._subagent_tool_parts.get(session_id, {})

        if index in thinking_parts:
            if content_delta:
                self.subagent_thinking_content.emit(session_id, content_delta)
        elif index in text_parts:
            if content_delta:
                self.subagent_token.emit(session_id, content_delta)
        elif index in tool_parts:
            args_delta = getattr(delta, 'args_delta', None)
            if args_delta:
                tool_name = tool_parts.get(index, "unknown")
                self.subagent_tool_args_delta.emit(session_id, tool_name, args_delta)

    def _on_subagent_part_end(self, session_id: str, event_data: dict):
        """Handle part_end event for a subagent."""
        index = event_data.get("index", 0)

        thinking_parts = self._subagent_thinking_parts.get(session_id, set())
        text_parts = self._subagent_text_parts.get(session_id, set())
        tool_parts = self._subagent_tool_parts.get(session_id, {})

        if index in thinking_parts:
            thinking_parts.discard(index)
            self._subagent_thinking_parts[session_id] = thinking_parts
            self.subagent_thinking_complete.emit(session_id)
        elif index in text_parts:
            text_parts.discard(index)
            self._subagent_text_parts[session_id] = text_parts
        elif index in tool_parts:
            tool_name = tool_parts.pop(index, "unknown")
            self._subagent_tool_parts[session_id] = tool_parts
            self.subagent_tool_complete.emit(session_id, tool_name)

    async def _handle_pre_tool_call(
        self,
        tool_name: str,
        tool_args: dict,
        context: Any = None,
    ):
        """Handle pre-tool-call callback to detect subagent invocations."""
        if self._cancelled:
            return

        # Detect invoke_agent tool call - store prompt for when we see the stream events
        if tool_name == "invoke_agent":
            agent_name = tool_args.get("agent_name", "unknown")
            prompt = tool_args.get("prompt", "")
            # Store prompt so we can use it when we register the subagent from stream events
            self._pending_subagent_prompts[agent_name] = prompt
            logger.info(f"Detected invoke_agent for: {agent_name}")

    async def _handle_post_tool_call(
        self,
        tool_name: str,
        tool_args: dict,
        result: Any,
        duration_ms: float,
        context: Any = None,
    ):
        """Handle post-tool-call callback to capture structured output.

        Delegates extraction to ToolOutputExtractor (SoC) and emits signal
        with appropriate output type and metadata for UI rendering.

        Note: file_edit outputs are handled via the message bus (DiffMessage)
        to capture the diff before it's stripped from the result.
        """
        if self._cancelled:
            return

        # Detect invoke_agent completion
        if tool_name == "invoke_agent":
            agent_name = tool_args.get("agent_name", "unknown")

            # Find the session_id for this agent in our active subagents
            session_id = None
            for sid in list(self._active_subagents):
                if sid.startswith(f"{agent_name}-session-"):
                    session_id = sid
                    break

            if session_id:
                # Clean up subagent tracking
                self._active_subagents.discard(session_id)
                self._subagent_thinking_parts.pop(session_id, None)
                self._subagent_text_parts.pop(session_id, None)
                self._subagent_tool_parts.pop(session_id, None)

                # Extract response from result - handle various result types
                response = ""
                if result:
                    if hasattr(result, 'response'):
                        # InvokeAgentOutput model
                        response = result.response or ""
                    elif hasattr(result, 'output'):
                        response = str(result.output) if result.output else ""
                    elif isinstance(result, str):
                        response = result
                    elif isinstance(result, dict):
                        response = result.get('response', result.get('output', str(result)))
                    else:
                        # Last resort - try to get string representation
                        response = str(result)

                logger.info(f"Subagent completed: {agent_name} ({session_id})")
                self.subagent_complete.emit(session_id, agent_name, response)
            else:
                logger.warning(f"Could not find session for completed subagent: {agent_name}")

            return  # Don't process as regular tool output

        try:
            from utils.tool_output_extractor import ToolOutputExtractor

            output_type, metadata = ToolOutputExtractor.extract(tool_name, tool_args, result)

            # Skip file_edit - we get these from the message bus with the diff intact
            if output_type == "file_edit":
                return

            if output_type:
                metadata["tool_name"] = tool_name
                metadata["duration_ms"] = duration_ms
                # Add duration for shell commands
                if output_type == "shell":
                    metadata["duration"] = duration_ms / 1000.0
                self.tool_output_received.emit(tool_name, output_type, metadata)
        except Exception as e:
            logger.error(f"Error handling post_tool_call: {e}", exc_info=True)

    def cancel(self):
        """Cancel the current operation."""
        self._cancelled = True

        # Cancel the asyncio task if running
        if self._current_task and self._loop:
            self._loop.call_soon_threadsafe(self._cancel_task)

    def _cancel_task(self):
        """Cancel the current task (called from event loop thread)."""
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            logger.info("Agent task cancelled")

    @property
    def is_running(self) -> bool:
        """Check if agent is currently running."""
        return self._running
