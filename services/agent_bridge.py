"""Bridge between GUI and agent worker thread.

Provides a thread-safe interface for the GUI to communicate with the agent
running in a separate thread.
"""

import logging
from typing import Optional

from PySide6.QtCore import QObject, Signal, QThread

from services.agent_worker import AgentWorker

logger = logging.getLogger(__name__)


class HookSignalEmitter(QObject):
    """Signal emitter for hook-to-GUI communication.

    This object is registered with the plugin's callback system to receive
    notifications from hooks and emit Qt signals for thread-safe UI updates.
    """

    agent_reloaded = Signal()  # Agent/model was reloaded
    agent_exception_occurred = Signal(str)  # Exception message from agent


class AgentBridge(QObject):
    """Thread-safe bridge to agent execution.

    This class manages the worker thread and provides Qt signals for
    the GUI to react to agent events.
    """

    # Forward signals from worker (main agent)
    token_received = Signal(str)
    thinking_started = Signal()
    thinking_content = Signal(str)
    thinking_complete = Signal()
    tool_call_started = Signal(str, str)  # tool_name, tool_args
    tool_call_args_delta = Signal(str, str)  # tool_name, args_delta
    tool_call_complete = Signal(str)
    tool_output_received = Signal(str, str, dict)  # tool_name, output_type, metadata
    diff_received = Signal(str, str, str)  # filepath, operation, diff_text
    response_complete = Signal(str)
    error_occurred = Signal(str)
    agent_busy = Signal(bool)

    # Ask user question signal
    ask_user_question_requested = Signal(str)  # questions_json

    # Hook-forwarded signals
    agent_reloaded = Signal()  # From agent_reload hook
    agent_exception_occurred = Signal(str)  # From agent_exception hook

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        # Create hook signal emitter and register with plugin callbacks
        self._hook_emitter = HookSignalEmitter()
        self._register_hook_emitter()

        # Create worker and move to thread
        self._worker = AgentWorker()

        # Connect worker signals to our signals (forwarding)
        self._worker.token_received.connect(self.token_received)
        self._worker.thinking_started.connect(self.thinking_started)
        self._worker.thinking_content.connect(self.thinking_content)
        self._worker.thinking_complete.connect(self.thinking_complete)
        self._worker.tool_call_started.connect(self.tool_call_started)
        self._worker.tool_call_args_delta.connect(self.tool_call_args_delta)
        self._worker.tool_call_complete.connect(self.tool_call_complete)
        self._worker.tool_output_received.connect(self.tool_output_received)
        self._worker.diff_received.connect(self.diff_received)
        self._worker.response_complete.connect(self.response_complete)
        self._worker.error_occurred.connect(self.error_occurred)
        self._worker.agent_busy.connect(self.agent_busy)

        # Connect ask_user_question signal
        self._worker.ask_user_question_requested.connect(self.ask_user_question_requested)

        # Connect hook emitter signals to our signals
        self._hook_emitter.agent_reloaded.connect(self.agent_reloaded)
        self._hook_emitter.agent_exception_occurred.connect(self.agent_exception_occurred)

        # Start the worker thread
        self._worker.start_worker()

    def _register_hook_emitter(self):
        """Register the hook signal emitter with the plugin callback system."""
        try:
            from register_callbacks import set_gui_signal_emitter
            set_gui_signal_emitter(self._hook_emitter)
            logger.info("Registered hook signal emitter")
        except ImportError as e:
            logger.warning(f"Could not register hook signal emitter: {e}")

    def prewarm(self):
        """Pre-initialize agent to reduce first-message latency."""
        self._worker.prewarm()

    def send_message(self, prompt: str, attachments: Optional[list] = None):
        """Send a message to the agent (thread-safe).

        Args:
            prompt: The user's message/prompt
            attachments: Optional list of file attachments
        """
        attachments = attachments or []
        self._worker.run_agent(prompt, attachments)

    def cancel(self):
        """Cancel the current operation."""
        self._worker.cancel()

    def is_busy(self) -> bool:
        """Check if the agent is currently processing."""
        return self._worker.is_running

    def clear_history(self):
        """Clear the agent's conversation history."""
        self._worker.clear_agent()

    def set_question_response(self, response: dict):
        """Send the user's response to an ask_user_question request.

        Args:
            response: Dict with structure from QuestionDialog.get_results()
        """
        self._worker.set_question_response(response)

    def cleanup(self):
        """Clean up resources. Call this before the application exits."""
        self._worker.stop_worker()
