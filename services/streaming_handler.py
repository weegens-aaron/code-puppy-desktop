"""Streaming token and message handling.

Separates streaming/buffering concerns from the main application (SRP/SoC).
"""

from typing import Optional, Callable

from PySide6.QtCore import QTimer, QObject

from models.data_types import Message, MessageRole
from models.message_model import MessageModel


class StreamingHandler(QObject):
    """Handles streaming tokens and message index tracking.

    Responsibilities:
    - Token buffering with throttled UI updates
    - Message index tracking (assistant, thinking, tool calls)
    - Coordinating message creation/updates during streaming
    """

    def __init__(
        self,
        message_model: MessageModel,
        flush_interval_ms: int = 50,
        parent: Optional[QObject] = None
    ):
        super().__init__(parent)
        self._model = message_model

        # Token buffering for throttled UI updates
        self._token_buffer: list[str] = []
        self._token_timer = QTimer(self)
        self._token_timer.setInterval(flush_interval_ms)
        self._token_timer.timeout.connect(self._flush_token_buffer)

        # Track current message indices for streaming updates
        self._current_thinking_index: int | None = None
        self._current_tool_indices: dict[str, int] = {}  # tool_name -> message index
        self._assistant_message_index: int | None = None

    @property
    def token_timer(self) -> QTimer:
        """Get the token timer for cleanup."""
        return self._token_timer

    def set_message_model(self, model: MessageModel):
        """Switch to a different message model (for tab switching).

        Args:
            model: The new message model to use
        """
        # Flush any pending tokens to the old model first
        self.flush_and_stop()
        self.reset_indices()
        self._model = model

    # -------------------------------------------------------------------------
    # Token Streaming
    # -------------------------------------------------------------------------

    def handle_token(self, token: str):
        """Handle a streaming token from the agent.

        Tokens are buffered and flushed periodically for performance.
        """
        self._token_buffer.append(token)
        if not self._token_timer.isActive():
            self._token_timer.start()

    def _flush_token_buffer(self):
        """Flush buffered tokens to UI."""
        if not self._token_buffer:
            return

        # Join all buffered tokens and update UI once
        combined = "".join(self._token_buffer)
        self._token_buffer.clear()

        # Create assistant message on first token
        if self._assistant_message_index is None:
            self._assistant_message_index = self._model.add_message(
                Message(role=MessageRole.ASSISTANT, content=combined)
            )
        else:
            # Append to the specific assistant message
            self._model.append_to_message(self._assistant_message_index, combined)

    def flush_and_stop(self):
        """Flush any remaining tokens and stop the timer."""
        self._token_timer.stop()
        self._flush_token_buffer()

    # -------------------------------------------------------------------------
    # Thinking Messages
    # -------------------------------------------------------------------------

    def start_thinking(self) -> int:
        """Start a thinking message.

        Returns:
            The message index of the thinking message
        """
        # Reset assistant message index so any prior text is finalized
        self._assistant_message_index = None

        # Create thinking message
        self._current_thinking_index = self._model.add_message(
            Message(role=MessageRole.THINKING, content="")
        )
        return self._current_thinking_index

    def append_thinking(self, content: str):
        """Append content to the current thinking message."""
        if self._current_thinking_index is not None:
            self._model.append_to_message(self._current_thinking_index, content)

    def complete_thinking(self):
        """Complete the current thinking message."""
        self._current_thinking_index = None
        # Reset assistant message index so text after thinking gets a new bubble
        self._assistant_message_index = None

    # -------------------------------------------------------------------------
    # Tool Call Messages
    # -------------------------------------------------------------------------

    def start_tool_call(self, tool_name: str, tool_args: str) -> int:
        """Start a tool call message.

        Args:
            tool_name: Name of the tool being called
            tool_args: Initial arguments (may be empty)

        Returns:
            The message index of the tool call message
        """
        # Reset assistant message index
        self._assistant_message_index = None

        # Create tool call message
        index = self._model.add_message(
            Message(
                role=MessageRole.TOOL_CALL,
                content=tool_args or "(no arguments)",
                metadata={"tool_name": tool_name}
            )
        )
        self._current_tool_indices[tool_name] = index
        return index

    def append_tool_args(self, tool_name: str, args_delta: str):
        """Append streaming arguments to a tool call."""
        if tool_name not in self._current_tool_indices:
            return

        index = self._current_tool_indices[tool_name]
        msg = self._model.get_message(index)

        if msg and msg.content == "(no arguments)":
            # Replace placeholder with actual args
            self._model.update_message_content(index, args_delta)
        else:
            self._model.append_to_message(index, args_delta)

    def complete_tool_call(self, tool_name: str):
        """Complete a tool call message."""
        if tool_name in self._current_tool_indices:
            del self._current_tool_indices[tool_name]

    def add_tool_output(self, tool_name: str, output_type: str, metadata: dict):
        """Add a tool output message.

        Args:
            tool_name: Name of the tool that produced output
            output_type: Type of output (diff, shell, file_listing, etc.)
            metadata: Structured data for rendering
        """
        self._model.add_message(
            Message(
                role=MessageRole.TOOL_OUTPUT,
                content="",  # Content is in metadata
                metadata={
                    "tool_name": tool_name,
                    "output_type": output_type,
                    **metadata
                }
            )
        )
        # Reset assistant message index so text after tool output gets a new bubble
        self._assistant_message_index = None

    def add_diff(self, filepath: str, operation: str, diff_text: str):
        """Add a diff message from the message bus.

        Args:
            filepath: Path to the file that was modified
            operation: Type of operation (create, modify, delete)
            diff_text: The unified diff text
        """
        if not diff_text:
            return

        self._model.add_message(
            Message(
                role=MessageRole.TOOL_OUTPUT,
                content="",
                metadata={
                    "tool_name": "edit_file",
                    "output_type": "file_edit",
                    "filepath": filepath,
                    "operation": operation,
                    "success": True,
                    "changed": True,
                    "diff_text": diff_text,
                }
            )
        )

    # -------------------------------------------------------------------------
    # Error Messages
    # -------------------------------------------------------------------------

    def add_error(self, error: str, error_type: str = "Error"):
        """Add an error message.

        Args:
            error: The error message
            error_type: Categorized error type for display
        """
        self._model.add_message(
            Message(
                role=MessageRole.ERROR,
                content=error,
                metadata={"error_type": error_type}
            )
        )

    # -------------------------------------------------------------------------
    # Response Completion
    # -------------------------------------------------------------------------

    def complete_response(self, response: str):
        """Handle response completion.

        Args:
            response: The final response text (used if no streaming occurred)
        """
        self.flush_and_stop()

        # If no assistant message was created during streaming, create one now
        if self._assistant_message_index is None and response:
            self._model.add_message(
                Message(role=MessageRole.ASSISTANT, content=response)
            )

        # Clear tracked message indices
        self.reset_indices()

    def complete_response_empty(self):
        """Handle response completion when no content was received.

        This should rarely be called - errors should be caught and displayed
        via error_occurred signal before reaching this point.
        """
        self.flush_and_stop()
        self.reset_indices()

    def reset_indices(self):
        """Reset all tracked message indices."""
        self._current_thinking_index = None
        self._current_tool_indices.clear()
        self._assistant_message_index = None

    # -------------------------------------------------------------------------
    # State Queries
    # -------------------------------------------------------------------------

    @property
    def assistant_message_index(self) -> int | None:
        """Get the current assistant message index."""
        return self._assistant_message_index

    @property
    def thinking_index(self) -> int | None:
        """Get the current thinking message index."""
        return self._current_thinking_index

    def get_tool_index(self, tool_name: str) -> int | None:
        """Get the message index for a tool call."""
        return self._current_tool_indices.get(tool_name)

    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    def cleanup(self):
        """Clean up resources."""
        self._token_timer.stop()
        self._token_buffer.clear()
        self.reset_indices()
