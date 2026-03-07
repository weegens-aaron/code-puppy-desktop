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

from utils.error_utils import get_error_capturer

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

    # Signals for streaming events
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

        # Track active parts for proper event handling
        self._thinking_parts: set[int] = set()
        self._text_parts: set[int] = set()
        self._tool_parts: dict[int, str] = {}  # index -> tool_name

        # Ask user question synchronization
        self._question_event = threading.Event()
        self._question_response: Optional[dict] = None

        # Error capture from agent_run_end hook
        self._last_agent_error: Optional[str] = None
        self._last_agent_success: bool = True

    def start_worker(self):
        """Start the worker thread with its own event loop."""
        if self._thread is not None and self._thread.is_alive():
            return

        # Initialize error capturer to patch MessageQueue early
        get_error_capturer()

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
        """Async prewarm - initialize agent and start enabled MCP servers."""
        try:
            # Initialize the agent
            agent = self.get_agent()
            if agent:
                # Clear any history from previous sessions
                agent.clear_message_history()
                logger.info("Cleared agent history from previous session")

            # Start all enabled MCP servers
            await self._start_enabled_mcp_servers()

            logger.info("Agent pre-warmed successfully")
        except Exception as e:
            logger.warning(f"Prewarm failed (non-fatal): {e}")

    async def _start_enabled_mcp_servers(self):
        """Start all enabled MCP servers that aren't already running."""
        try:
            from code_puppy.mcp_.manager import get_mcp_manager
            from code_puppy.mcp_.managed_server import ServerState

            manager = get_mcp_manager()
            servers = manager.list_servers()

            started_count = 0
            for server in servers:
                # Only start enabled servers that aren't already running
                if server.enabled and server.state not in (ServerState.RUNNING, ServerState.STARTING):
                    try:
                        success = await manager.start_server(server.id)
                        if success:
                            started_count += 1
                            logger.info(f"Started MCP server: {server.name}")
                        else:
                            logger.warning(f"Failed to start MCP server: {server.name}")
                    except Exception as e:
                        logger.warning(f"Error starting MCP server {server.name}: {e}")

            if started_count > 0:
                logger.info(f"Started {started_count} MCP server(s)")
            elif servers:
                logger.debug("All enabled MCP servers already running or none configured")

        except ImportError as e:
            logger.debug(f"MCP module not available: {e}")
        except Exception as e:
            logger.warning(f"Failed to start MCP servers: {e}")

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
            get_message_bus, DiffMessage, TextMessage, MessageLevel,
            get_global_queue, MessageType,  # Legacy queue for error capture
        )

        self._running = True
        self._cancelled = False
        self._current_response = ""
        self.agent_busy.emit(True)

        # Track state for cleanup - must be set before any potential exception
        stream_callback_registered = False
        tool_callback_registered = False
        agent_run_end_registered = False
        poll_task = None
        message_bus = None
        legacy_queue = None

        # Clear previous error state
        self._last_agent_error = None
        self._last_agent_success = True
        self._captured_error_messages: list[str] = []  # Capture errors from legacy queue

        # Clear and get error capturer for capturing error messages
        error_capturer = get_error_capturer()
        error_capturer.clear()

        try:
            # Convert file paths to BinaryContent
            binary_attachments = self._convert_attachments(attachments)
            logger.info(f"Sending prompt with {len(binary_attachments)} attachments (from {len(attachments)} paths)")

            # Set up message bus for diff messages
            message_bus = get_message_bus()
            # Mark renderer active so messages are queued instead of buffered
            message_bus.mark_renderer_active()
            logger.info(f"MessageBus marked active, has_active_renderer={message_bus.has_active_renderer}")

            # Retry configuration
            max_retries = 3
            retry_delay = 2.0  # seconds

            # Get legacy queue for error message capture
            legacy_queue = get_global_queue()

            poll_count = 0
            async def poll_message_bus():
                """Poll message bus for DiffMessage and legacy queue for error messages."""
                nonlocal poll_count
                while self._running and not self._cancelled:
                    poll_count += 1
                    if poll_count % 100 == 0:  # Log every 100 polls (~1 second)
                        logger.debug(f"MessageBus poll #{poll_count}, queue_size={message_bus.outgoing_qsize}")

                    # Poll new message bus for diff messages
                    msg = message_bus.get_message_nowait()
                    if msg is not None:
                        logger.debug(f"MessageBus received: {type(msg).__name__}")
                        if isinstance(msg, DiffMessage):
                            # Extract diff text from diff_lines
                            diff_text = "\n".join(
                                (("+" if line.type == "add" else "-" if line.type == "remove" else " ") + line.content)
                                for line in msg.diff_lines
                            )
                            self.diff_received.emit(msg.path, msg.operation, diff_text)

                    # Poll legacy queue for error messages
                    legacy_msg = legacy_queue.get_nowait()
                    if legacy_msg is not None:
                        # Check for error/warning messages
                        if legacy_msg.type in (MessageType.ERROR, MessageType.WARNING, MessageType.INFO):
                            content = str(legacy_msg.content) if legacy_msg.content else ""
                            # Check for error indicators
                            if any(indicator in content.lower() for indicator in [
                                'unexpected error', 'error:', 'failed', 'status_code:',
                                'bad request', 'unauthorized', 'forbidden', 'not found',
                                'does not appear to support', 'api error', 'connection error',
                                'usage limit', 'mcp server error'
                            ]):
                                logger.info(f"Captured error from legacy queue: {content[:100]}")
                                self._captured_error_messages.append(content)

                    await asyncio.sleep(0.01)

            # Start message bus polling task
            poll_task = asyncio.create_task(poll_message_bus())
            # Register callback for streaming events
            callbacks.register_callback("stream_event", self._handle_stream_event)
            stream_callback_registered = True

            # Register callback for tool outputs
            callbacks.register_callback("post_tool_call", self._handle_post_tool_call)
            tool_callback_registered = True

            # Register callback for agent run completion (captures errors)
            callbacks.register_callback("agent_run_end", self._handle_agent_run_end)
            agent_run_end_registered = True

            agent = self.get_agent()
            if not agent:
                self.error_occurred.emit("No agent available")
                return

            # Ensure enabled MCP servers are started before running agent
            await self._start_enabled_mcp_servers()

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

                    # Check for error indicators in the result
                    if result:
                        # Check common error attributes
                        if hasattr(result, 'error') and result.error:
                            error_msg = str(result.error)
                            logger.error(f"Agent returned error in result: {error_msg}")
                            self.error_occurred.emit(error_msg)
                            return

                        if hasattr(result, 'status') and result.status == 'error':
                            error_msg = getattr(result, 'message', 'Unknown error')
                            logger.error(f"Agent returned error status: {error_msg}")
                            self.error_occurred.emit(str(error_msg))
                            return

                    # Extract response text
                    if result and hasattr(result, 'output'):
                        response_text = str(result.output) if result.output else self._current_response
                    else:
                        response_text = self._current_response

                    # Check if agent_run_end captured an error (error swallowed by agent code)
                    if not response_text.strip() and not self._current_response.strip():
                        # Priority 1: Error from agent_run_end hook
                        if self._last_agent_error:
                            logger.warning(f"Agent completed with error (from hook): {self._last_agent_error}")
                            self.error_occurred.emit(self._last_agent_error)
                            return

                        # Priority 2: Error messages captured from message bus
                        if self._captured_error_messages:
                            error_msg = self._captured_error_messages[-1]
                            logger.warning(f"Agent completed with error (from message bus): {error_msg}")
                            self.error_occurred.emit(error_msg)
                            return

                        # Priority 3: Errors captured from MessageQueue
                        captured_error = error_capturer.get_last_error()
                        if captured_error:
                            logger.warning(f"Agent completed with error (from capturer): {captured_error}")
                            self.error_occurred.emit(captured_error)
                            return

                        # Priority 4: agent_run_end reported failure
                        if not self._last_agent_success:
                            logger.warning("Agent completed unsuccessfully but no error details")
                            self.error_occurred.emit("Agent request failed - check console output for details")
                            return

                        # Last resort: emit empty response (app.py will handle)
                        logger.warning("Agent completed with no response content")

                    # Update agent message history and trigger autosave
                    # This mirrors the CLI behavior in cli_runner.py
                    try:
                        if result and hasattr(result, 'all_messages'):
                            agent.set_message_history(list(result.all_messages()))
                            logger.info("Updated agent message history for session persistence")

                        # Trigger autosave if enabled
                        from code_puppy.config import auto_save_session_if_enabled
                        auto_save_session_if_enabled()
                        logger.debug("Autosave triggered")
                    except Exception as e:
                        logger.warning(f"Failed to update message history or autosave: {e}")

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
            # Stop message bus polling (if started)
            if poll_task is not None:
                poll_task.cancel()
                try:
                    await poll_task
                except asyncio.CancelledError:
                    pass

            # Mark renderer inactive (if message_bus was created)
            if message_bus is not None:
                message_bus.mark_renderer_inactive()

            # Unregister callbacks
            if stream_callback_registered:
                callbacks.unregister_callback("stream_event", self._handle_stream_event)
            if tool_callback_registered:
                callbacks.unregister_callback("post_tool_call", self._handle_post_tool_call)
            if agent_run_end_registered:
                callbacks.unregister_callback("agent_run_end", self._handle_agent_run_end)

            self._running = False
            self.agent_busy.emit(False)

            # Clean up tracking state
            self._thinking_parts.clear()
            self._text_parts.clear()
            self._tool_parts.clear()

    async def _handle_stream_event(
        self, event_type: str, event_data: Any, agent_session_id: str | None = None
    ):
        """Handle streaming events from the agent callback system."""
        if self._cancelled:
            return

        # Skip subagent events - they're handled by the CLI
        if agent_session_id:
            return

        try:
            # Main agent event
            if event_type == "part_start":
                self._on_part_start(event_data)
            elif event_type == "part_delta":
                self._on_part_delta(event_data)
            elif event_type == "part_end":
                self._on_part_end(event_data)
        except Exception as e:
            logger.error(f"Error handling stream event: {e}", exc_info=True)

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

        # Skip invoke_agent - subagent activity is shown in CLI
        if tool_name == "invoke_agent":
            return

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

    async def _handle_agent_run_end(
        self,
        agent_name: str,
        model_name: str,
        session_id: str | None = None,
        success: bool = True,
        error: Exception | None = None,
        response_text: str | None = None,
        metadata: dict | None = None,
    ):
        """Handle agent_run_end callback to capture errors.

        This callback fires at the end of run_with_mcp (in finally block),
        giving us access to any error that occurred, even if it was caught
        and not re-raised.
        """
        self._last_agent_success = success
        if error:
            # Format the error message
            error_str = str(error)
            # Handle tuple-like error args
            if hasattr(error, 'args') and error.args:
                if len(error.args) == 1:
                    error_str = str(error.args[0])
                else:
                    error_str = str(error.args)
            self._last_agent_error = error_str
            logger.info(f"agent_run_end captured error: {error_str[:200]}")
        elif not success:
            self._last_agent_error = "Agent run failed (no error details)"
            logger.info("agent_run_end: success=False but no error provided")

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
