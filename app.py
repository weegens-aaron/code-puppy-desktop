"""Main application window."""

import os
import time
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QStatusBar, QPushButton, QTextEdit,
    QSplitter, QFileDialog, QLabel, QFrame,
)
from PySide6.QtCore import Qt, QTimer, QElapsedTimer
from PySide6.QtGui import QAction, QKeySequence, QShortcut

from desktop.widgets.message_list import MessageListView
from desktop.widgets.file_tree import FileTree
from desktop.models.data_types import Message, MessageRole, ToolOutputType
from desktop.services.agent_bridge import AgentBridge
from desktop.windows.dialogs.settings_dialog import SettingsDialog
from desktop.windows.dialogs.help_dialog import HelpDialog
from desktop.windows.dialogs.agent_dialog import AgentDialog
from desktop.windows.dialogs.skills_dialog import SkillsDialog
from desktop.windows.dialogs.mcp_dialog import MCPDialog
from desktop.windows.dialogs.model_dialog import ModelDialog
from desktop.windows.dialogs.session_dialog import SessionDialog
from desktop.styles import (
    COLORS, get_main_window_style, get_send_button_style,
    get_cancel_button_style, get_attach_button_style, input_style,
    get_theme_manager, ColorScheme,
)
from code_puppy.config import get_owner_name, get_puppy_name
from code_puppy.agents import get_current_agent
from code_puppy.command_line.model_picker_completion import get_active_model


class CodePuppyApp(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{get_puppy_name()} - {os.path.basename(os.getcwd())}")
        self.setMinimumSize(1200, 800)

        # Attachments list for current message
        self._attachments: list[str] = []

        # Token buffering for throttled UI updates
        self._token_buffer: list[str] = []
        self._token_timer = QTimer(self)
        self._token_timer.setInterval(50)  # Flush every 50ms
        self._token_timer.timeout.connect(self._flush_token_buffer)

        # Track current message indices for streaming updates
        self._current_thinking_index: int | None = None
        self._current_tool_indices: dict[str, int] = {}  # tool_name -> message index
        self._assistant_message_index: int | None = None  # Track assistant message for streaming

        # Activity indicator for long operations
        self._activity_timer = QTimer(self)
        self._activity_timer.setInterval(100)  # Update every 100ms
        self._activity_timer.timeout.connect(self._update_activity_indicator)
        self._activity_frame = 0
        self._activity_start_time: float = 0
        self._current_tool_name: str = ""
        self._activity_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

        # Theme manager
        self._theme_manager = get_theme_manager()
        self._theme_manager.add_listener(self._on_theme_changed)

        # Apply current theme
        self._apply_theme()

        # Initialize agent bridge
        self.agent_bridge = AgentBridge(self)
        self._connect_agent_signals()

        self._setup_ui()
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_shortcuts()

        # Add welcome message
        self._add_welcome_message()

        # Pre-warm agent after UI is ready (reduces first-message latency)
        QTimer.singleShot(100, self._prewarm_agent)

    def _prewarm_agent(self):
        """Pre-initialize agent in background."""
        self.statusBar().showMessage("Initializing agent...")
        self.agent_bridge.prewarm()
        # Clear status after a moment
        QTimer.singleShot(2000, lambda: self.statusBar().showMessage("Ready"))

    def _apply_theme(self):
        """Apply current theme to the application."""
        self.setStyleSheet(get_main_window_style())

    def _on_theme_changed(self, theme: ColorScheme):
        """Handle theme change from settings."""
        self._apply_theme()
        self._refresh_widget_styles()
        self.statusBar().showMessage(f"Theme changed to: {theme.name}")

    def _connect_agent_signals(self):
        """Connect agent bridge signals to handlers."""
        self.agent_bridge.token_received.connect(self._on_token)
        self.agent_bridge.thinking_started.connect(self._on_thinking_started)
        self.agent_bridge.thinking_content.connect(self._on_thinking_content)
        self.agent_bridge.thinking_complete.connect(self._on_thinking_complete)
        self.agent_bridge.tool_call_started.connect(self._on_tool_call_started)
        self.agent_bridge.tool_call_args_delta.connect(self._on_tool_call_args_delta)
        self.agent_bridge.tool_call_complete.connect(self._on_tool_call_complete)
        self.agent_bridge.tool_output_received.connect(self._on_tool_output)
        self.agent_bridge.response_complete.connect(self._on_response_complete)
        self.agent_bridge.error_occurred.connect(self._on_error)
        self.agent_bridge.agent_busy.connect(self._on_agent_busy)

    def _setup_ui(self):
        """Set up the user interface."""
        central = QWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main splitter for sidebar and chat
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # File tree sidebar
        self.file_tree = FileTree(os.getcwd())
        self.file_tree.setMinimumWidth(200)
        self.file_tree.setMaximumWidth(400)
        self.file_tree.file_attached.connect(self._on_file_attached)
        self.file_tree.file_selected.connect(self._on_file_selected)
        self.file_tree.path_referenced.connect(self._on_path_referenced)
        splitter.addWidget(self.file_tree)

        # Chat area
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # Message list
        self.message_list = MessageListView()
        chat_layout.addWidget(self.message_list, stretch=1)

        # Input area
        input_widget = self._create_input_area()
        chat_layout.addWidget(input_widget)

        splitter.addWidget(chat_widget)

        # Set splitter proportions (1:3 ratio)
        splitter.setSizes([250, 950])

        main_layout.addWidget(splitter)
        self.setCentralWidget(central)

    def _create_input_area(self) -> QWidget:
        """Create the message input area."""
        container = QWidget()
        container.setStyleSheet(f"QWidget {{ background-color: {COLORS.bg_secondary}; }}")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Attachments display
        self._attachments_widget = QWidget()
        self._attachments_layout = QHBoxLayout(self._attachments_widget)
        self._attachments_layout.setContentsMargins(0, 0, 0, 0)
        self._attachments_layout.setSpacing(4)
        self._attachments_widget.setVisible(False)
        layout.addWidget(self._attachments_widget)

        # Text input
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Type a message... (Ctrl+Enter to send)")
        self.input_field.setMaximumHeight(120)
        self.input_field.setStyleSheet(input_style())
        layout.addWidget(self.input_field)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        # Attach button
        self.attach_btn = QPushButton("Attach")
        self.attach_btn.setStyleSheet(get_attach_button_style())
        self.attach_btn.clicked.connect(self._on_attach)
        button_layout.addWidget(self.attach_btn)

        # Cancel button (hidden by default)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(get_cancel_button_style())
        self.cancel_btn.clicked.connect(self._on_cancel)
        self.cancel_btn.setVisible(False)
        button_layout.addWidget(self.cancel_btn)

        button_layout.addStretch()

        # Send button
        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet(get_send_button_style())
        self.send_btn.clicked.connect(self._on_send)
        button_layout.addWidget(self.send_btn)

        layout.addLayout(button_layout)

        return container

    def _setup_toolbar(self):
        """Set up the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # New conversation action
        new_action = QAction("New Chat", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("Start a new conversation")
        new_action.triggered.connect(self._on_new_chat)
        toolbar.addAction(new_action)

        # Resume session action
        resume_action = QAction("Resume", self)
        resume_action.setShortcut("Ctrl+R")
        resume_action.setStatusTip("Resume a previous session")
        resume_action.triggered.connect(self._on_resume)
        toolbar.addAction(resume_action)

        toolbar.addSeparator()

        # Change workspace action
        folder_action = QAction("Change Workspace", self)
        folder_action.setShortcut("Ctrl+O")
        folder_action.setStatusTip("Change working directory")
        folder_action.triggered.connect(self._on_open_folder)
        toolbar.addAction(folder_action)

        toolbar.addSeparator()

        # Agents action
        agents_action = QAction("Agents", self)
        agents_action.setShortcut("Ctrl+Shift+A")
        agents_action.setStatusTip("Select agent")
        agents_action.triggered.connect(self._on_agents)
        toolbar.addAction(agents_action)

        # Skills action
        skills_action = QAction("Skills", self)
        skills_action.setShortcut("Ctrl+Shift+S")
        skills_action.setStatusTip("Manage skills")
        skills_action.triggered.connect(self._on_skills)
        toolbar.addAction(skills_action)

        # MCP action
        mcp_action = QAction("MCP", self)
        mcp_action.setShortcut("Ctrl+Shift+M")
        mcp_action.setStatusTip("Manage MCP servers")
        mcp_action.triggered.connect(self._on_mcp)
        toolbar.addAction(mcp_action)

        # Model action
        model_action = QAction("Model", self)
        model_action.setShortcut("Ctrl+M")
        model_action.setStatusTip("Select AI model")
        model_action.triggered.connect(self._on_model)
        toolbar.addAction(model_action)

        toolbar.addSeparator()

        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.setStatusTip("Open settings")
        settings_action.triggered.connect(self._on_settings)
        toolbar.addAction(settings_action)

        # Help action
        help_action = QAction("Help", self)
        help_action.setShortcut("F1")
        help_action.setStatusTip("Show help")
        help_action.triggered.connect(self._on_help)
        toolbar.addAction(help_action)

    def _setup_statusbar(self):
        """Set up the status bar."""
        self.setStatusBar(QStatusBar())

        # Activity indicator (left side, shows during operations)
        self._activity_label = QLabel()
        self._activity_label.setStyleSheet(f"color: {COLORS.accent_info}; padding: 0 8px; font-weight: bold;")
        self._activity_label.setVisible(False)
        self.statusBar().addWidget(self._activity_label)

        # Create permanent widgets for model, agent, and context info
        self._context_label = QLabel()
        self._context_label.setStyleSheet(f"color: {COLORS.text_secondary}; padding: 0 8px;")

        # Separator 1
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        separator1.setStyleSheet(f"color: {COLORS.border_subtle};")

        self._agent_label = QLabel()
        self._agent_label.setStyleSheet(f"color: {COLORS.accent_success}; padding: 0 8px;")

        # Separator 2
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setStyleSheet(f"color: {COLORS.border_subtle};")

        self._model_label = QLabel()
        self._model_label.setStyleSheet(f"color: {COLORS.accent_info}; padding: 0 8px;")

        # Add permanent widgets (right side): context | agent | model
        self.statusBar().addPermanentWidget(self._context_label)
        self.statusBar().addPermanentWidget(separator1)
        self.statusBar().addPermanentWidget(self._agent_label)
        self.statusBar().addPermanentWidget(separator2)
        self.statusBar().addPermanentWidget(self._model_label)

        # Initialize displays
        self._update_status_bar_info()

        self.statusBar().showMessage("Ready")

    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # Ctrl+Enter to send
        send_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        send_shortcut.activated.connect(self._on_send)

        # Escape to cancel
        cancel_shortcut = QShortcut(QKeySequence("Escape"), self)
        cancel_shortcut.activated.connect(self._on_cancel)

    def _add_welcome_message(self):
        """Add welcome message on startup."""
        owner_name = get_owner_name()
        agent = get_current_agent()
        agent_name = agent.display_name if agent else get_puppy_name()
        description = agent.description if agent else "your AI coding assistant"
        self.message_list.message_model.add_message(
            Message(
                role=MessageRole.ASSISTANT,
                content=f"Hello {owner_name}! I'm {agent_name}. {description}. How can I help you today?"
            )
        )

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
        # Clear existing widgets
        while self._attachments_layout.count():
            item = self._attachments_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add attachment chips
        for filepath in self._attachments:
            chip = self._create_attachment_chip(filepath)
            self._attachments_layout.addWidget(chip)

        self._attachments_layout.addStretch()
        self._attachments_widget.setVisible(len(self._attachments) > 0)

    def _create_attachment_chip(self, filepath: str) -> QWidget:
        """Create an attachment chip widget."""
        chip = QWidget()
        chip.setStyleSheet("""
            QWidget {
                background-color: #3d3d3d;
                border-radius: 4px;
                padding: 2px;
            }
        """)
        layout = QHBoxLayout(chip)
        layout.setContentsMargins(8, 4, 4, 4)
        layout.setSpacing(4)

        # File name
        filename = os.path.basename(filepath)
        label = QPushButton(filename)
        label.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #e0e0e0;
                border: none;
                text-align: left;
                padding: 0;
            }
        """)
        label.setToolTip(filepath)
        layout.addWidget(label)

        # Remove button
        remove_btn = QPushButton("\u2715")
        remove_btn.setFixedSize(20, 20)
        remove_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #a0a0a0;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #ff6b6b;
            }
        """)
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

        # Add user message with attachments
        self.message_list.message_model.add_message(
            Message(role=MessageRole.USER, content=text, attachments=self._attachments.copy())
        )
        self.input_field.clear()

        # Reset assistant message tracking (will be created when first token arrives)
        self._assistant_message_index = None

        # Send to agent with attachments
        attachments_to_send = self._attachments.copy()
        self.agent_bridge.send_message(text, attachments_to_send)
        self._clear_attachments()

    def _on_attach(self):
        """Handle attach button click."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Attach",
            self.file_tree.get_root_path(),
            "All Files (*.*)"
        )
        for filepath in files:
            self._add_attachment(filepath)

    def _on_file_attached(self, filepath: str):
        """Handle file attached from file tree."""
        self._add_attachment(filepath)
        self.statusBar().showMessage(f"Attached: {os.path.basename(filepath)}")

    def _on_file_selected(self, filepath: str):
        """Handle file selected from file tree."""
        # For now, just show in status bar
        # In future, could open in a preview pane
        self.statusBar().showMessage(f"Selected: {filepath}")

    def _on_path_referenced(self, path: str):
        """Handle path referenced from file tree - insert into chat input."""
        current_text = self.input_field.toPlainText()
        if current_text and not current_text.endswith(' '):
            path = ' ' + path
        self.input_field.insertPlainText(path)
        self.input_field.setFocus()

    def _on_cancel(self):
        """Handle cancel button click."""
        if self.agent_bridge.is_busy():
            self.agent_bridge.cancel()
            # Stop activity indicator and reset UI
            self._stop_activity_indicator()
            self._token_timer.stop()
            self._flush_token_buffer()
            # Clear tracked indices
            self._current_thinking_index = None
            self._current_tool_indices.clear()
            self._assistant_message_index = None
            # Re-enable UI
            self.send_btn.setEnabled(True)
            self.attach_btn.setEnabled(True)
            self.cancel_btn.setVisible(False)
            self.input_field.setEnabled(True)
            self.statusBar().showMessage("Cancelled")

    def _on_new_chat(self):
        """Handle new chat action."""
        if self.agent_bridge.is_busy():
            self.statusBar().showMessage("Cannot start new chat while agent is running")
            return

        # Clear agent conversation history (same as CLI 'clear' command)
        self.agent_bridge.clear_history()
        # Clear UI message list (clears both model and widgets)
        self.message_list.clear()
        self._clear_attachments()
        # Clear tracked message indices
        self._current_thinking_index = None
        self._current_tool_indices.clear()
        self._assistant_message_index = None
        self._add_welcome_message()
        self._update_status_bar_info()
        self.statusBar().showMessage("New conversation started")

    def _on_open_folder(self):
        """Handle change workspace action."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Change Workspace",
            self.file_tree.get_root_path(),
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            # Change the actual working directory
            os.chdir(folder)
            # Update the file tree
            self.file_tree.set_root_path(folder)
            # Update window title
            self.setWindowTitle(f"{get_puppy_name()} - {os.path.basename(folder)}")
            self.statusBar().showMessage(f"Workspace: {folder}")

    def _on_settings(self):
        """Handle settings action."""
        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(self._apply_settings)
        dialog.exec()

    def _apply_settings(self, settings: dict):
        """Apply settings from dialog."""
        # Theme is applied automatically via the theme manager listener
        theme_name = settings.get("theme", "")
        if theme_name:
            self.statusBar().showMessage(f"Theme: {theme_name}")

    def _on_help(self):
        """Handle help action."""
        dialog = HelpDialog(self)
        dialog.exec()

    def _on_agents(self):
        """Handle agents action - show agent selection dialog."""
        if self.agent_bridge.is_busy():
            self.statusBar().showMessage("Cannot change agent while processing")
            return

        dialog = AgentDialog(self)
        if dialog.exec():
            selected = dialog.get_selected_agent()
            if selected:
                # Clear the cached agent in the worker so it picks up the new one
                self.agent_bridge.clear_history()
                # Update displays
                self._update_status_bar_info()
                self.setWindowTitle(f"{get_puppy_name()} - {os.path.basename(os.getcwd())}")
                self.statusBar().showMessage(f"Switched to agent: {selected}")

    def _on_skills(self):
        """Handle skills action - show skills management dialog."""
        dialog = SkillsDialog(self)
        dialog.exec()

    def _on_mcp(self):
        """Handle MCP action - show MCP server management dialog."""
        dialog = MCPDialog(self)
        dialog.exec()

    def _on_model(self):
        """Handle model action - show model selection dialog."""
        dialog = ModelDialog(self)
        if dialog.exec():
            # Update status bar to show new model
            self._update_status_bar_info()
            self.statusBar().showMessage(f"Model changed to: {dialog.get_selected_model()}")

    def _on_resume(self):
        """Handle resume action - show session picker dialog."""
        if self.agent_bridge.is_busy():
            self.statusBar().showMessage("Cannot resume session while agent is running")
            return

        dialog = SessionDialog(self)
        if dialog.exec():
            session_name = dialog.get_selected_session()
            history = dialog.get_loaded_history()

            if session_name == "__NEW__":
                # User requested a new session
                self._on_new_chat()
                self.statusBar().showMessage("New session started")
                return

            if history:
                # Clear current state
                self.message_list.clear()
                self._current_thinking_index = None
                self._current_tool_indices.clear()
                self._assistant_message_index = None

                # Load history into agent
                agent = get_current_agent()
                if agent:
                    agent.set_message_history(history)

                    # Set the autosave session ID to continue this session
                    try:
                        from code_puppy.config import set_current_autosave_from_session_name
                        set_current_autosave_from_session_name(session_name)
                    except Exception:
                        pass

                # Display recent messages in UI
                self._display_resumed_history(history)

                # Update context display
                self._update_context_display()

                self.statusBar().showMessage(
                    f"Session resumed: {len(history)} messages"
                )

    def _display_resumed_history(self, history: list, max_messages: int = 20):
        """Display recent messages from loaded history in the UI.

        Args:
            history: The full message history
            max_messages: Maximum number of recent messages to display
        """
        if not history:
            return

        # Skip system message (first message) and get recent messages
        displayable = history[1:] if len(history) > 1 else []
        if not displayable:
            return

        # Take last N messages
        messages_to_show = displayable[-max_messages:] if len(displayable) > max_messages else displayable

        for msg in messages_to_show:
            try:
                self._add_history_message(msg)
            except Exception:
                continue  # Skip messages that fail to render

        # Scroll to bottom
        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, lambda: self.message_list.verticalScrollBar().setValue(
            self.message_list.verticalScrollBar().maximum()
        ))

    def _add_history_message(self, msg):
        """Add a single history message to the UI.

        Args:
            msg: A pydantic-ai message object from history
        """
        # Determine role and content from message parts
        part_kinds = [getattr(p, "part_kind", "unknown") for p in msg.parts]

        if msg.kind == "request":
            if all(pk == "tool-return" for pk in part_kinds):
                role = MessageRole.TOOL_OUTPUT
            else:
                role = MessageRole.USER
        else:
            if all(pk == "tool-call" for pk in part_kinds):
                role = MessageRole.TOOL_CALL
            elif any(pk == "thinking" for pk in part_kinds):
                role = MessageRole.THINKING
            else:
                role = MessageRole.ASSISTANT

        # Extract content
        content_parts = []
        metadata = {}

        for part in msg.parts:
            part_kind = getattr(part, "part_kind", "unknown")

            if part_kind == "tool-call":
                tool_name = getattr(part, "tool_name", "tool")
                args = getattr(part, "args", {})
                metadata["tool_name"] = tool_name
                content_parts.append(f"{tool_name}: {str(args)[:200]}")

            elif part_kind == "tool-return":
                tool_name = getattr(part, "tool_name", "tool")
                result = getattr(part, "content", "")
                metadata["tool_name"] = tool_name
                if isinstance(result, str):
                    content_parts.append(result[:500])

            elif part_kind == "thinking":
                content = getattr(part, "content", "")
                if isinstance(content, str):
                    content_parts.append(content)

            elif hasattr(part, "content"):
                content = part.content
                if isinstance(content, str) and content.strip():
                    content_parts.append(content)

        content = "\n".join(content_parts) if content_parts else "..."

        # Create and add message
        message = Message(role=role, content=content, metadata=metadata)
        self.message_list.message_model.add_message(message)

    # -------------------------------------------------------------------------
    # Agent event handlers
    # -------------------------------------------------------------------------

    def _on_token(self, token: str):
        """Handle streaming token from agent."""
        # Buffer tokens and start timer if not running
        self._token_buffer.append(token)
        if not self._token_timer.isActive():
            self._token_timer.start()

    def _flush_token_buffer(self):
        """Flush buffered tokens to UI."""
        if self._token_buffer:
            # Join all buffered tokens and update UI once
            combined = "".join(self._token_buffer)
            self._token_buffer.clear()

            # Create assistant message on first token
            if self._assistant_message_index is None:
                self._assistant_message_index = self.message_list.message_model.add_message(
                    Message(role=MessageRole.ASSISTANT, content=combined)
                )
            else:
                # Append to the specific assistant message, not just "last"
                self.message_list.message_model.append_to_message(
                    self._assistant_message_index, combined
                )

    def _on_thinking_started(self):
        """Handle thinking started event."""
        self.statusBar().showMessage("Thinking...")
        # Create thinking message
        self._current_thinking_index = self.message_list.message_model.add_message(
            Message(role=MessageRole.THINKING, content="")
        )

    def _on_thinking_content(self, content: str):
        """Handle thinking content delta."""
        if self._current_thinking_index is not None:
            self.message_list.message_model.append_to_message(
                self._current_thinking_index, content
            )

    def _on_thinking_complete(self):
        """Handle thinking complete event."""
        self.statusBar().showMessage("Responding...")
        self._current_thinking_index = None

    def _on_tool_call_started(self, tool_name: str, tool_args: str):
        """Handle tool call started event."""
        # Start activity indicator
        self._start_activity_indicator(tool_name)

        # Create tool call message
        index = self.message_list.message_model.add_message(
            Message(
                role=MessageRole.TOOL_CALL,
                content=tool_args or "(no arguments)",
                metadata={"tool_name": tool_name}
            )
        )
        self._current_tool_indices[tool_name] = index

    def _on_tool_call_args_delta(self, tool_name: str, args_delta: str):
        """Handle tool call args streaming."""
        if tool_name in self._current_tool_indices:
            msg = self.message_list.message_model.get_message(self._current_tool_indices[tool_name])
            if msg and msg.content == "(no arguments)":
                # Replace placeholder with actual args
                self.message_list.message_model.update_message_content(
                    self._current_tool_indices[tool_name], args_delta
                )
            else:
                self.message_list.message_model.append_to_message(
                    self._current_tool_indices[tool_name], args_delta
                )

    def _on_tool_call_complete(self, tool_name: str):
        """Handle tool call complete event."""
        # Stop activity indicator for this tool
        if self._current_tool_name == tool_name:
            self._stop_activity_indicator()

        self.statusBar().showMessage(f"Tool complete: {tool_name}")
        if tool_name in self._current_tool_indices:
            del self._current_tool_indices[tool_name]

    def _on_tool_output(self, tool_name: str, output_type: str, metadata: dict):
        """Handle tool output with structured data for rich rendering.

        Args:
            tool_name: Name of the tool that produced output
            output_type: Type of output (diff, shell, file_listing, grep, file_header)
            metadata: Structured data for rendering
        """
        self.statusBar().showMessage(f"Tool output: {tool_name}")

        # Add a TOOL_OUTPUT message with the structured metadata
        self.message_list.message_model.add_message(
            Message(
                role=MessageRole.TOOL_OUTPUT,
                content="",  # Content is in metadata
                metadata={
                    "tool_name": tool_name,
                    "output_type": output_type,
                    **metadata
                }
            )
        )

    def _on_response_complete(self, response: str):
        """Handle response completion."""
        # Stop activity indicator
        self._stop_activity_indicator()
        # Flush any remaining buffered tokens
        self._token_timer.stop()
        self._flush_token_buffer()

        # If no assistant message was created during streaming, create one now
        # This handles cases where streaming didn't work or response came all at once
        if self._assistant_message_index is None and response:
            self.message_list.message_model.add_message(
                Message(role=MessageRole.ASSISTANT, content=response)
            )

        # Clear tracked message indices
        self._current_thinking_index = None
        self._current_tool_indices.clear()
        self._assistant_message_index = None
        self.statusBar().showMessage("Ready")

    def _on_error(self, error: str):
        """Handle agent error."""
        # Stop activity indicator
        self._stop_activity_indicator()
        self.statusBar().showMessage(f"Error: {error[:50]}...")

        # Determine error type from message
        error_type = "Error"
        error_lower = error.lower()
        if "400" in error or "bad request" in error_lower:
            error_type = "API Error (400)"
        elif "401" in error or "unauthorized" in error_lower:
            error_type = "Auth Error (401)"
        elif "403" in error or "forbidden" in error_lower:
            error_type = "Access Denied (403)"
        elif "429" in error or "rate limit" in error_lower:
            error_type = "Rate Limited (429)"
        elif "500" in error or "502" in error or "503" in error or "504" in error:
            error_type = "Server Error"
        elif "timeout" in error_lower or "timed out" in error_lower:
            error_type = "Timeout"
        elif "connection" in error_lower:
            error_type = "Connection Error"

        # Create a dedicated error message
        self.message_list.message_model.add_message(
            Message(
                role=MessageRole.ERROR,
                content=error,
                metadata={"error_type": error_type}
            )
        )

    def _on_agent_busy(self, busy: bool):
        """Handle agent busy state change."""
        self.send_btn.setEnabled(not busy)
        self.attach_btn.setEnabled(not busy)
        self.cancel_btn.setVisible(busy)
        self.input_field.setEnabled(not busy)

        if busy:
            self.statusBar().showMessage("Processing...")
        else:
            self._stop_activity_indicator()
            self.statusBar().showMessage("Ready")
            self._update_status_bar_info()

    # -------------------------------------------------------------------------
    # Activity indicator
    # -------------------------------------------------------------------------

    def _start_activity_indicator(self, tool_name: str):
        """Start the activity indicator for a tool operation."""
        self._current_tool_name = tool_name
        self._activity_start_time = time.time()
        self._activity_frame = 0
        # Clear status message to avoid overlap
        self.statusBar().clearMessage()
        self._activity_label.setVisible(True)
        self._update_activity_indicator()
        self._activity_timer.start()

    def _stop_activity_indicator(self):
        """Stop the activity indicator."""
        self._activity_timer.stop()
        self._activity_label.setVisible(False)
        self._current_tool_name = ""

    def _update_activity_indicator(self):
        """Update the activity indicator display."""
        if not self._current_tool_name:
            return

        # Cycle through animation frames
        frame = self._activity_frames[self._activity_frame % len(self._activity_frames)]
        self._activity_frame += 1

        # Calculate elapsed time
        elapsed = time.time() - self._activity_start_time
        elapsed_str = f"{elapsed:.1f}s"

        # Update label with spinner, tool name, and elapsed time
        self._activity_label.setText(f"{frame} Calling {self._current_tool_name}... {elapsed_str}")

    # -------------------------------------------------------------------------
    # Status bar info
    # -------------------------------------------------------------------------

    def _update_status_bar_info(self):
        """Update all status bar info displays."""
        self._update_model_display()
        self._update_agent_display()
        self._update_context_display()

    def _update_model_display(self):
        """Update the model display in status bar."""
        agent = get_current_agent()

        # Get global model
        global_model = get_active_model() or "(default)"

        # Check if agent has a pinned model
        agent_model = None
        if agent and hasattr(agent, "get_model_name"):
            agent_model = agent.get_model_name()

        # Determine display
        if agent_model and agent_model != global_model:
            model_display = f"{global_model} → {agent_model}"
        else:
            model_display = agent_model or global_model

        self._model_label.setText(f"🤖 {model_display}")

    def _update_agent_display(self):
        """Update the agent display in status bar."""
        agent = get_current_agent()
        if agent:
            self._agent_label.setText(f"🐕 {agent.display_name}")
        else:
            self._agent_label.setText(f"🐕 {get_puppy_name()}")

    def _update_context_display(self):
        """Update the context info display in status bar."""
        agent = get_current_agent()
        if agent:
            messages = agent.get_message_history()
            msg_count = len(messages)

            # Estimate tokens used (messages + system prompt overhead)
            message_tokens = sum(agent.estimate_tokens_for_message(m) for m in messages)
            overhead_tokens = agent.estimate_context_overhead_tokens()
            total_tokens = message_tokens + overhead_tokens

            # Get context window size
            context_length = agent.get_model_context_length()

            # Calculate percentage
            usage_percent = (total_tokens / context_length * 100) if context_length > 0 else 0

            self._context_label.setText(
                f"💬 {msg_count} msgs | {total_tokens:,}/{context_length:,} ({usage_percent:.0f}%)"
            )
        else:
            self._context_label.setText("💬 0 msgs | 0/0 (0%)")

    # -------------------------------------------------------------------------
    # Theme refresh
    # -------------------------------------------------------------------------

    def _refresh_widget_styles(self):
        """Refresh widget styles after theme change."""
        colors = self._theme_manager.current

        # Refresh input area
        self.input_field.setStyleSheet(input_style())
        self.send_btn.setStyleSheet(get_send_button_style())
        self.cancel_btn.setStyleSheet(get_cancel_button_style())
        self.attach_btn.setStyleSheet(get_attach_button_style())

        # Refresh input container
        input_container = self.input_field.parent()
        if input_container:
            input_container.setStyleSheet(f"QWidget {{ background-color: {colors.bg_secondary}; }}")

        # Refresh status bar labels
        self._activity_label.setStyleSheet(f"color: {colors.accent_info}; padding: 0 8px; font-weight: bold;")
        self._model_label.setStyleSheet(f"color: {colors.accent_info}; padding: 0 8px;")
        self._agent_label.setStyleSheet(f"color: {colors.accent_success}; padding: 0 8px;")
        self._context_label.setStyleSheet(f"color: {colors.text_secondary}; padding: 0 8px;")

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    def closeEvent(self, event):
        """Clean up on close."""
        self._token_timer.stop()
        self._theme_manager.remove_listener(self._on_theme_changed)
        self.agent_bridge.cleanup()
        super().closeEvent(event)
