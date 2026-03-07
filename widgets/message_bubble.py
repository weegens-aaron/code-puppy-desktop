"""Modern message widget with aligned chat bubbles."""

import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextBrowser, QFrame, QPushButton, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QTimer

from models.data_types import Message, MessageRole, ToolOutputType
from styles import (
    COLORS, get_role_style,
    get_message_bubble_style, get_bubble_content_style,
)
from utils.content_renderer import ContentRenderer
from utils.html_utils import render_image_html
from widgets.theme_aware import ThemeAwareMixin
from code_puppy.config import get_owner_name, get_puppy_name


# Role display name providers - allows dependency injection
def _default_user_name() -> str:
    return get_owner_name()


def _default_assistant_name() -> str:
    return get_puppy_name()


class MessageWidget(QFrame, ThemeAwareMixin):
    """A modern chat bubble message widget.

    User messages appear right-aligned with accent color.
    Assistant messages appear left-aligned with secondary background.
    Tool/thinking messages are centered with subtle styling.
    """

    copy_clicked = Signal(str)

    # Class-level name providers (can be overridden for testing)
    get_user_name = staticmethod(_default_user_name)
    get_assistant_name = staticmethod(_default_assistant_name)

    def __init__(self, message: Message, parent=None):
        super().__init__(parent)
        self._message = message
        self._collapsed = False
        self._is_tool_message = message.role in (
            MessageRole.THINKING, MessageRole.TOOL_CALL, MessageRole.TOOL_OUTPUT
        )
        self._is_user = message.role == MessageRole.USER

        self.setFrameShape(QFrame.Shape.NoFrame)
        self._setup_ui()
        self._update_content()

        # Listen for theme changes (via mixin)
        self.setup_theme_listener()

    def _on_theme_changed(self, theme):
        """Update styles when theme changes."""
        self._apply_styles()
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
            return "💭 Thinking", style.text_color, style.background_color
        elif role == MessageRole.TOOL_CALL:
            tool_name = self._message.metadata.get("tool_name", "Tool")
            return f"⚡ {tool_name}", style.text_color, style.background_color
        elif role == MessageRole.TOOL_OUTPUT:
            tool_name = self._message.metadata.get("tool_name", "Output")
            return f"📤 {tool_name}", style.text_color, style.background_color
        elif role == MessageRole.ERROR:
            error_type = self._message.metadata.get("error_type", "Error")
            return f"❌ {error_type}", style.text_color, style.background_color
        else:
            return self.get_assistant_name(), style.text_color, style.background_color

    def _setup_ui(self):
        """Set up the message card UI."""
        # Apply style directly to this frame (no nested frame)
        self._apply_styles()

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        role_text, role_color, bg_color = self._get_role_config()

        # Header row
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        # For tool messages, add collapse indicator
        if self._is_tool_message:
            self._collapse_indicator = QLabel("▼")
            self._collapse_indicator.setStyleSheet(f"color: {role_color}; font-size: 10px;")
            self._collapse_indicator.setFixedWidth(12)
            header_layout.addWidget(self._collapse_indicator)
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Role label
        self._role_label = QLabel(role_text)
        self._role_label.setStyleSheet(f"color: {role_color}; font-size: 12px; font-weight: bold;")
        header_layout.addWidget(self._role_label)

        header_layout.addStretch()

        # Copy button
        self._copy_btn = QPushButton("📋")
        self._copy_btn.setFixedSize(24, 24)
        self._copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._copy_btn.setToolTip("Copy")
        self._copy_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
        """)
        self._copy_btn.clicked.connect(self._on_copy)
        header_layout.addWidget(self._copy_btn)

        layout.addLayout(header_layout)

        # Content area
        self._content = QTextBrowser()
        self._content.setOpenExternalLinks(True)
        self._content.setFrameShape(QFrame.Shape.NoFrame)
        self._content.setStyleSheet(get_bubble_content_style(self._is_user))
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
        self._attachments_container.setStyleSheet("background-color: transparent;")
        self._attachments_layout = QVBoxLayout(self._attachments_container)
        self._attachments_layout.setContentsMargins(0, 0, 0, 8)
        self._attachments_layout.setSpacing(8)
        self._attachments_container.setVisible(False)
        layout.addWidget(self._attachments_container)

        # Connect click handler for tool messages
        if self._is_tool_message:
            self.mousePressEvent = self._on_header_click

    def _apply_styles(self):
        """Apply current theme styles to the message card."""
        self.setStyleSheet(get_message_bubble_style(
            is_user=self._is_user,
            is_tool=self._is_tool_message
        ))

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
        """Render tool output based on output_type in metadata."""
        output_type = metadata.get("output_type", ToolOutputType.JSON.value)

        if output_type == ToolOutputType.FILE_EDIT.value:
            return ContentRenderer.render_file_edit(
                filepath=metadata.get("filepath", ""),
                operation=metadata.get("operation", "modify"),
                success=metadata.get("success", True),
                message=metadata.get("message", ""),
                diff_text=metadata.get("diff_text", ""),
                changed=metadata.get("changed", True),
            )
        elif output_type == ToolOutputType.DIFF.value:
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
        """Add an image attachment widget using shared image rendering."""
        # Use shared utility for consistent rendering with tool call images
        img_html = render_image_html(filepath)
        if not img_html:
            return

        html = f'<div style="margin: 4px 0;">{img_html}</div>'

        # Create a QTextBrowser for HTML rendering
        img_browser = QTextBrowser()
        img_browser.setHtml(html)
        img_browser.setOpenExternalLinks(False)
        img_browser.setFrameShape(QFrame.Shape.NoFrame)
        img_browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        img_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        img_browser.setStyleSheet("background-color: transparent;")
        img_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # Auto-resize based on document content
        def adjust_browser_height(size=None):
            doc = img_browser.document()
            doc.setTextWidth(img_browser.viewport().width())
            height = int(doc.size().height()) + 8
            img_browser.setFixedHeight(max(50, height))

        img_browser.document().documentLayout().documentSizeChanged.connect(
            adjust_browser_height
        )

        self._attachments_layout.addWidget(img_browser)

    def _add_file_attachment(self, filepath: str):
        """Add a non-image file attachment widget."""
        file_label = QLabel(f"📎 {os.path.basename(filepath)}")
        file_label.setStyleSheet(f"color: {COLORS.text_secondary}; font-size: 12px;")
        self._attachments_layout.addWidget(file_label)

    def _adjust_height(self, size=None):
        """Adjust content height to fit text."""
        doc = self._content.document()
        doc.setTextWidth(self._content.viewport().width())
        height = int(doc.size().height()) + 16
        self._content.setFixedHeight(max(32, height))

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
        """Toggle collapse state for tool messages."""
        self._collapsed = not self._collapsed
        self._content.setVisible(not self._collapsed)
        if hasattr(self, '_collapse_indicator'):
            self._collapse_indicator.setText("▶" if self._collapsed else "▼")

    @property
    def message(self) -> Message:
        return self._message

    def resizeEvent(self, event):
        """Handle resize to reflow content."""
        super().resizeEvent(event)
        self._adjust_height()

    def cleanup(self):
        """Explicitly clean up resources. Call before discarding widget."""
        self.cleanup_theme_listener()

    def hideEvent(self, event):
        """Clean up when widget is hidden (removed from view)."""
        # Don't cleanup on hide - only when actually deleted
        super().hideEvent(event)


# Alias for backwards compatibility
MessageBubble = MessageWidget
