"""Tool call display section widget."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QPushButton, QPlainTextEdit,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal


class ToolCallSection(QFrame):
    """Section displaying a tool call with name, status, and arguments.

    Shows a compact header that can be expanded to view tool arguments.
    Indicates whether the tool call is in progress or complete.
    """

    expanded_changed = Signal(bool)  # Emits True when expanded

    def __init__(self, tool_name: str, tool_args: str = "", parent=None):
        super().__init__(parent)
        self._tool_name = tool_name
        self._tool_args = tool_args
        self._is_complete = False
        self._is_expanded = False

        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            ToolCallSection {
                background-color: #1e3a5f;
                border: 1px solid #2d5a8f;
                border-radius: 8px;
            }
        """)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Header row
        header = QHBoxLayout()
        header.setSpacing(8)

        # Status icon
        self._status_icon = QLabel("\u23f3")  # Hourglass
        self._status_icon.setStyleSheet("color: #4fc3f7; font-size: 14px;")
        header.addWidget(self._status_icon)

        # Tool name
        self._name_label = QLabel(f"Tool: {self._tool_name}")
        self._name_label.setStyleSheet("color: #4fc3f7; font-weight: bold; font-size: 13px;")
        header.addWidget(self._name_label)

        header.addStretch()

        # Expand button (starts expanded)
        self._expand_btn = QPushButton("\u25bc")  # Down arrow (expanded)
        self._expand_btn.setFixedSize(24, 24)
        self._expand_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #4fc3f7;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(79, 195, 247, 0.2);
                border-radius: 4px;
            }
        """)
        self._expand_btn.clicked.connect(self._toggle_expand)
        header.addWidget(self._expand_btn)

        layout.addLayout(header)

        # Arguments area (visible by default)
        self._args_text = QPlainTextEdit()
        self._args_text.setReadOnly(True)
        self._args_text.setPlainText(self._tool_args or "(no arguments)")
        self._args_text.setStyleSheet("""
            QPlainTextEdit {
                background-color: rgba(0, 0, 0, 0.2);
                border: none;
                color: #b0bec5;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        self._args_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._args_text.setMinimumHeight(40)
        # Auto-resize to fit content
        self._args_text.document().documentLayout().documentSizeChanged.connect(
            self._adjust_height
        )
        self._is_expanded = True  # Start expanded
        self._args_text.setVisible(True)
        layout.addWidget(self._args_text)

        # Initial height adjustment
        self._adjust_height()

    def _toggle_expand(self):
        """Toggle expanded state."""
        self._is_expanded = not self._is_expanded
        self._args_text.setVisible(self._is_expanded)
        self._expand_btn.setText("\u25bc" if self._is_expanded else "\u25b6")
        self.expanded_changed.emit(self._is_expanded)

    def _adjust_height(self):
        """Adjust text edit height to fit content."""
        doc = self._args_text.document()
        # Set text width to viewport width for proper height calculation
        doc.setTextWidth(self._args_text.viewport().width() or 400)
        # Calculate height based on document size plus margins
        height = int(doc.size().height()) + 20
        self._args_text.setMinimumHeight(max(40, min(height, 300)))
        self._args_text.setMaximumHeight(max(40, min(height, 300)))

    def set_tool_name(self, name: str):
        """Update the tool name."""
        self._tool_name = name
        self._name_label.setText(f"Tool: {name}")

    def set_tool_args(self, args: str):
        """Update the tool arguments."""
        self._tool_args = args
        self._args_text.setPlainText(args or "(no arguments)")
        self._adjust_height()

    def append_args(self, args_delta: str):
        """Append to tool arguments (for streaming)."""
        self._tool_args = (self._tool_args or "") + args_delta
        # Use insertPlainText for efficient streaming
        cursor = self._args_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(args_delta)
        self._args_text.setTextCursor(cursor)
        self._adjust_height()

    def set_complete(self, complete: bool):
        """Mark the tool call as complete."""
        self._is_complete = complete
        if complete:
            self._status_icon.setText("\u2713")  # Checkmark
            self._status_icon.setStyleSheet("color: #4caf50; font-size: 14px;")
        else:
            self._status_icon.setText("\u23f3")  # Hourglass
            self._status_icon.setStyleSheet("color: #4fc3f7; font-size: 14px;")

    def is_complete(self) -> bool:
        """Check if the tool call is complete."""
        return self._is_complete

    @property
    def tool_name(self) -> str:
        """Get the tool name."""
        return self._tool_name
