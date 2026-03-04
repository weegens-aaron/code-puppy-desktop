"""Help dialog with keyboard shortcuts and usage information."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QTextBrowser, QPushButton,
)
from PySide6.QtCore import Qt

from styles import COLORS, get_theme_manager


class HelpDialog(QDialog):
    """Help dialog showing keyboard shortcuts and usage guide."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help")
        self.setMinimumSize(500, 450)
        self.setModal(True)

        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header = QLabel("Code Puppy Desktop")
        header.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLORS.text_primary};")
        layout.addWidget(header)

        # Content
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(self._get_help_content())
        layout.addWidget(browser)

        # Footer with buttons
        button_layout = QHBoxLayout()

        github_btn = QPushButton("GitHub")
        github_btn.setStyleSheet(self._get_secondary_button_style())
        github_btn.clicked.connect(self._open_github)
        button_layout.addWidget(github_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(self._get_primary_button_style())
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _get_help_content(self) -> str:
        """Generate help content HTML."""
        return f"""
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; color: {COLORS.text_primary}; }}
            h2 {{ color: {COLORS.text_primary}; font-size: 14px; margin-top: 16px; margin-bottom: 8px; }}
            p {{ color: {COLORS.text_secondary}; margin: 4px 0; font-size: 13px; }}
            table {{ margin: 8px 0; }}
            td {{ padding: 4px 12px 4px 0; font-size: 13px; }}
            .key {{
                background-color: {COLORS.bg_tertiary};
                padding: 2px 8px;
                border-radius: 3px;
                font-family: monospace;
                color: {COLORS.text_primary};
            }}
            .desc {{ color: {COLORS.text_secondary}; }}
        </style>

        <h2>Keyboard Shortcuts</h2>
        <table>
            <tr><td><span class="key">Ctrl+Enter</span></td><td class="desc">Send message</td></tr>
            <tr><td><span class="key">Ctrl+N</span></td><td class="desc">New conversation</td></tr>
            <tr><td><span class="key">Ctrl+B</span></td><td class="desc">Toggle sidebar</td></tr>
            <tr><td><span class="key">Ctrl+,</span></td><td class="desc">Settings</td></tr>
            <tr><td><span class="key">Escape</span></td><td class="desc">Cancel operation</td></tr>
            <tr><td><span class="key">F1</span></td><td class="desc">Help</td></tr>
        </table>

        <h2>Tips</h2>
        <p>Drag files from the sidebar to attach them to your message.</p>
        <p>Click the copy button on any message to copy its content.</p>
        <p>Collapse tool and thinking sections by clicking their headers.</p>

        <h2>About</h2>
        <p>Code Puppy Desktop v0.1.0</p>
        <p>A desktop GUI for the Code Puppy AI assistant.</p>
        """

    def _apply_style(self):
        """Apply theme styling."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS.bg_primary};
                color: {COLORS.text_primary};
            }}
            QTextBrowser {{
                background-color: {COLORS.bg_secondary};
                border: 1px solid {COLORS.border_subtle};
                border-radius: 4px;
                padding: 12px;
            }}
            QLabel {{
                color: {COLORS.text_primary};
            }}
        """)

    def _get_primary_button_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {COLORS.accent_primary};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS.accent_primary_hover};
            }}
        """

    def _get_secondary_button_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {COLORS.bg_tertiary};
                color: {COLORS.text_primary};
                border: 1px solid {COLORS.border_default};
                border-radius: 4px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background-color: {COLORS.bg_secondary};
            }}
        """

    def _open_github(self):
        """Open GitHub repository in browser."""
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl("https://github.com/weegens-aaron/code-puppy-desktop"))
