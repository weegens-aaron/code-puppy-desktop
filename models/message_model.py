"""Qt Model for chat messages."""

from typing import Optional

from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, Signal

from models.data_types import Message


class MessageModel(QAbstractListModel):
    """Model holding chat messages for QListView."""

    # Custom role for getting full Message object
    MessageDataRole = Qt.ItemDataRole.UserRole + 1

    message_added = Signal(int)  # Emits row index
    message_updated = Signal(int)  # Emits row index when content changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self._messages: list[Message] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._messages)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self._messages):
            return None

        message = self._messages[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            return message.get_display_text()
        elif role == self.MessageDataRole:
            return message

        return None

    def add_message(self, message: Message) -> int:
        """Add a new message. Returns the row index."""
        row = len(self._messages)
        self.beginInsertRows(QModelIndex(), row, row)
        self._messages.append(message)
        self.endInsertRows()
        self.message_added.emit(row)
        return row

    def update_last_message(self, content: str):
        """Update the last message's content (for streaming)."""
        if not self._messages:
            return

        self._messages[-1].content = content
        index = self.index(len(self._messages) - 1)
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
        self.message_updated.emit(len(self._messages) - 1)

    def append_to_last_message(self, text: str):
        """Append text to the last message (efficient streaming)."""
        if not self._messages:
            return

        self._messages[-1].append_content(text)
        index = self.index(len(self._messages) - 1)
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
        self.message_updated.emit(len(self._messages) - 1)

    def append_to_message(self, row: int, text: str):
        """Append text to a specific message by row index."""
        if 0 <= row < len(self._messages):
            self._messages[row].append_content(text)
            index = self.index(row)
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
            self.message_updated.emit(row)

    def update_message_content(self, row: int, content: str):
        """Update a specific message's content."""
        if 0 <= row < len(self._messages):
            self._messages[row].content = content
            index = self.index(row)
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
            self.message_updated.emit(row)

    def get_message(self, row: int) -> Optional[Message]:
        """Get message at row."""
        if 0 <= row < len(self._messages):
            return self._messages[row]
        return None

    def get_last_message(self) -> Optional[Message]:
        """Get the last message."""
        if self._messages:
            return self._messages[-1]
        return None

    def clear(self):
        """Clear all messages."""
        self.beginResetModel()
        self._messages.clear()
        self.endResetModel()

    def message_count(self) -> int:
        """Get total message count."""
        return len(self._messages)
