"""Worker thread for agent execution with streaming support."""

import asyncio
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

    def start_worker(self):
        """Start the worker thread with its own event loop."""
        if self._thread is not None and self._thread.is_alive():
            return

        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()

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
        from code_puppy.messaging import get_message_bus, DiffMessage

        self._running = True
        self._cancelled = False
        self._current_response = ""
        self.agent_busy.emit(True)

        # Convert file paths to BinaryContent
        binary_attachments = self._convert_attachments(attachments)
        logger.info(f"Sending prompt with {len(binary_attachments)} attachments (from {len(attachments)} paths)")

        # Track registered callbacks for cleanup
        stream_callback_registered = False
        tool_callback_registered = False

        # Set up message bus for diff messages
        message_bus = get_message_bus()
        message_bus.mark_renderer_active()
        
        # Process any buffered messages first
        buffered = message_bus.get_buffered_messages()
        if buffered:
            logger.info(f"Processing {len(buffered)} buffered messages")
            for msg in buffered:
                if isinstance(msg, DiffMessage):
                    diff_text = "\n".join(
                        (("+" if line.type == "add" else "-" if line.type == "remove" else " ") + line.content)
                        for line in msg.diff_lines
                    )
                    self.diff_received.emit(msg.path, msg.operation, diff_text)
            message_bus.clear_buffer()

        # Retry configuration
        max_retries = 3
        retry_delay = 2.0  # seconds

        async def poll_message_bus():
            """Poll message bus for DiffMessage events."""
            msg_count = 0
            while self._running and not self._cancelled:
                msg = message_bus.get_message_nowait()
                if msg is not None:
                    msg_count += 1
                    msg_type = type(msg).__name__
                    logger.info(f"Message bus received #{msg_count}: {msg_type}")
                    if isinstance(msg, DiffMessage):
                        logger.info(f"DiffMessage for {msg.path}, operation={msg.operation}, {len(msg.diff_lines)} lines")
                        # Extract diff text from diff_lines
                        diff_text = "\n".join(
                            (("+" if line.type == "add" else "-" if line.type == "remove" else " ") + line.content)
                            for line in msg.diff_lines
                        )
                        logger.info(f"Emitting diff_received signal with {len(diff_text)} chars")
                        self.diff_received.emit(msg.path, msg.operation, diff_text)
                await asyncio.sleep(0.01)

        # Start message bus polling task
        poll_task = asyncio.create_task(poll_message_bus())

        try:
            # Register callback for streaming events
            callbacks.register_callback("stream_event", self._handle_stream_event)
            stream_callback_registered = True

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
            message_bus.mark_renderer_inactive()

            # Unregister callbacks
            if stream_callback_registered:
                callbacks.unregister_callback("stream_event", self._handle_stream_event)
            if tool_callback_registered:
                callbacks.unregister_callback("post_tool_call", self._handle_post_tool_call)

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

        try:
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
