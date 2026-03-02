"""MCP server management dialog for the desktop application."""

import json
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QTextEdit, QFrame, QSplitter, QLineEdit,
    QComboBox, QFormLayout, QMessageBox, QGroupBox,
)
from PySide6.QtCore import Qt

from desktop.styles import COLORS, button_style
from code_puppy.mcp_.manager import get_mcp_manager, MCPManager
from code_puppy.mcp_.managed_server import ServerConfig, ServerState


# Example configurations for each server type
SERVER_EXAMPLES = {
    "stdio": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"],
        "env": {},
        "timeout": 30
    },
    "http": {
        "url": "http://localhost:8080/mcp",
        "headers": {},
        "timeout": 30
    },
    "sse": {
        "url": "http://localhost:8080/sse",
        "headers": {},
    },
}


class AddServerDialog(QDialog):
    """Dialog for adding a new MCP server."""

    def __init__(self, parent=None, edit_mode=False, existing_config: Optional[ServerConfig] = None):
        super().__init__(parent)
        self.setWindowTitle("Edit MCP Server" if edit_mode else "Add MCP Server")
        self.setMinimumSize(500, 400)
        self.edit_mode = edit_mode
        self.existing_config = existing_config
        self._setup_ui()
        self._apply_style()

        if existing_config:
            self._populate_from_config(existing_config)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Form
        form_group = QGroupBox("Server Configuration")
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(8)

        # Name
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("my-server")
        form_layout.addRow("Name:", self._name_input)

        # Type
        self._type_combo = QComboBox()
        self._type_combo.addItems(["stdio", "http", "sse"])
        self._type_combo.currentTextChanged.connect(self._on_type_changed)
        form_layout.addRow("Type:", self._type_combo)

        layout.addWidget(form_group)

        # JSON config
        config_group = QGroupBox("JSON Configuration")
        config_layout = QVBoxLayout(config_group)

        self._config_edit = QTextEdit()
        self._config_edit.setPlaceholderText("Enter JSON configuration...")
        self._config_edit.setMinimumHeight(150)
        config_layout.addWidget(self._config_edit)

        # Load example button
        example_btn = QPushButton("Load Example")
        example_btn.clicked.connect(self._load_example)
        config_layout.addWidget(example_btn)

        layout.addWidget(config_group)

        # Validation message
        self._validation_label = QLabel()
        self._validation_label.setStyleSheet(f"color: {COLORS.accent_error};")
        self._validation_label.setVisible(False)
        layout.addWidget(self._validation_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(button_style(
            bg_color=COLORS.bg_tertiary,
            text_color=COLORS.text_primary,
        ))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(button_style(
            bg_color=COLORS.accent_primary,
            text_color="white",
            hover_color=COLORS.accent_primary_hover,
        ))
        save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

        # Load initial example
        self._load_example()

    def _apply_style(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS.bg_primary};
                color: {COLORS.text_primary};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {COLORS.border_subtle};
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 12px;
                color: {COLORS.text_primary};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }}
            QLineEdit, QComboBox {{
                background-color: {COLORS.bg_secondary};
                color: {COLORS.text_primary};
                border: 1px solid {COLORS.border_default};
                border-radius: 4px;
                padding: 6px;
            }}
            QTextEdit {{
                background-color: {COLORS.bg_secondary};
                color: {COLORS.text_primary};
                border: 1px solid {COLORS.border_default};
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
            }}
            QLabel {{
                color: {COLORS.text_primary};
            }}
            QPushButton {{
                padding: 8px 16px;
                border-radius: 4px;
            }}
        """)

    def _populate_from_config(self, config: ServerConfig):
        """Populate form from existing config."""
        self._name_input.setText(config.name)
        self._name_input.setEnabled(False)  # Don't allow name change in edit mode

        index = self._type_combo.findText(config.type.lower())
        if index >= 0:
            self._type_combo.setCurrentIndex(index)

        # Format config as JSON
        self._config_edit.setText(json.dumps(config.config, indent=2))

    def _on_type_changed(self, server_type: str):
        """Handle type change - optionally update example."""
        pass  # Don't auto-update config when type changes in case user has edits

    def _load_example(self):
        """Load example config for current type."""
        server_type = self._type_combo.currentText()
        example = SERVER_EXAMPLES.get(server_type, {})
        self._config_edit.setText(json.dumps(example, indent=2))

    def _validate(self) -> bool:
        """Validate form inputs."""
        name = self._name_input.text().strip()
        if not name:
            self._show_error("Server name is required")
            return False

        if not name.replace("-", "").replace("_", "").isalnum():
            self._show_error("Name must be alphanumeric (hyphens/underscores allowed)")
            return False

        try:
            config = json.loads(self._config_edit.toPlainText())
        except json.JSONDecodeError as e:
            self._show_error(f"Invalid JSON: {e}")
            return False

        server_type = self._type_combo.currentText()
        if server_type == "stdio" and "command" not in config:
            self._show_error("stdio server requires 'command' field")
            return False
        if server_type in ("http", "sse") and "url" not in config:
            self._show_error(f"{server_type} server requires 'url' field")
            return False

        self._validation_label.setVisible(False)
        return True

    def _show_error(self, message: str):
        """Show validation error."""
        self._validation_label.setText(message)
        self._validation_label.setVisible(True)

    def _on_save(self):
        """Save the server configuration."""
        if not self._validate():
            return

        self.accept()

    def get_config(self) -> ServerConfig:
        """Get the server configuration from form."""
        name = self._name_input.text().strip()
        server_type = self._type_combo.currentText()
        config = json.loads(self._config_edit.toPlainText())

        # Use existing ID in edit mode
        server_id = self.existing_config.id if self.existing_config else ""

        return ServerConfig(
            id=server_id,
            name=name,
            type=server_type,
            enabled=True,
            config=config,
        )


class MCPDialog(QDialog):
    """Dialog for managing MCP servers."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MCP Servers")
        self.setMinimumSize(900, 600)
        self._manager: MCPManager = get_mcp_manager()
        self._setup_ui()
        self._load_servers()

    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setStyleSheet(f"""
            QDialog {{
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
                width: 2px;
            }}
            QListWidget {{
                background-color: {COLORS.bg_secondary};
                color: {COLORS.text_primary};
                border: 1px solid {COLORS.border_subtle};
                border-radius: 4px;
                padding: 4px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
                margin: 2px 0;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS.accent_primary};
                color: white;
            }}
            QListWidget::item:hover:!selected {{
                background-color: {COLORS.bg_tertiary};
            }}
            QTextEdit {{
                background-color: {COLORS.bg_secondary};
                color: {COLORS.text_primary};
                border: 1px solid {COLORS.border_subtle};
                border-radius: 4px;
                padding: 8px;
            }}
            QLabel {{
                color: {COLORS.text_primary};
                background-color: transparent;
            }}
            QPushButton {{
                padding: 8px 16px;
                border-radius: 4px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Top buttons
        top_layout = QHBoxLayout()

        add_btn = QPushButton("Add Server")
        add_btn.setStyleSheet(button_style(
            bg_color=COLORS.accent_success,
            text_color="white",
        ))
        add_btn.clicked.connect(self._on_add_server)
        top_layout.addWidget(add_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(button_style(
            bg_color=COLORS.bg_tertiary,
            text_color=COLORS.text_primary,
        ))
        refresh_btn.clicked.connect(self._load_servers)
        top_layout.addWidget(refresh_btn)

        top_layout.addStretch()

        layout.addLayout(top_layout)

        # Splitter for list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: Server list
        left_widget = QFrame()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        list_label = QLabel("Registered Servers")
        list_label.setStyleSheet(f"font-weight: bold; color: {COLORS.text_secondary};")
        left_layout.addWidget(list_label)

        self._server_list = QListWidget()
        self._server_list.currentItemChanged.connect(self._on_selection_changed)
        left_layout.addWidget(self._server_list)

        splitter.addWidget(left_widget)

        # Right side: Server details
        right_widget = QFrame()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        details_label = QLabel("Server Details")
        details_label.setStyleSheet(f"font-weight: bold; color: {COLORS.text_secondary};")
        right_layout.addWidget(details_label)

        self._details_text = QTextEdit()
        self._details_text.setReadOnly(True)
        right_layout.addWidget(self._details_text)

        splitter.addWidget(right_widget)
        splitter.setSizes([350, 550])

        layout.addWidget(splitter)

        # Action buttons
        button_layout = QHBoxLayout()

        # Start/Stop button
        self._start_btn = QPushButton("Start")
        self._start_btn.setStyleSheet(button_style(
            bg_color=COLORS.accent_success,
            text_color="white",
        ))
        self._start_btn.clicked.connect(self._on_start_server)
        button_layout.addWidget(self._start_btn)

        self._stop_btn = QPushButton("Stop")
        self._stop_btn.setStyleSheet(button_style(
            bg_color=COLORS.accent_warning,
            text_color="white",
        ))
        self._stop_btn.clicked.connect(self._on_stop_server)
        button_layout.addWidget(self._stop_btn)

        # Edit button
        self._edit_btn = QPushButton("Edit")
        self._edit_btn.setStyleSheet(button_style(
            bg_color=COLORS.bg_tertiary,
            text_color=COLORS.text_primary,
        ))
        self._edit_btn.clicked.connect(self._on_edit_server)
        button_layout.addWidget(self._edit_btn)

        # Remove button
        self._remove_btn = QPushButton("Remove")
        self._remove_btn.setStyleSheet(button_style(
            bg_color=COLORS.accent_error,
            text_color="white",
        ))
        self._remove_btn.clicked.connect(self._on_remove_server)
        button_layout.addWidget(self._remove_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(button_style(
            bg_color=COLORS.accent_primary,
            text_color="white",
            hover_color=COLORS.accent_primary_hover,
        ))
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _load_servers(self):
        """Load MCP servers into the list."""
        self._server_list.clear()

        try:
            servers = self._manager.list_servers()
        except Exception:
            servers = []

        if not servers:
            item = QListWidgetItem("No MCP servers registered")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            item.setForeground(Qt.GlobalColor.gray)
            self._server_list.addItem(item)
            self._details_text.setHtml(self._render_no_servers_help())
            return

        # Sort by name
        servers.sort(key=lambda s: s.name.lower())

        for server in servers:
            item = QListWidgetItem()

            # Format display with state indicator
            state = server.state
            if state == ServerState.RUNNING:
                icon = "🟢"
                color = Qt.GlobalColor.green
            elif state == ServerState.STOPPED:
                icon = "⚪"
                color = Qt.GlobalColor.gray
            elif state == ServerState.ERROR:
                icon = "🔴"
                color = Qt.GlobalColor.red
            elif state == ServerState.QUARANTINED:
                icon = "🟡"
                color = Qt.GlobalColor.yellow
            else:
                icon = "🔵"
                color = Qt.GlobalColor.cyan

            item.setText(f"{icon} {server.name} ({server.type.upper()})")
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
            return

        server = current.data(Qt.ItemDataRole.UserRole)
        if not server:
            return

        self._details_text.setHtml(self._render_server_details(server))
        self._update_buttons(server)

    def _update_buttons(self, server):
        """Update button states based on server."""
        is_running = server.state == ServerState.RUNNING
        self._start_btn.setEnabled(not is_running)
        self._stop_btn.setEnabled(is_running)

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
            <h3 style="color: {COLORS.accent_info}; margin-bottom: 8px;">
                {server.name}
            </h3>
            <p>
                <b>Type:</b> <span style="color: #60a5fa;">{server.type.upper()}</span>
            </p>
            <p>
                <b>State:</b>
                <span style="color: {state_color}; font-weight: bold;">{state.value}</span>
            </p>
            <p>
                <b>Enabled:</b>
                <span style="color: {'#4ade80' if server.enabled else '#f87171'};">
                    {'Yes' if server.enabled else 'No'}
                </span>
            </p>
        """

        if server.quarantined:
            html += f"""
            <p style="color: #fbbf24;">
                <b>Quarantined:</b> Yes
            </p>
            """

        if server.uptime_seconds:
            uptime = self._format_uptime(server.uptime_seconds)
            html += f"""
            <p>
                <b>Uptime:</b> {uptime}
            </p>
            """

        if server.error_message:
            html += f"""
            <p style="margin-top: 12px;">
                <b>Error:</b><br>
                <span style="color: #f87171;">{server.error_message}</span>
            </p>
            """

        if server.health:
            health_status = "Healthy" if server.health.get("is_healthy") else "Unhealthy"
            health_color = "#4ade80" if server.health.get("is_healthy") else "#f87171"
            html += f"""
            <p style="margin-top: 12px;">
                <b>Health:</b>
                <span style="color: {health_color};">{health_status}</span>
            </p>
            """

        # Show server ID
        html += f"""
        <p style="margin-top: 12px;">
            <b>ID:</b><br>
            <span style="color: {COLORS.text_muted}; font-size: 11px;">{server.id}</span>
        </p>
        """

        html += """
        <p style="margin-top: 16px; color: #a0a0a0; font-size: 12px;">
            Use Start/Stop to control the server. Edit to modify configuration.
        </p>
        </div>
        """

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
        <div style="font-family: 'Segoe UI', sans-serif; color: {COLORS.text_primary}; padding: 12px;">
            <h3 style="color: {COLORS.accent_warning};">No MCP Servers</h3>
            <p style="color: {COLORS.text_secondary};">
                MCP (Model Context Protocol) servers extend the agent's capabilities
                with external tools and data sources.
            </p>
            <p style="margin-top: 12px;"><b>Server Types:</b></p>
            <ul style="color: {COLORS.text_secondary};">
                <li><b>stdio</b> - Local command via stdin/stdout (npx, python, uvx)</li>
                <li><b>http</b> - HTTP endpoint implementing MCP protocol</li>
                <li><b>sse</b> - Server-Sent Events for real-time streaming</li>
            </ul>
            <p style="margin-top: 12px;">
                Click <b>Add Server</b> to configure a new MCP server.
            </p>
            <p style="margin-top: 8px; color: {COLORS.text_muted}; font-size: 12px;">
                Popular MCP servers: filesystem, github, postgres, sqlite, brave-search
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
            "Confirm Removal",
            f"Are you sure you want to remove '{server.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self._manager.remove_server(server.id)
                self._remove_from_config_file(server.name)
                self._load_servers()
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
            QMessageBox.warning(self, "Warning", f"Server registered but config file save failed: {e}")

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
            pass  # Silently ignore config file errors on removal
