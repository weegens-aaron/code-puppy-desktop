"""Message list widget with rich content rendering."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal

from models.message_model import MessageModel
from models.data_types import Message
from widgets.message_bubble import MessageWidget
from styles import COLORS, SCROLL_AREA_STYLE


class MessageListView(QScrollArea):
    """Scroll area containing message widgets with rich content."""

    copy_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Auto-scroll state
        self._auto_scroll = True
        self._scroll_threshold = 50  # pixels from bottom to re-enable auto-scroll

        # Configure scroll area
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setFrameShape(QFrame.Shape.NoFrame)

        self.setStyleSheet(SCROLL_AREA_STYLE)

        # Container for messages
        self._container = QWidget()
        self._container.setStyleSheet(f"background-color: {COLORS.bg_primary};")
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.addStretch()

        self.setWidget(self._container)

        # Model and widgets
        self._model = MessageModel(self)
        self._widgets: list[MessageWidget] = []

        self._model.message_added.connect(self._on_message_added)
        self._model.message_updated.connect(self._on_message_updated)

        # Track user scrolling to manage auto-scroll
        self.verticalScrollBar().valueChanged.connect(self._on_scroll)

    def _on_message_added(self, row: int):
        """Add widget for new message."""
        message = self._model.get_message(row)
        if message:
            self._add_widget(message)

    def _on_message_updated(self, row: int):
        """Update widget for changed message."""
        if 0 <= row < len(self._widgets):
            message = self._model.get_message(row)
            if message:
                self._widgets[row].update_content(message.content)
                self._scroll_to_bottom()

    def _add_widget(self, message: Message):
        """Add a message widget."""
        widget = MessageWidget(message)
        widget.copy_clicked.connect(self.copy_requested)

        # Remove stretch, add widget, re-add stretch
        if self._layout.count() > 0:
            self._layout.takeAt(self._layout.count() - 1)

        self._layout.addWidget(widget)
        self._layout.addStretch()
        self._widgets.append(widget)

        self._scroll_to_bottom()

    def _on_scroll(self, value: int):
        """Track scroll position to manage auto-scroll."""
        scrollbar = self.verticalScrollBar()
        max_value = scrollbar.maximum()
        # Re-enable auto-scroll if user scrolls near the bottom
        distance_from_bottom = max_value - value
        self._auto_scroll = distance_from_bottom <= self._scroll_threshold

    def _scroll_to_bottom(self):
        """Scroll to bottom if auto-scroll is enabled."""
        if not self._auto_scroll:
            return
        from PySide6.QtCore import QTimer
        QTimer.singleShot(10, lambda: self.verticalScrollBar().setValue(
            self.verticalScrollBar().maximum()
        ))

    def _clear_widgets(self):
        """Remove all message widgets and reset layout."""
        for w in self._widgets:
            self._layout.removeWidget(w)
            w.deleteLater()
        self._widgets.clear()
        # Clear any remaining items (stretches) from layout
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # Add single stretch at end
        self._layout.addStretch()

    @property
    def message_model(self) -> MessageModel:
        return self._model

    def clear(self):
        """Clear all messages."""
        self._model.clear()
        self._clear_widgets()
        self._auto_scroll = True  # Reset auto-scroll on clear
