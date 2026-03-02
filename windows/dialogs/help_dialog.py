"""Help dialog with keyboard shortcuts and usage information."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QTextBrowser, QPushButton,
    QScrollArea, QFrame,
)
from PySide6.QtCore import Qt


class HelpDialog(QDialog):
    """Help dialog showing keyboard shortcuts and usage guide.

    Provides tabs for:
    - Quick Start guide
    - Keyboard Shortcuts
    - Features overview
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help - Code Puppy")
        self.setMinimumSize(600, 500)
        self.setModal(True)

        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Header
        header = QLabel("Code Puppy Desktop")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #4fc3f7;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        subtitle = QLabel("Your AI Coding Assistant")
        subtitle.setStyleSheet("font-size: 14px; color: #a0a0a0;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Tab widget
        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        # Quick Start tab
        self._tabs.addTab(self._create_quick_start_tab(), "Quick Start")

        # Shortcuts tab
        self._tabs.addTab(self._create_shortcuts_tab(), "Keyboard Shortcuts")

        # Features tab
        self._tabs.addTab(self._create_features_tab(), "Features")

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _apply_style(self):
        """Apply dark theme styling."""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #a0a0a0;
                padding: 8px 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3d3d3d;
                color: #e0e0e0;
            }
            QTextBrowser {
                background-color: transparent;
                border: none;
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)

    def _create_quick_start_tab(self) -> QWidget:
        """Create the quick start guide tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
        <h2 style="color: #4fc3f7;">Getting Started</h2>

        <h3 style="color: #e0e0e0;">1. Start a Conversation</h3>
        <p>Type your coding question or request in the input box at the bottom
        and press <b>Ctrl+Enter</b> or click <b>Send</b>.</p>

        <h3 style="color: #e0e0e0;">2. Attach Files</h3>
        <p>Click the <b>Attach</b> button or drag files from the sidebar to
        include them in your message. Use <b>@filepath</b> syntax to reference
        files in your prompt.</p>

        <h3 style="color: #e0e0e0;">3. Browse Files</h3>
        <p>Use the file tree on the left to browse your project. Double-click
        files to view them, or right-click for more options.</p>

        <h3 style="color: #e0e0e0;">4. Review Responses</h3>
        <p>Code Puppy will stream responses in real-time. You can see:
        <ul>
        <li><b>Thinking</b> - The AI's reasoning process (collapsible)</li>
        <li><b>Tool Calls</b> - Actions taken (file edits, searches, etc.)</li>
        <li><b>Response</b> - The final answer with formatted code</li>
        </ul>
        </p>

        <h3 style="color: #e0e0e0;">5. Copy Code</h3>
        <p>Click the <b>Copy</b> button on any message to copy its content
        to your clipboard.</p>
        """)
        layout.addWidget(browser)
        return tab

    def _create_shortcuts_tab(self) -> QWidget:
        """Create the keyboard shortcuts tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        shortcuts = [
            ("Ctrl+Enter", "Send message"),
            ("Ctrl+N", "New conversation"),
            ("Ctrl+,", "Open settings"),
            ("Escape", "Cancel current operation"),
            ("F1", "Show this help dialog"),
            ("Ctrl+L", "Clear conversation"),
            ("Ctrl+Shift+C", "Copy last response"),
        ]

        browser = QTextBrowser()
        html = "<h2 style='color: #4fc3f7;'>Keyboard Shortcuts</h2><table>"

        for key, description in shortcuts:
            html += f"""
            <tr>
                <td style="padding: 8px; background-color: #3d3d3d; border-radius: 4px; font-family: monospace;">
                    {key}
                </td>
                <td style="padding: 8px 16px; color: #e0e0e0;">
                    {description}
                </td>
            </tr>
            <tr><td colspan="2" style="height: 4px;"></td></tr>
            """

        html += "</table>"
        browser.setHtml(html)
        layout.addWidget(browser)
        return tab

    def _create_features_tab(self) -> QWidget:
        """Create the features overview tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
        <h2 style="color: #4fc3f7;">Features</h2>

        <h3 style="color: #34a853;">\u2713 Streaming Responses</h3>
        <p>See AI responses as they're generated in real-time, with smooth
        token-by-token streaming.</p>

        <h3 style="color: #34a853;">\u2713 Code Highlighting</h3>
        <p>Syntax highlighting for all major programming languages in both
        questions and responses.</p>

        <h3 style="color: #34a853;">\u2713 File Context</h3>
        <p>Attach files to your messages or reference them with @filepath
        syntax for context-aware assistance.</p>

        <h3 style="color: #34a853;">\u2713 Tool Visibility</h3>
        <p>See what tools the AI is using (file operations, searches, etc.)
        with expandable details.</p>

        <h3 style="color: #34a853;">\u2713 Thinking Display</h3>
        <p>Optional display of the AI's reasoning process for transparency
        and learning.</p>

        <h3 style="color: #34a853;">\u2713 Dark Theme</h3>
        <p>Easy on the eyes with a carefully designed dark theme optimized
        for coding.</p>

        <h3 style="color: #34a853;">\u2713 Native Performance</h3>
        <p>Built with PySide6/Qt for fast, responsive native desktop
        performance.</p>

        <hr style="border-color: #3d3d3d;">

        <p style="color: #a0a0a0; text-align: center;">
            Code Puppy Desktop v0.1.0<br>
            <a href="https://github.com/weegens-aaron/code_puppy" style="color: #4fc3f7;">
                GitHub Repository
            </a>
        </p>
        """)
        layout.addWidget(browser)
        return tab
