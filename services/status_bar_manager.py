"""Status bar management with activity indicator.

Separates status bar concerns from the main application (SRP/SoC).
"""

import time
from typing import Optional

from PySide6.QtWidgets import QStatusBar, QLabel, QFrame
from PySide6.QtCore import QTimer, QObject, Signal

from styles import (
    COLORS, get_status_label_style, get_status_activity_style,
    get_status_separator_style, get_theme_manager,
)
from code_puppy.agents import get_current_agent
from code_puppy.command_line.model_picker_completion import get_active_model
from code_puppy.config import get_puppy_name


class StatusBarManager(QObject):
    """Manages the application status bar.

    Handles:
    - Activity indicator (spinner during tool calls)
    - Status messages
    - Model/Agent/Context info displays
    - Theme updates
    """

    def __init__(self, status_bar: QStatusBar, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._status_bar = status_bar

        # Activity indicator state
        self._activity_timer = QTimer(self)
        self._activity_timer.setInterval(100)
        self._activity_timer.timeout.connect(self._update_activity_indicator)
        self._activity_frame = 0
        self._activity_start_time: float = 0
        self._current_tool_name: str = ""
        self._activity_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

        # Create widgets
        self._setup_widgets()

        # Theme listener
        self._theme_manager = get_theme_manager()
        self._theme_manager.add_listener(self._on_theme_changed)

    def _setup_widgets(self):
        """Set up status bar widgets."""
        # Activity indicator (left side, shows during operations)
        self._activity_label = QLabel()
        self._activity_label.setStyleSheet(get_status_activity_style())
        self._activity_label.setVisible(False)
        self._status_bar.addWidget(self._activity_label)

        # Create permanent widgets for model, agent, and context info
        self._context_label = QLabel()
        self._context_label.setStyleSheet(get_status_label_style(COLORS.text_secondary))

        # Separator 1
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        separator1.setStyleSheet(get_status_separator_style())

        self._agent_label = QLabel()
        self._agent_label.setStyleSheet(get_status_label_style(COLORS.accent_success))

        # Separator 2
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setStyleSheet(get_status_separator_style())

        self._model_label = QLabel()
        self._model_label.setStyleSheet(get_status_label_style(COLORS.accent_info))

        # Add permanent widgets (right side): context | agent | model
        self._status_bar.addPermanentWidget(self._context_label)
        self._status_bar.addPermanentWidget(separator1)
        self._status_bar.addPermanentWidget(self._agent_label)
        self._status_bar.addPermanentWidget(separator2)
        self._status_bar.addPermanentWidget(self._model_label)

        # Initialize displays
        self.update_info()
        self._status_bar.showMessage("Ready")

    def _on_theme_changed(self, theme):
        """Update styles when theme changes."""
        colors = self._theme_manager.current
        self._activity_label.setStyleSheet(get_status_activity_style())
        self._model_label.setStyleSheet(get_status_label_style(colors.accent_info))
        self._agent_label.setStyleSheet(get_status_label_style(colors.accent_success))
        self._context_label.setStyleSheet(get_status_label_style(colors.text_secondary))

    # -------------------------------------------------------------------------
    # Activity Indicator
    # -------------------------------------------------------------------------

    def start_activity(self, tool_name: str):
        """Start the activity indicator for a tool operation."""
        self._current_tool_name = tool_name
        self._activity_start_time = time.time()
        self._activity_frame = 0
        # Clear status message to avoid overlap
        self._status_bar.clearMessage()
        self._activity_label.setVisible(True)
        self._update_activity_indicator()
        self._activity_timer.start()

    def stop_activity(self):
        """Stop the activity indicator."""
        self._activity_timer.stop()
        self._activity_label.setVisible(False)
        self._current_tool_name = ""

    def _update_activity_indicator(self):
        """Update the activity indicator display."""
        if not self._current_tool_name:
            return

        # Cycle through animation frames
        frame = self._activity_frames[self._activity_frame % len(self._activity_frames)]
        self._activity_frame += 1

        # Calculate elapsed time
        elapsed = time.time() - self._activity_start_time
        elapsed_str = f"{elapsed:.1f}s"

        # Update label with spinner, tool name, and elapsed time
        self._activity_label.setText(f"{frame} Calling {self._current_tool_name}... {elapsed_str}")

    @property
    def current_tool(self) -> str:
        """Get the current tool being tracked."""
        return self._current_tool_name

    @property
    def activity_timer(self) -> QTimer:
        """Get the activity timer for cleanup."""
        return self._activity_timer

    # -------------------------------------------------------------------------
    # Status Messages
    # -------------------------------------------------------------------------

    def show_message(self, message: str):
        """Show a status message."""
        self._status_bar.showMessage(message)

    def clear_message(self):
        """Clear the status message."""
        self._status_bar.clearMessage()

    # -------------------------------------------------------------------------
    # Info Displays
    # -------------------------------------------------------------------------

    def update_info(self):
        """Update all status bar info displays."""
        self._update_model_display()
        self._update_agent_display()
        self._update_context_display()

    def _update_model_display(self):
        """Update the model display in status bar."""
        agent = get_current_agent()

        # Get global model
        global_model = get_active_model() or "(default)"

        # Check if agent has a pinned model
        agent_model = None
        if agent and hasattr(agent, "get_model_name"):
            agent_model = agent.get_model_name()

        # Determine display
        if agent_model and agent_model != global_model:
            model_display = f"{global_model} → {agent_model}"
        else:
            model_display = agent_model or global_model

        self._model_label.setText(f"🤖 {model_display}")

    def _update_agent_display(self):
        """Update the agent display in status bar."""
        agent = get_current_agent()
        if agent:
            self._agent_label.setText(f"🐕 {agent.display_name}")
        else:
            self._agent_label.setText(f"🐕 {get_puppy_name()}")

    def _update_context_display(self):
        """Update the context info display in status bar."""
        agent = get_current_agent()
        if agent:
            messages = agent.get_message_history()
            msg_count = len(messages)

            # Estimate tokens used (messages + system prompt overhead)
            message_tokens = sum(agent.estimate_tokens_for_message(m) for m in messages)
            overhead_tokens = agent.estimate_context_overhead_tokens()
            total_tokens = message_tokens + overhead_tokens

            # Get context window size
            context_length = agent.get_model_context_length()

            # Calculate percentage
            usage_percent = (total_tokens / context_length * 100) if context_length > 0 else 0

            self._context_label.setText(
                f"💬 {msg_count} msgs | {total_tokens:,}/{context_length:,} ({usage_percent:.0f}%)"
            )
        else:
            self._context_label.setText("💬 0 msgs | 0/0 (0%)")

    def update_context_only(self):
        """Update just the context display (for efficiency after session changes)."""
        self._update_context_display()

    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    def cleanup(self):
        """Clean up resources."""
        self._activity_timer.stop()
        try:
            self._theme_manager.remove_listener(self._on_theme_changed)
        except Exception:
            pass
