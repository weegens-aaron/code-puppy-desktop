"""Bridge between Code Puppy's MessageBus and the Qt GUI.

This service polls the MessageBus for messages and emits Qt signals
for thread-safe UI updates. This ensures ALL output from the CLI
(emit_info, emit_error, shell output, etc.) is captured in the desktop UI.
"""

import logging
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal, QTimer

logger = logging.getLogger(__name__)


class MessageBusBridge(QObject):
    """Polls MessageBus and emits Qt signals for each message type.

    This bridges the gap between Code Puppy's messaging system and Qt's
    signal/slot mechanism, ensuring thread-safe UI updates.
    """

    # Text messages (emit_info, emit_warning, emit_error, emit_success)
    text_message = Signal(str, str)  # level, text

    # File operations
    file_listing = Signal(dict)  # FileListingMessage data
    file_content = Signal(dict)  # FileContentMessage data
    grep_result = Signal(dict)  # GrepResultMessage data
    diff_message = Signal(dict)  # DiffMessage data

    # Shell output
    shell_start = Signal(dict)  # ShellStartMessage data
    shell_line = Signal(str, str)  # line, stream
    shell_output = Signal(dict)  # ShellOutputMessage data

    # Agent messages
    agent_reasoning = Signal(str, list)  # reasoning, next_steps
    agent_response = Signal(str)  # response text

    # Sub-agent messages
    subagent_invocation = Signal(dict)  # SubAgentInvocationMessage data
    subagent_response = Signal(dict)  # SubAgentResponseMessage data
    subagent_status = Signal(dict)  # SubAgentStatusMessage data

    # User interaction requests
    input_request = Signal(dict)  # UserInputRequest data
    confirmation_request = Signal(dict)  # ConfirmationRequest data
    selection_request = Signal(dict)  # SelectionRequest data

    # Misc
    divider = Signal()  # DividerMessage
    status_panel = Signal(dict)  # StatusPanelMessage data
    skill_list = Signal(dict)  # SkillListMessage data
    skill_activate = Signal(dict)  # SkillActivateMessage data
    spinner_control = Signal(str, str)  # action, message

    # Generic fallback for unhandled message types
    generic_message = Signal(str, dict)  # message_type, data

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setInterval(16)  # ~60fps polling
        self._timer.timeout.connect(self._poll_messages)
        self._active = False
        self._message_bus = None

    def start(self):
        """Start polling the MessageBus."""
        if self._active:
            return

        try:
            from code_puppy.messaging import get_message_bus
            self._message_bus = get_message_bus()

            # Mark renderer as active so messages go to queue, not buffer
            self._message_bus.mark_renderer_active()

            # Process any buffered startup messages
            buffered = self._message_bus.get_buffered_messages()
            for msg in buffered:
                self._handle_message(msg)
            self._message_bus.clear_buffer()

            self._active = True
            self._timer.start()
            logger.info("MessageBusBridge started")
        except Exception as e:
            logger.error(f"Failed to start MessageBusBridge: {e}")

    def stop(self):
        """Stop polling the MessageBus."""
        if not self._active:
            return

        self._timer.stop()
        self._active = False

        if self._message_bus:
            self._message_bus.mark_renderer_inactive()

        logger.info("MessageBusBridge stopped")

    def _poll_messages(self):
        """Poll for messages and emit signals."""
        if not self._message_bus:
            return

        # Process up to 50 messages per tick to avoid blocking
        for _ in range(50):
            msg = self._message_bus.get_message_nowait()
            if msg is None:
                break
            self._handle_message(msg)

    def _handle_message(self, msg: Any):
        """Route message to appropriate signal."""
        try:
            from code_puppy.messaging import (
                TextMessage,
                FileListingMessage,
                FileContentMessage,
                GrepResultMessage,
                DiffMessage,
                ShellStartMessage,
                ShellLineMessage,
                ShellOutputMessage,
                AgentReasoningMessage,
                AgentResponseMessage,
                SubAgentInvocationMessage,
                SubAgentResponseMessage,
                SubAgentStatusMessage,
                UserInputRequest,
                ConfirmationRequest,
                SelectionRequest,
                DividerMessage,
                StatusPanelMessage,
                SkillListMessage,
                SkillActivateMessage,
                SpinnerControl,
            )

            if isinstance(msg, TextMessage):
                self.text_message.emit(msg.level.value, msg.text)

            elif isinstance(msg, FileListingMessage):
                self.file_listing.emit(self._msg_to_dict(msg))

            elif isinstance(msg, FileContentMessage):
                self.file_content.emit(self._msg_to_dict(msg))

            elif isinstance(msg, GrepResultMessage):
                self.grep_result.emit(self._msg_to_dict(msg))

            elif isinstance(msg, DiffMessage):
                self.diff_message.emit(self._msg_to_dict(msg))

            elif isinstance(msg, ShellStartMessage):
                self.shell_start.emit(self._msg_to_dict(msg))

            elif isinstance(msg, ShellLineMessage):
                self.shell_line.emit(msg.line, msg.stream)

            elif isinstance(msg, ShellOutputMessage):
                self.shell_output.emit(self._msg_to_dict(msg))

            elif isinstance(msg, AgentReasoningMessage):
                next_steps = msg.next_steps or []
                self.agent_reasoning.emit(msg.reasoning, next_steps)

            elif isinstance(msg, AgentResponseMessage):
                self.agent_response.emit(msg.response)

            elif isinstance(msg, SubAgentInvocationMessage):
                self.subagent_invocation.emit(self._msg_to_dict(msg))

            elif isinstance(msg, SubAgentResponseMessage):
                self.subagent_response.emit(self._msg_to_dict(msg))

            elif isinstance(msg, SubAgentStatusMessage):
                self.subagent_status.emit(self._msg_to_dict(msg))

            elif isinstance(msg, UserInputRequest):
                self.input_request.emit(self._msg_to_dict(msg))

            elif isinstance(msg, ConfirmationRequest):
                self.confirmation_request.emit(self._msg_to_dict(msg))

            elif isinstance(msg, SelectionRequest):
                self.selection_request.emit(self._msg_to_dict(msg))

            elif isinstance(msg, DividerMessage):
                self.divider.emit()

            elif isinstance(msg, StatusPanelMessage):
                self.status_panel.emit(self._msg_to_dict(msg))

            elif isinstance(msg, SkillListMessage):
                self.skill_list.emit(self._msg_to_dict(msg))

            elif isinstance(msg, SkillActivateMessage):
                self.skill_activate.emit(self._msg_to_dict(msg))

            elif isinstance(msg, SpinnerControl):
                self.spinner_control.emit(msg.action, msg.message or "")

            else:
                # Fallback for unknown message types
                msg_type = type(msg).__name__
                self.generic_message.emit(msg_type, self._msg_to_dict(msg))

        except Exception as e:
            logger.error(f"Error handling message {type(msg).__name__}: {e}")

    def _msg_to_dict(self, msg: Any) -> dict:
        """Convert a Pydantic message to a dict for Qt signal."""
        try:
            if hasattr(msg, 'model_dump'):
                return msg.model_dump()
            elif hasattr(msg, 'dict'):
                return msg.dict()
            else:
                return {"raw": str(msg)}
        except Exception:
            return {"raw": str(msg)}


# Global singleton
_bridge: Optional[MessageBusBridge] = None


def get_message_bus_bridge() -> MessageBusBridge:
    """Get or create the global MessageBusBridge singleton."""
    global _bridge
    if _bridge is None:
        _bridge = MessageBusBridge()
    return _bridge
