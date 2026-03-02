"""Collapsible thinking/reasoning section widget."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QPlainTextEdit, QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal


class ThinkingSection(QFrame):
    """Collapsible section for displaying AI thinking/reasoning.

    Shows a header with expand/collapse toggle and displays
    the thinking content in a dimmed, monospace font.
    """

    collapsed_changed = Signal(bool)  # Emits True when collapsed

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_collapsed = False
        self._content = ""
        self._is_complete = False

        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            ThinkingSection {
                background-color: #3d3522;
                border: 1px solid #5c4d2b;
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

        # Icon
        self._icon = QLabel("\u26a1")  # Lightning bolt
        self._icon.setStyleSheet("color: #ffc107; font-size: 14px;")
        header.addWidget(self._icon)

        # Title
        self._title = QLabel("Thinking...")
        self._title.setStyleSheet("color: #ffc107; font-weight: bold; font-size: 13px;")
        header.addWidget(self._title)

        header.addStretch()

        # Toggle button
        self._toggle_btn = QPushButton("\u25bc")  # Down arrow
        self._toggle_btn.setFixedSize(24, 24)
        self._toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #ffc107;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 193, 7, 0.2);
                border-radius: 4px;
            }
        """)
        self._toggle_btn.clicked.connect(self._toggle)
        header.addWidget(self._toggle_btn)

        layout.addLayout(header)

        # Content area
        self._text_edit = QPlainTextEdit()
        self._text_edit.setReadOnly(True)
        self._text_edit.setStyleSheet("""
            QPlainTextEdit {
                background-color: transparent;
                border: none;
                color: #c4b99a;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        self._text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._text_edit.setMinimumHeight(40)
        # Auto-resize to fit content
        self._text_edit.document().documentLayout().documentSizeChanged.connect(
            self._adjust_height
        )
        layout.addWidget(self._text_edit)

        # Initial height adjustment
        self._adjust_height()

    def _toggle(self):
        """Toggle collapsed state."""
        self._is_collapsed = not self._is_collapsed
        self._text_edit.setVisible(not self._is_collapsed)
        self._toggle_btn.setText("\u25b6" if self._is_collapsed else "\u25bc")
        self.collapsed_changed.emit(self._is_collapsed)

    def _adjust_height(self):
        """Adjust text edit height to fit content."""
        doc = self._text_edit.document()
        # Set text width to viewport width for proper height calculation
        doc.setTextWidth(self._text_edit.viewport().width() or 400)
        # Calculate height based on document size plus margins
        height = int(doc.size().height()) + 20
        self._text_edit.setMinimumHeight(max(40, min(height, 400)))
        self._text_edit.setMaximumHeight(max(40, min(height, 400)))

    def set_content(self, content: str):
        """Set the thinking content."""
        self._content = content
        self._text_edit.setPlainText(content)

    def append_content(self, text: str):
        """Append text to the thinking content (for streaming)."""
        self._content += text
        # Use insertPlainText for efficient streaming
        cursor = self._text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text)
        self._text_edit.setTextCursor(cursor)
        # Adjust height to fit new content
        self._adjust_height()
        # Auto-scroll to bottom
        scrollbar = self._text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def get_content(self) -> str:
        """Get the current content."""
        return self._content

    def set_complete(self, complete: bool):
        """Mark thinking as complete."""
        self._is_complete = complete
        self._title.setText("Thinking" if complete else "Thinking...")

    def is_complete(self) -> bool:
        """Check if thinking is complete."""
        return self._is_complete

    def clear(self):
        """Clear the content."""
        self._content = ""
        self._text_edit.clear()
        self._is_complete = False
        self._title.setText("Thinking...")
