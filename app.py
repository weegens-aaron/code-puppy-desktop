"""Main application window.

Coordinates UI components and delegates to specialized services (SRP).
"""

import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QStatusBar, QPushButton, QTextEdit,
    QSplitter, QFileDialog, QFrame, QTabWidget,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence, QShortcut

from widgets.message_list import MessageListView
from widgets.collapsible_sidebar import CollapsibleSidebar
from models.data_types import Message, MessageRole
from services.agent_bridge import AgentBridge
from services.status_bar_manager import StatusBarManager
from services.streaming_handler import StreamingHandler
from services.session_manager import SessionManager
from utils.error_utils import categorize_error
from windows.dialogs.settings_dialog import SettingsDialog
from windows.dialogs.help_dialog import HelpDialog
from styles import (
    COLORS, get_main_window_style, get_send_button_style,
    get_cancel_button_style, get_attach_button_style,
    get_theme_manager, ColorScheme,
    get_attachment_chip_style, get_attachment_label_style,
    get_attachment_remove_style,
    get_modern_input_container_style, get_modern_input_field_style,
    get_tab_widget_style,
)
from code_puppy.config import get_puppy_name
from code_puppy.agents import get_current_agent


class CodePuppyApp(QMainWindow):
    """Main application window.

    Coordinates UI components and delegates to specialized services:
    - StatusBarManager: Status bar, activity indicator
    - StreamingHandler: Token buffering, message streaming
    - SessionManager: Session/history management
    - AgentBridge: Agent communication
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{get_puppy_name()} - {os.path.basename(os.getcwd())}")
        self.setMinimumSize(1200, 800)

        # Attachments list for current message
        self._attachments: list[str] = []

        # Theme manager
        self._theme_manager = get_theme_manager()
        self._theme_manager.add_listener(self._on_theme_changed)

        # Apply current theme
        self._apply_theme()

        # Initialize agent bridge
        self.agent_bridge = AgentBridge(self)

        # Set up UI first (creates message_list)
        self._setup_ui()
        self._setup_toolbar()

        # Initialize services (after UI is set up)
        self._setup_statusbar()
        self._streaming = StreamingHandler(self.message_list.message_model, parent=self)
        self._session = SessionManager(self.message_list.message_model, parent=self)

        self._setup_shortcuts()
        self._connect_agent_signals()

        # Add welcome message
        self._session.add_welcome_message()

        # Pre-warm agent after UI is ready
        QTimer.singleShot(100, self._prewarm_agent)

    def _prewarm_agent(self):
        """Pre-initialize agent in background."""
        self._status.show_message("Initializing agent...")
        self.agent_bridge.prewarm()
        QTimer.singleShot(2000, lambda: self._status.show_message("Ready"))

    def _apply_theme(self):
        """Apply current theme to the application."""
        self.setStyleSheet(get_main_window_style())

    def _on_theme_changed(self, theme: ColorScheme):
        """Handle theme change from settings."""
        self._apply_theme()
        self._refresh_widget_styles()
        self._status.show_message(f"Theme changed to: {theme.name}")

    def _connect_agent_signals(self):
        """Connect agent bridge signals to handlers."""
        # Main agent signals
        self.agent_bridge.token_received.connect(self._streaming.handle_token)
        self.agent_bridge.thinking_started.connect(self._on_thinking_started)
        self.agent_bridge.thinking_content.connect(self._streaming.append_thinking)
        self.agent_bridge.thinking_complete.connect(self._on_thinking_complete)
        self.agent_bridge.tool_call_started.connect(self._on_tool_call_started)
        self.agent_bridge.tool_call_args_delta.connect(self._streaming.append_tool_args)
        self.agent_bridge.tool_call_complete.connect(self._on_tool_call_complete)
        self.agent_bridge.tool_output_received.connect(self._streaming.add_tool_output)
        self.agent_bridge.diff_received.connect(self._streaming.add_diff)
        self.agent_bridge.response_complete.connect(self._on_response_complete)
        self.agent_bridge.error_occurred.connect(self._on_error)
        self.agent_bridge.agent_busy.connect(self._on_agent_busy)

        # Ask user question signal
        self.agent_bridge.ask_user_question_requested.connect(self._on_ask_user_question)

        # Hook-forwarded signals
        self.agent_bridge.agent_reloaded.connect(self._on_agent_reloaded)
        self.agent_bridge.agent_exception_occurred.connect(self._on_agent_exception)

    def _setup_ui(self):
        """Set up the user interface."""
        central = QWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main splitter for sidebar and chat
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Collapsible sidebar
        self.sidebar = CollapsibleSidebar(os.getcwd())
        self._connect_sidebar_signals()
        splitter.addWidget(self.sidebar)

        # Chat area
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # Tabbed chat area
        self.chat_tabs = QTabWidget()
        self.chat_tabs.setTabsClosable(False)
        self.chat_tabs.setStyleSheet(get_tab_widget_style())

        # Create chat tab
        self.message_list = MessageListView()
        self.message_list.question_answered.connect(self._on_question_answered)
        self.chat_tabs.addTab(self.message_list, "Chat")

        chat_layout.addWidget(self.chat_tabs, stretch=1)

        # Input area
        input_widget = self._create_input_area()
        chat_layout.addWidget(input_widget)

        splitter.addWidget(chat_widget)
        splitter.setSizes([250, 950])

        main_layout.addWidget(splitter)
        self.setCentralWidget(central)

    def _connect_sidebar_signals(self):
        """Connect sidebar signals."""
        self.sidebar.file_attached.connect(self._on_file_attached)
        self.sidebar.file_selected.connect(self._on_file_selected)
        self.sidebar.path_referenced.connect(self._on_path_referenced)
        self.sidebar.session_selected.connect(self._on_session_selected)
        self.sidebar.agent_selected.connect(self._on_agent_selected)
        self.sidebar.model_changed.connect(self._on_model_changed)
        self.sidebar.model_queued.connect(self._on_model_queued)
        self.sidebar.skills_changed.connect(lambda: self._status.show_message("Skills updated"))
        self.sidebar.servers_changed.connect(lambda: self._status.show_message("MCP servers updated"))

    def _create_input_area(self) -> QWidget:
        """Create the message input area."""
        container = QWidget()
        container.setStyleSheet(get_modern_input_container_style())

        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(8)

        # Attachments display
        self._attachments_widget = QWidget()
        self._attachments_layout = QHBoxLayout(self._attachments_widget)
        self._attachments_layout.setContentsMargins(8, 0, 8, 0)
        self._attachments_layout.setSpacing(8)
        self._attachments_widget.setVisible(False)
        layout.addWidget(self._attachments_widget)

        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        # Text input
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Message... (Ctrl+Enter to send)")
        self.input_field.setMinimumHeight(44)
        self.input_field.setMaximumHeight(120)
        self.input_field.setStyleSheet(get_modern_input_field_style())
        input_row.addWidget(self.input_field, stretch=1)

        # Buttons
        button_column = QVBoxLayout()
        button_column.setSpacing(4)

        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet(get_send_button_style())
        self.send_btn.setToolTip("Send message (Ctrl+Enter)")
        self.send_btn.clicked.connect(self._on_send)
        button_column.addWidget(self.send_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(get_cancel_button_style())
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._on_cancel)
        button_column.addWidget(self.cancel_btn)

        self.attach_btn = QPushButton("Attach")
        self.attach_btn.setStyleSheet(get_attach_button_style())
        self.attach_btn.setToolTip("Attach files")
        self.attach_btn.clicked.connect(self._on_attach)
        button_column.addWidget(self.attach_btn)

        input_row.addLayout(button_column)
        layout.addLayout(input_row)

        return container

    def _setup_toolbar(self):
        """Set up the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        self.addToolBar(toolbar)

        new_action = QAction("New Chat", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("Start a new conversation")
        new_action.triggered.connect(self._on_new_chat)
        toolbar.addAction(new_action)

        folder_action = QAction("Change Workspace", self)
        folder_action.setShortcut("Ctrl+O")
        folder_action.setStatusTip("Change working directory")
        folder_action.triggered.connect(self._on_open_folder)
        toolbar.addAction(folder_action)

        toolbar.addSeparator()

        settings_action = QAction("Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.setStatusTip("Open settings")
        settings_action.triggered.connect(self._on_settings)
        toolbar.addAction(settings_action)

        help_action = QAction("Help", self)
        help_action.setShortcut("F1")
        help_action.setStatusTip("Show help")
        help_action.triggered.connect(self._on_help)
        toolbar.addAction(help_action)

    def _setup_statusbar(self):
        """Set up the status bar."""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        self._status = StatusBarManager(status_bar, parent=self)

    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self._on_send)
        QShortcut(QKeySequence("Escape"), self).activated.connect(self._on_cancel)
        QShortcut(QKeySequence("Ctrl+B"), self).activated.connect(self.sidebar.toggle)
        QShortcut(QKeySequence("Ctrl+Shift+A"), self).activated.connect(lambda: self.sidebar.switch_to_tab('agents'))
        QShortcut(QKeySequence("Ctrl+M"), self).activated.connect(lambda: self.sidebar.switch_to_tab('models'))
        QShortcut(QKeySequence("Ctrl+Shift+S"), self).activated.connect(lambda: self.sidebar.switch_to_tab('skills'))
        QShortcut(QKeySequence("Ctrl+Shift+M"), self).activated.connect(lambda: self.sidebar.switch_to_tab('mcp'))

    # -------------------------------------------------------------------------
    # Attachment management
    # -------------------------------------------------------------------------

    def _add_attachment(self, filepath: str):
        """Add a file attachment."""
        if filepath not in self._attachments:
            self._attachments.append(filepath)
            self._update_attachments_display()

    def _remove_attachment(self, filepath: str):
        """Remove a file attachment."""
        if filepath in self._attachments:
            self._attachments.remove(filepath)
            self._update_attachments_display()

    def _clear_attachments(self):
        """Clear all attachments."""
        self._attachments.clear()
        self._update_attachments_display()

    def _update_attachments_display(self):
        """Update the attachments display."""
        while self._attachments_layout.count():
            item = self._attachments_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for filepath in self._attachments:
            chip = self._create_attachment_chip(filepath)
            self._attachments_layout.addWidget(chip)

        self._attachments_layout.addStretch()
        self._attachments_widget.setVisible(len(self._attachments) > 0)

    def _create_attachment_chip(self, filepath: str) -> QWidget:
        """Create an attachment chip widget."""
        chip = QWidget()
        chip.setStyleSheet(get_attachment_chip_style())
        layout = QHBoxLayout(chip)
        layout.setContentsMargins(8, 4, 4, 4)
        layout.setSpacing(4)

        filename = os.path.basename(filepath)
        label = QPushButton(filename)
        label.setStyleSheet(get_attachment_label_style())
        label.setToolTip(filepath)
        layout.addWidget(label)

        remove_btn = QPushButton("\u2715")
        remove_btn.setFixedSize(20, 20)
        remove_btn.setStyleSheet(get_attachment_remove_style())
        remove_btn.clicked.connect(lambda: self._remove_attachment(filepath))
        layout.addWidget(remove_btn)

        return chip

    # -------------------------------------------------------------------------
    # User actions
    # -------------------------------------------------------------------------

    def _on_send(self):
        """Handle send button click."""
        if self.agent_bridge.is_busy():
            return

        text = self.input_field.toPlainText().strip()
        if not text and not self._attachments:
            return

        # Add user message
        self._session.add_user_message(text, self._attachments.copy())
        self.input_field.clear()

        # Reset streaming state
        self._streaming.reset_indices()

        # Send to agent
        self.agent_bridge.send_message(text, self._attachments.copy())
        self._clear_attachments()

    def _on_attach(self):
        """Handle attach button click."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Attach Images", self.sidebar.get_root_path(),
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp)"
        )
        for filepath in files:
            self._add_attachment(filepath)

    def _on_file_attached(self, filepath: str):
        """Handle file attached from file tree."""
        self._add_attachment(filepath)
        self._status.show_message(f"Attached: {os.path.basename(filepath)}")

    def _on_file_selected(self, filepath: str):
        """Handle file selected from file tree."""
        self._status.show_message(f"Selected: {filepath}")

    def _on_path_referenced(self, path: str):
        """Handle path referenced from file tree."""
        current_text = self.input_field.toPlainText()
        if current_text and not current_text.endswith(' '):
            path = ' ' + path
        self.input_field.insertPlainText(path)
        self.input_field.setFocus()

    def _on_cancel(self):
        """Handle cancel button click."""
        if self.agent_bridge.is_busy():
            self.agent_bridge.cancel()
            self._status.stop_activity()
            self._streaming.flush_and_stop()
            self._streaming.reset_indices()
            self._set_ui_enabled(True)
            self._status.show_message("Cancelled")

    def _on_new_chat(self):
        """Handle new chat action."""
        if self.agent_bridge.is_busy():
            self._status.show_message("Cannot start new chat while agent is running")
            return

        self._start_new_session()
        self._status.show_message("New conversation started")

    def _on_open_folder(self):
        """Handle change workspace action."""
        if self.agent_bridge.is_busy():
            self._status.show_message("Cannot change workspace while agent is running")
            return

        folder = QFileDialog.getExistingDirectory(
            self, "Change Workspace", self.sidebar.get_root_path(),
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            os.chdir(folder)
            self.sidebar.set_root_path(folder)
            self.setWindowTitle(f"{get_puppy_name()} - {os.path.basename(folder)}")
            self._start_new_session()
            self._status.show_message(f"New session in: {folder}")

    def _start_new_session(self):
        """Start a new session."""
        self._streaming.reset_indices()
        self._clear_attachments()

        # Clear UI widgets
        self.message_list.clear()
        self._session.start_new_session(self.agent_bridge.clear_history)
        self._status.update_info()

    def _on_settings(self):
        """Handle settings action."""
        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(self._apply_settings)
        dialog.exec()

    def _apply_settings(self, settings: dict):
        """Apply settings from dialog."""
        theme_name = settings.get("theme", "")
        if theme_name:
            self._status.show_message(f"Theme: {theme_name}")

    def _on_help(self):
        """Handle help action."""
        HelpDialog(self).exec()

    def _on_agent_selected(self, agent_name: str):
        """Handle agent selection from sidebar panel."""
        if self.agent_bridge.is_busy():
            self._status.show_message("Cannot change agent while processing")
            return

        self._start_new_session()
        self.setWindowTitle(f"{get_puppy_name()} - {os.path.basename(os.getcwd())}")
        self._status.show_message(f"Switched to agent: {agent_name}")

    def _on_model_changed(self, model_name: str):
        """Handle model change from sidebar panel."""
        self._status.update_info()
        self._status.show_message(f"Model changed to: {model_name}")

    def _on_model_queued(self, model_name: str):
        """Handle model change queued (agent is busy)."""
        self._status.show_message(f"Model '{model_name}' queued (will apply after response)")

    def _on_session_selected(self, session_name: str):
        """Handle session selection from the sessions panel."""
        if self.agent_bridge.is_busy():
            self._status.show_message("Cannot change session while agent is running")
            return

        if session_name == "__NEW__":
            self._on_new_chat()
            return

        history = self.sidebar.sessions_panel.get_loaded_history()
        if history:
            self._streaming.reset_indices()
            self.message_list.clear()

            success = self._session.load_session(
                session_name, history,
                lambda: self.message_list.verticalScrollBar().setValue(
                    self.message_list.verticalScrollBar().maximum()
                )
            )

            if success:
                self._status.update_context_only()
                self._status.show_message(f"Session resumed: {len(history)} messages")

    # -------------------------------------------------------------------------
    # Agent event handlers
    # -------------------------------------------------------------------------

    def _on_thinking_started(self):
        """Handle thinking started event."""
        self._status.show_message("Thinking...")
        self._streaming.start_thinking()

    def _on_thinking_complete(self):
        """Handle thinking complete event."""
        self._status.show_message("Responding...")
        self._streaming.complete_thinking()

    def _on_tool_call_started(self, tool_name: str, tool_args: str):
        """Handle tool call started event."""
        self._status.start_activity(tool_name)
        self._streaming.start_tool_call(tool_name, tool_args)

    def _on_tool_call_complete(self, tool_name: str):
        """Handle tool call complete event."""
        if self._status.current_tool == tool_name:
            self._status.stop_activity()
        self._status.show_message(f"Tool complete: {tool_name}")
        self._streaming.complete_tool_call(tool_name)

    def _on_response_complete(self, response: str):
        """Handle response completion."""
        self._status.stop_activity()

        # Check if we got any content (streaming tokens or final response)
        has_content = (
            response.strip() or
            self._streaming.assistant_message_index is not None
        )

        if has_content:
            self._streaming.complete_response(response)
            self._status.show_message("Ready")
        else:
            # No content received - errors should already be displayed via _on_error
            # Just clean up streaming state
            self._streaming.complete_response_empty()
            self._status.show_message("Ready")

    def _on_error(self, error: str):
        """Handle agent error."""
        self._status.stop_activity()
        self._status.show_message(f"Error: {error[:50]}...")

        # Flush any pending tokens and reset streaming state
        self._streaming.flush_and_stop()

        # Categorize error
        error_type = self._categorize_error(error)
        self._streaming.add_error(error, error_type)

        # Reset streaming indices for next message
        self._streaming.reset_indices()

    def _categorize_error(self, error: str) -> str:
        """Categorize an error message using shared utility."""
        return categorize_error(error)

    def _on_agent_busy(self, busy: bool):
        """Handle agent busy state change."""
        self._set_ui_enabled(not busy)
        
        # Update sidebar panels about busy state (for queuing model changes)
        self.sidebar.set_agent_busy(busy)

        if busy:
            self._status.show_message("Processing...")
        else:
            self._status.stop_activity()
            self._status.show_message("Ready")
            self._status.update_info()

    def _set_ui_enabled(self, enabled: bool):
        """Enable or disable UI controls."""
        self.send_btn.setEnabled(enabled)
        self.attach_btn.setEnabled(enabled)
        self.cancel_btn.setEnabled(not enabled)
        self.input_field.setEnabled(enabled)

    def _on_agent_reloaded(self):
        """Handle agent reload - refresh panels."""
        logger.info("Agent reloaded, refreshing panels")
        self.sidebar.refresh_all()

    def _on_agent_exception(self, error: str):
        """Handle agent exception from hook (backup error capture)."""
        logger.info(f"Agent exception from hook: {error}")
        # Only show if we're currently processing (to avoid duplicate errors)
        if self.agent_bridge.is_busy():
            self._on_error(error)

    # -------------------------------------------------------------------------
    # Ask user question
    # -------------------------------------------------------------------------

    def _on_ask_user_question(self, questions_json: str):
        """Handle ask_user_question tool request.

        Adds an interactive question message to the chat for inline response.
        """
        try:
            questions = json.loads(questions_json)
            logger.info(f"Adding inline question with {len(questions)} questions")

            # Add question message to chat (will create QuestionWidget)
            self.message_list.message_model.add_message(
                Message(
                    role=MessageRole.QUESTION,
                    content="",
                    metadata={"questions": questions}
                )
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse questions JSON: {e}")
            self.agent_bridge.set_question_response({"cancelled": True, "answers": []})
        except Exception as e:
            logger.error(f"Error handling ask_user_question: {e}", exc_info=True)
            self.agent_bridge.set_question_response({"cancelled": True, "answers": []})

    def _on_question_answered(self, result: dict):
        """Handle user's answer to an inline question.

        Args:
            result: Dict with structure {"cancelled": bool, "answers": [...]}
        """
        logger.info(f"Question answered: cancelled={result.get('cancelled', False)}")
        self.agent_bridge.set_question_response(result)

    # -------------------------------------------------------------------------
    # Theme refresh
    # -------------------------------------------------------------------------

    def _refresh_widget_styles(self):
        """Refresh widget styles after theme change."""
        self.input_field.setStyleSheet(get_modern_input_field_style())
        self.send_btn.setStyleSheet(get_send_button_style())
        self.cancel_btn.setStyleSheet(get_cancel_button_style())
        self.attach_btn.setStyleSheet(get_attach_button_style())
        self.chat_tabs.setStyleSheet(get_tab_widget_style())

        input_container = self.input_field.parent()
        if input_container and input_container.parent():
            input_container.parent().setStyleSheet(get_modern_input_container_style())

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    def closeEvent(self, event):
        """Clean up on close."""
        # Stop timers
        self._streaming.cleanup()
        self._status.cleanup()

        # Clean up theme listener
        try:
            self._theme_manager.remove_listener(self._on_theme_changed)
        except Exception:
            pass

        # Clean up child widgets
        if hasattr(self.message_list, 'cleanup'):
            self.message_list.cleanup()
        if hasattr(self.sidebar, 'cleanup'):
            self.sidebar.cleanup()

        self.agent_bridge.cleanup()
        super().closeEvent(event)
