"""Custom delegate for rendering message bubbles."""

from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem
from PySide6.QtCore import Qt, QSize, QRect, QModelIndex
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QFontMetrics

from ..models.message_model import MessageModel
from ..models.data_types import MessageRole


class MessageDelegate(QStyledItemDelegate):
    """Delegate for rendering chat message bubbles."""

    PADDING = 12
    BUBBLE_RADIUS = 12
    MAX_WIDTH = 700
    VERTICAL_SPACING = 8

    # Colors - Dark theme
    USER_BG = QColor("#1a73e8")
    ASSISTANT_BG = QColor("#3c4043")
    SYSTEM_BG = QColor("#5f6368")
    TEXT_COLOR = QColor("#ffffff")
    USER_TEXT_COLOR = QColor("#ffffff")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._font = QFont("Segoe UI", 11)
        self._font_metrics = QFontMetrics(self._font)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        message = index.data(MessageModel.MessageDataRole)
        if not message:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(self._font)

        # Calculate bubble dimensions
        text = message.get_display_text()
        if not text:
            text = "..."  # Placeholder for empty streaming message

        available_width = min(self.MAX_WIDTH, option.rect.width() - 100)
        text_rect = self._font_metrics.boundingRect(
            QRect(0, 0, available_width - 2 * self.PADDING, 10000),
            Qt.TextFlag.TextWordWrap,
            text
        )

        bubble_width = text_rect.width() + 2 * self.PADDING
        bubble_height = text_rect.height() + 2 * self.PADDING

        # Position bubble (right-align user, left-align assistant)
        if message.role == MessageRole.USER:
            bubble_x = option.rect.right() - bubble_width - 20
            bg_color = self.USER_BG
            text_color = self.USER_TEXT_COLOR
        else:
            bubble_x = option.rect.left() + 20
            bg_color = self.ASSISTANT_BG if message.role == MessageRole.ASSISTANT else self.SYSTEM_BG
            text_color = self.TEXT_COLOR

        bubble_y = option.rect.top() + self.VERTICAL_SPACING // 2
        bubble_rect = QRect(int(bubble_x), int(bubble_y), int(bubble_width), int(bubble_height))

        # Draw bubble
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bubble_rect, self.BUBBLE_RADIUS, self.BUBBLE_RADIUS)

        # Draw text
        painter.setPen(QPen(text_color))
        inner_rect = bubble_rect.adjusted(self.PADDING, self.PADDING, -self.PADDING, -self.PADDING)
        painter.drawText(inner_rect, Qt.TextFlag.TextWordWrap, text)

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        message = index.data(MessageModel.MessageDataRole)
        if not message:
            return QSize(0, 0)

        text = message.get_display_text()
        if not text:
            text = "..."

        # Use a reasonable default width if option.rect is not set
        rect_width = option.rect.width() if option.rect.width() > 0 else 800
        available_width = min(self.MAX_WIDTH, rect_width - 100)

        text_rect = self._font_metrics.boundingRect(
            QRect(0, 0, available_width - 2 * self.PADDING, 10000),
            Qt.TextFlag.TextWordWrap,
            text
        )

        height = text_rect.height() + 2 * self.PADDING + self.VERTICAL_SPACING
        return QSize(rect_width, max(height, 50))
