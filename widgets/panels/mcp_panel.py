"""MCP server management panel for the sidebar."""

import json
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QTextEdit, QFrame, QSplitter, QMessageBox,
)
from PySide6.QtCore import Qt, Signal

from styles import COLORS, button_style
from code_puppy.mcp_.manager import get_mcp_manager, MCPManager
from code_puppy.mcp_.managed_server import ServerConfig, ServerState

# Import the AddServerDialog from the dialogs module
from windows.dialogs.mcp_dialog import AddServerDialog


class MCPPanel(QWidget):
    """Panel for managing MCP servers."""

    servers_changed = Signal()  # Emits when servers are modified

    def __init__(self, parent=None):
        super().__init__(parent)
        self._manager: MCPManager = get_mcp_manager()
        self._setup_ui()
        self._load_servers()

    def _setup_ui(self):
        """Set up the panel UI."""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS.bg_primary};
                color: {COLORS.text_primary};
            }}
            QFrame {{
                background-color: {COLORS.bg_primary};
                border: none;
            }}
            QSplitter {{
                background-color: {COLORS.bg_primary};
            }}
            QSplitter::handle {{
                background-color: {COLORS.border_subtle};
                height: 2px;
            }}
            QListWidget {{
                background-color: {COLORS.bg_primary};
                color: {COLORS.text_primary};
                border: none;
                padding: 0;
                outline: none;
            }}
            QListWidget::item {{
                padding: 6px;
                border: none;
                margin: 0;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS.accent_primary};
                color: white;
            }}
            QListWidget::item:hover:!selected {{
                background-color: {COLORS.bg_tertiary};
            }}
            QTextEdit {{
                background-color: {COLORS.bg_primary};
                color: {COLORS.text_primary};
                border: none;
                padding: 8px 0;
            }}
            QLabel {{
                color: {COLORS.text_primary};
                background-color: transparent;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header with add and refresh buttons
        header = QHBoxLayout()

        title = QLabel("MCP Servers")
        title.setStyleSheet(f"font-weight: bold; color: {COLORS.text_primary}; padding: 4px;")
        header.addWidget(title)

        header.addStretch()

        add_btn = QPushButton("+")
        add_btn.setFixedSize(28, 28)
        add_btn.setToolTip("Add server")
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS.accent_success};
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #3fb950;
            }}
        """)
        add_btn.clicked.connect(self._on_add_server)
        header.addWidget(add_btn)

        layout.addLayout(header)

        # Splitter for list and details (vertical for sidebar)
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Server list
        list_widget = QFrame()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(2)

        list_label = QLabel("Registered")
        list_label.setStyleSheet(f"font-size: 11px; color: {COLORS.text_secondary};")
        list_layout.addWidget(list_label)

        self._server_list = QListWidget()
        self._server_list.currentItemChanged.connect(self._on_selection_changed)
        list_layout.addWidget(self._server_list)

        splitter.addWidget(list_widget)

        # Server details
        details_widget = QFrame()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(2)

        details_label = QLabel("Details")
        details_label.setStyleSheet(f"font-size: 11px; color: {COLORS.text_secondary};")
        details_layout.addWidget(details_label)

        self._details_text = QTextEdit()
        self._details_text.setReadOnly(True)
        details_layout.addWidget(self._details_text)

        splitter.addWidget(details_widget)
        splitter.setSizes([180, 120])

        layout.addWidget(splitter)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 4, 0, 0)
        button_layout.setSpacing(4)

        self._start_btn = QPushButton("\u25b6")
        self._start_btn.setFixedSize(32, 28)
        self._start_btn.setToolTip("Start server")
        self._start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS.accent_success};
                color: white;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #3fb950;
            }}
            QPushButton:disabled {{
                background-color: {COLORS.bg_tertiary};
                color: {COLORS.text_muted};
            }}
        """)
        self._start_btn.clicked.connect(self._on_start_server)
        button_layout.addWidget(self._start_btn)

        self._stop_btn = QPushButton("\u25a0")
        self._stop_btn.setFixedSize(32, 28)
        self._stop_btn.setToolTip("Stop server")
        self._stop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS.accent_warning};
                color: white;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #e5a00d;
            }}
            QPushButton:disabled {{
                background-color: {COLORS.bg_tertiary};
                color: {COLORS.text_muted};
            }}
        """)
        self._stop_btn.clicked.connect(self._on_stop_server)
        button_layout.addWidget(self._stop_btn)

        self._edit_btn = QPushButton("\u270e")
        self._edit_btn.setFixedSize(32, 28)
        self._edit_btn.setToolTip("Edit server")
        self._edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS.bg_tertiary};
                color: {COLORS.text_primary};
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #4d4d4d;
            }}
        """)
        self._edit_btn.clicked.connect(self._on_edit_server)
        button_layout.addWidget(self._edit_btn)

        self._remove_btn = QPushButton("\u2715")
        self._remove_btn.setFixedSize(32, 28)
        self._remove_btn.setToolTip("Remove server")
        self._remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS.accent_error};
                color: white;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #dc2626;
            }}
        """)
        self._remove_btn.clicked.connect(self._on_remove_server)
        button_layout.addWidget(self._remove_btn)

        button_layout.addStretch()

        layout.addLayout(button_layout)

    def _load_servers(self):
        """Load MCP servers into the list."""
        self._server_list.clear()

        try:
            servers = self._manager.list_servers()
        except Exception:
            servers = []

        if not servers:
            item = QListWidgetItem("No servers")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            item.setForeground(Qt.GlobalColor.gray)
            self._server_list.addItem(item)
            self._details_text.setHtml(self._render_no_servers_help())
            self._update_buttons(None)
            return

        # Sort by name
        servers.sort(key=lambda s: s.name.lower())

        for server in servers:
            item = QListWidgetItem()

            # Format display with state indicator
            state = server.state
            if state == ServerState.RUNNING:
                icon = "\U0001f7e2"
                color = Qt.GlobalColor.green
            elif state == ServerState.STOPPED:
                icon = "\u26aa"
                color = Qt.GlobalColor.gray
            elif state == ServerState.ERROR:
                icon = "\U0001f534"
                color = Qt.GlobalColor.red
            elif state == ServerState.QUARANTINED:
                icon = "\U0001f7e1"
                color = Qt.GlobalColor.yellow
            else:
                icon = "\U0001f535"
                color = Qt.GlobalColor.cyan

            item.setText(f"{icon} {server.name}")
            item.setForeground(color)

            # Store server info
            item.setData(Qt.ItemDataRole.UserRole, server)
            self._server_list.addItem(item)

        # Select first
        if self._server_list.count() > 0:
            self._server_list.setCurrentRow(0)

    def _on_selection_changed(self, current, previous):
        """Handle selection change in server list."""
        if not current:
            self._update_buttons(None)
            return

        server = current.data(Qt.ItemDataRole.UserRole)
        if not server:
            self._update_buttons(None)
            return

        self._details_text.setHtml(self._render_server_details(server))
        self._update_buttons(server)

    def _update_buttons(self, server):
        """Update button states based on server."""
        if server is None:
            self._start_btn.setEnabled(False)
            self._stop_btn.setEnabled(False)
            self._edit_btn.setEnabled(False)
            self._remove_btn.setEnabled(False)
            return

        is_running = server.state == ServerState.RUNNING
        self._start_btn.setEnabled(not is_running)
        self._stop_btn.setEnabled(is_running)
        self._edit_btn.setEnabled(True)
        self._remove_btn.setEnabled(True)

    def _render_server_details(self, server) -> str:
        """Render server details as HTML."""
        state = server.state
        state_colors = {
            ServerState.RUNNING: "#4ade80",
            ServerState.STOPPED: "#a0a0a0",
            ServerState.ERROR: "#f87171",
            ServerState.QUARANTINED: "#fbbf24",
            ServerState.STARTING: "#60a5fa",
            ServerState.STOPPING: "#fbbf24",
        }
        state_color = state_colors.get(state, "#a0a0a0")

        html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; color: {COLORS.text_primary};">
            <h3 style="color: {COLORS.accent_info}; margin: 0 0 8px 0; font-size: 14px;">
                {server.name}
            </h3>
            <p style="margin: 4px 0;">
                <b>Type:</b> {server.type.upper()}
            </p>
            <p style="margin: 4px 0;">
                <b>State:</b>
                <span style="color: {state_color};">{state.value}</span>
            </p>
        """

        if server.error_message:
            html += f"""
            <p style="margin: 8px 0; color: #f87171; font-size: 11px;">
                Error: {server.error_message[:100]}
            </p>
            """

        if server.uptime_seconds:
            uptime = self._format_uptime(server.uptime_seconds)
            html += f"""
            <p style="margin: 4px 0; font-size: 11px;">
                <b>Uptime:</b> {uptime}
            </p>
            """

        html += "</div>"
        return html

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable form."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"

    def _render_no_servers_help(self) -> str:
        """Render help text when no servers are registered."""
        return f"""
        <div style="font-family: 'Segoe UI', sans-serif; color: {COLORS.text_primary}; padding: 8px;">
            <h3 style="color: {COLORS.accent_warning}; font-size: 14px;">No MCP Servers</h3>
            <p style="color: {COLORS.text_secondary}; font-size: 12px;">
                Click + to add a server.
            </p>
            <p style="color: {COLORS.text_muted}; font-size: 11px; margin-top: 8px;">
                Types: stdio, http, sse
            </p>
        </div>
        """

    def _on_add_server(self):
        """Handle add server button."""
        dialog = AddServerDialog(self)
        if dialog.exec():
            config = dialog.get_config()
            try:
                self._manager.register_server(config)
                self._save_to_config_file(config)
                self._load_servers()
                self.servers_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add server: {e}")

    def _on_edit_server(self):
        """Handle edit server button."""
        current = self._server_list.currentItem()
        if not current:
            return

        server_info = current.data(Qt.ItemDataRole.UserRole)
        if not server_info:
            return

        # Get full config from registry
        config = self._manager.registry.get(server_info.id)
        if not config:
            QMessageBox.warning(self, "Error", "Could not load server configuration")
            return

        dialog = AddServerDialog(self, edit_mode=True, existing_config=config)
        if dialog.exec():
            new_config = dialog.get_config()
            try:
                self._manager.update_server(server_info.id, new_config)
                self._save_to_config_file(new_config)
                self._load_servers()
                self.servers_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update server: {e}")

    def _on_remove_server(self):
        """Handle remove server button."""
        current = self._server_list.currentItem()
        if not current:
            return

        server = current.data(Qt.ItemDataRole.UserRole)
        if not server:
            return

        reply = QMessageBox.question(
            self,
            "Confirm",
            f"Remove '{server.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self._manager.remove_server(server.id)
                self._remove_from_config_file(server.name)
                self._load_servers()
                self.servers_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to remove server: {e}")

    def _on_start_server(self):
        """Handle start server button."""
        current = self._server_list.currentItem()
        if not current:
            return

        server = current.data(Qt.ItemDataRole.UserRole)
        if not server:
            return

        try:
            self._manager.start_server_sync(server.id)
            self._load_servers()
            self.servers_changed.emit()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start server: {e}")

    def _on_stop_server(self):
        """Handle stop server button."""
        current = self._server_list.currentItem()
        if not current:
            return

        server = current.data(Qt.ItemDataRole.UserRole)
        if not server:
            return

        try:
            self._manager.stop_server_sync(server.id)
            self._load_servers()
            self.servers_changed.emit()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop server: {e}")

    def _save_to_config_file(self, config: ServerConfig):
        """Save server to mcp_servers.json for persistence."""
        import os
        from code_puppy.config import MCP_SERVERS_FILE

        try:
            if os.path.exists(MCP_SERVERS_FILE):
                with open(MCP_SERVERS_FILE, "r") as f:
                    data = json.load(f)
                    servers = data.get("mcp_servers", {})
            else:
                servers = {}
                data = {"mcp_servers": servers}

            # Add/update server with type
            save_config = config.config.copy()
            save_config["type"] = config.type
            servers[config.name] = save_config

            # Save back
            os.makedirs(os.path.dirname(MCP_SERVERS_FILE), exist_ok=True)
            with open(MCP_SERVERS_FILE, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Config save failed: {e}")

    def _remove_from_config_file(self, server_name: str):
        """Remove server from mcp_servers.json."""
        import os
        from code_puppy.config import MCP_SERVERS_FILE

        try:
            if not os.path.exists(MCP_SERVERS_FILE):
                return

            with open(MCP_SERVERS_FILE, "r") as f:
                data = json.load(f)

            servers = data.get("mcp_servers", {})
            if server_name in servers:
                del servers[server_name]

            with open(MCP_SERVERS_FILE, "w") as f:
                json.dump(data, f, indent=2)

        except Exception:
            pass

    def refresh(self):
        """Refresh the server list."""
        self._load_servers()
