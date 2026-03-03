"""Bridge between GUI and agent worker thread.

Provides a thread-safe interface for the GUI to communicate with the agent
running in a separate thread.
"""

import logging
from typing import Optional

from PySide6.QtCore import QObject, Signal, QThread

from .agent_worker import AgentWorker

logger = logging.getLogger(__name__)


class AgentBridge(QObject):
    """Thread-safe bridge to agent execution.

    This class manages the worker thread and provides Qt signals for
    the GUI to react to agent events.
    """

    # Forward signals from worker (for convenience)
    token_received = Signal(str)
    thinking_started = Signal()
    thinking_content = Signal(str)
    thinking_complete = Signal()
    tool_call_started = Signal(str, str)  # tool_name, tool_args
    tool_call_args_delta = Signal(str, str)  # tool_name, args_delta
    tool_call_complete = Signal(str)
    tool_output_received = Signal(str, str, dict)  # tool_name, output_type, metadata
    response_complete = Signal(str)
    error_occurred = Signal(str)
    agent_busy = Signal(bool)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

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
        self._worker.response_complete.connect(self.response_complete)
        self._worker.error_occurred.connect(self.error_occurred)
        self._worker.agent_busy.connect(self.agent_busy)

        # Start the worker thread
        self._worker.start_worker()

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

    def cleanup(self):
        """Clean up resources. Call this before the application exits."""
        self._worker.stop_worker()
