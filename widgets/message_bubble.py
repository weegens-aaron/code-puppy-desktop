"""Message widget with markdown rendering."""

import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextBrowser, QFrame, QPushButton, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap

from desktop.models.data_types import Message, MessageRole, ToolOutputType
from desktop.styles import (
    COLORS, get_role_style, CONTENT_BROWSER_STYLE, COPY_BUTTON_STYLE
)
from desktop.utils.content_renderer import ContentRenderer
from code_puppy.config import get_owner_name, get_puppy_name


# Role display name providers - allows dependency injection
def _default_user_name() -> str:
    return get_owner_name()


def _default_assistant_name() -> str:
    return get_puppy_name()


class MessageWidget(QFrame):
    """A full-width message widget with markdown rendering.

    Displays messages with a colored header bar, role indicator,
    and properly rendered markdown content.
    """

    copy_clicked = Signal(str)

    # Class-level name providers (can be overridden for testing)
    get_user_name = staticmethod(_default_user_name)
    get_assistant_name = staticmethod(_default_assistant_name)

    def __init__(self, message: Message, parent=None):
        super().__init__(parent)
        self._message = message
        self._collapsed = False
        self._collapsible = message.role in (
            MessageRole.THINKING, MessageRole.TOOL_CALL, MessageRole.TOOL_OUTPUT
        )

        self.setFrameShape(QFrame.Shape.NoFrame)
        self._setup_ui()
        self._update_content()

    def _get_role_config(self) -> tuple[str, str, str]:
        """Get role-specific configuration.

        Returns:
            Tuple of (role_text, role_color, background_color)
        """
        role = self._message.role
        style = get_role_style(role.value)

        if role == MessageRole.USER:
            return self.get_user_name(), style.text_color, style.background_color
        elif role == MessageRole.THINKING:
            return "Thinking", style.text_color, style.background_color
        elif role == MessageRole.TOOL_CALL:
            tool_name = self._message.metadata.get("tool_name", "Tool")
            return tool_name, style.text_color, style.background_color
        elif role == MessageRole.TOOL_OUTPUT:
            # Get tool name from metadata for display
            tool_name = self._message.metadata.get("tool_name", "Tool Output")
            return tool_name, style.text_color, style.background_color
        elif role == MessageRole.ERROR:
            error_type = self._message.metadata.get("error_type", "Error")
            return error_type, style.text_color, style.background_color
        else:
            return self.get_assistant_name(), style.text_color, style.background_color

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        role_text, role_color, bg_color = self._get_role_config()

        # Header bar with role and copy button
        self._header = QFrame()
        self._header.setFixedHeight(32)
        self._header.setStyleSheet(f"background-color: {bg_color};")

        header_layout = QHBoxLayout(self._header)
        header_layout.setContentsMargins(16, 4, 16, 4)
        header_layout.setSpacing(8)

        # Collapse indicator for collapsible messages
        if self._collapsible:
            self._collapse_indicator = QLabel("▼")
            self._collapse_indicator.setStyleSheet(f"color: {role_color}; font-size: 10px;")
            header_layout.addWidget(self._collapse_indicator)
            self._header.setCursor(Qt.CursorShape.PointingHandCursor)
            self._header.mousePressEvent = self._on_header_click

        # Role label
        role_label = QLabel(role_text)
        role_label.setStyleSheet(f"color: {role_color}; font-weight: bold; font-size: 13px;")
        header_layout.addWidget(role_label)

        header_layout.addStretch()

        # Copy button (icon)
        copy_btn = QPushButton("📋")
        copy_btn.setFixedSize(24, 22)
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setToolTip("Copy to clipboard")
        copy_btn.setStyleSheet(COPY_BUTTON_STYLE)
        copy_btn.clicked.connect(self._on_copy)
        self._copy_btn = copy_btn
        header_layout.addWidget(copy_btn)

        layout.addWidget(self._header)

        # Content area
        self._content = QTextBrowser()
        self._content.setOpenExternalLinks(True)
        self._content.setFrameShape(QFrame.Shape.NoFrame)
        self._content.setStyleSheet(CONTENT_BROWSER_STYLE)
        self._content.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._content.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # Auto-resize on content change
        self._content.document().documentLayout().documentSizeChanged.connect(
            self._adjust_height
        )

        layout.addWidget(self._content)

        # Attachments area (for images)
        self._attachments_container = QWidget()
        self._attachments_container.setStyleSheet(f"background-color: {COLORS.bg_content};")
        self._attachments_layout = QVBoxLayout(self._attachments_container)
        self._attachments_layout.setContentsMargins(16, 0, 16, 12)
        self._attachments_layout.setSpacing(8)
        self._attachments_container.setVisible(False)
        layout.addWidget(self._attachments_container)

        # Bottom divider
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background-color: {COLORS.border_subtle};")
        layout.addWidget(divider)

    def _update_content(self):
        """Update the displayed content with proper rendering."""
        content = self._message.get_display_text()
        if not content:
            content = "..."

        # Use appropriate renderer based on role
        role = self._message.role
        metadata = self._message.metadata

        if role == MessageRole.USER:
            html = ContentRenderer.render_plain_text(content)
        elif role == MessageRole.THINKING:
            html = ContentRenderer.render_thinking(content)
        elif role == MessageRole.TOOL_CALL:
            tool_name = metadata.get("tool_name", "tool")
            html = ContentRenderer.render_tool_call(tool_name, content)
        elif role == MessageRole.TOOL_OUTPUT:
            html = self._render_tool_output(content, metadata)
        elif role == MessageRole.ERROR:
            error_type = metadata.get("error_type", "Error")
            html = ContentRenderer.render_error(content, error_type)
        else:
            html = ContentRenderer.render_markdown(content)

        self._content.setHtml(html)
        self._adjust_height()
        self._render_attachments()

    def _render_tool_output(self, content: str, metadata: dict) -> str:
        """Render tool output based on output_type in metadata.

        Args:
            content: The raw content
            metadata: Message metadata containing output_type and other data

        Returns:
            HTML string with styled content
        """
        output_type = metadata.get("output_type", ToolOutputType.JSON.value)

        if output_type == ToolOutputType.DIFF.value:
            return ContentRenderer.render_diff(
                diff_text=metadata.get("diff_text", content),
                operation=metadata.get("operation", "modify"),
                filepath=metadata.get("filepath", "")
            )
        elif output_type == ToolOutputType.SHELL.value:
            return ContentRenderer.render_shell_command(
                command=metadata.get("command", ""),
                output=metadata.get("output", content),
                exit_code=metadata.get("exit_code", 0),
                cwd=metadata.get("cwd", ""),
                duration=metadata.get("duration", 0.0),
                background=metadata.get("background", False)
            )
        elif output_type == ToolOutputType.FILE_LISTING.value:
            return ContentRenderer.render_file_listing(
                directory=metadata.get("directory", "."),
                entries=metadata.get("entries", []),
                recursive=metadata.get("recursive", False),
                total_size=metadata.get("total_size", 0),
                dir_count=metadata.get("dir_count", 0),
                file_count=metadata.get("file_count", 0)
            )
        elif output_type == ToolOutputType.GREP.value:
            return ContentRenderer.render_grep_results(
                search_term=metadata.get("search_term", ""),
                directory=metadata.get("directory", "."),
                matches=metadata.get("matches", []),
                total_matches=metadata.get("total_matches", 0)
            )
        elif output_type == ToolOutputType.FILE_HEADER.value:
            return ContentRenderer.render_file_header(
                path=metadata.get("filepath", ""),
                line_info=metadata.get("line_info", "")
            )
        elif output_type == ToolOutputType.SKILL_LIST.value:
            return ContentRenderer.render_skill_list(
                skills=metadata.get("skills", []),
                total_count=metadata.get("total_count", 0),
                query=metadata.get("query", ""),
                error=metadata.get("error")
            )
        elif output_type == ToolOutputType.SKILL_ACTIVATE.value:
            return ContentRenderer.render_skill_activate(
                skill_name=metadata.get("skill_name", ""),
                content=metadata.get("content", ""),
                resources=metadata.get("resources", []),
                error=metadata.get("error")
            )
        else:
            # Default to JSON rendering
            return ContentRenderer.render_json(content)

    def _render_attachments(self):
        """Render image attachments if present."""
        # Clear existing attachments
        while self._attachments_layout.count():
            item = self._attachments_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._message.attachments:
            self._attachments_container.setVisible(False)
            return

        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
        has_attachments = False

        for filepath in self._message.attachments:
            ext = os.path.splitext(filepath)[1].lower()
            if ext in image_extensions and os.path.exists(filepath):
                has_attachments = True
                self._add_image_attachment(filepath)
            else:
                has_attachments = True
                self._add_file_attachment(filepath)

        self._attachments_container.setVisible(has_attachments)

    def _add_image_attachment(self, filepath: str):
        """Add an image attachment widget."""
        pixmap = QPixmap(filepath)
        if not pixmap.isNull():
            # Scale to max width while maintaining aspect ratio
            max_width = 400
            if pixmap.width() > max_width:
                pixmap = pixmap.scaledToWidth(
                    max_width, Qt.TransformationMode.SmoothTransformation
                )

            img_label = QLabel()
            img_label.setPixmap(pixmap)
            img_label.setStyleSheet(f"""
                QLabel {{
                    border: 1px solid {COLORS.border_subtle};
                    border-radius: 4px;
                    padding: 2px;
                }}
            """)
            self._attachments_layout.addWidget(img_label)

    def _add_file_attachment(self, filepath: str):
        """Add a non-image file attachment widget."""
        file_label = QLabel(f"📎 {os.path.basename(filepath)}")
        file_label.setStyleSheet(f"color: {COLORS.text_secondary}; font-size: 12px;")
        self._attachments_layout.addWidget(file_label)

    def _adjust_height(self, size=None):
        """Adjust content height to fit text."""
        doc = self._content.document()
        doc.setTextWidth(self._content.viewport().width())
        height = int(doc.size().height()) + 24  # Add padding
        self._content.setFixedHeight(max(40, height))

    def update_content(self, content: str):
        """Update message content (for streaming)."""
        self._message.content = content
        self._update_content()

    def _on_copy(self):
        """Copy message content to clipboard."""
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(self._message.get_display_text())
        self.copy_clicked.emit(self._message.get_display_text())

        self._copy_btn.setText("✓")
        QTimer.singleShot(1500, lambda: self._copy_btn.setText("📋"))

    def _on_header_click(self, event):
        """Toggle collapse state for collapsible messages."""
        self._collapsed = not self._collapsed
        self._content.setVisible(not self._collapsed)
        self._collapse_indicator.setText("▶" if self._collapsed else "▼")

    @property
    def message(self) -> Message:
        return self._message

    def resizeEvent(self, event):
        """Handle resize to reflow content."""
        super().resizeEvent(event)
        self._adjust_height()


# Alias for backwards compatibility
MessageBubble = MessageWidget
