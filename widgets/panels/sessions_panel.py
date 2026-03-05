"""Session management panel for the sidebar."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QTextEdit, QFrame, QSplitter, QMessageBox,
)
from PySide6.QtCore import Qt, Signal

from styles import COLORS, button_style
from code_puppy.config import AUTOSAVE_DIR, rotate_autosave_id
from code_puppy.session_storage import list_sessions, load_session


def _get_session_metadata(base_dir: Path, session_name: str) -> dict:
    """Load metadata for a session."""
    meta_path = base_dir / f"{session_name}_meta.json"
    try:
        with meta_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _get_session_entries(base_dir: Path) -> list[tuple[str, dict]]:
    """Get all sessions with their metadata, sorted by timestamp."""
    try:
        sessions = list_sessions(base_dir)
    except (FileNotFoundError, PermissionError):
        return []

    entries = []
    for name in sessions:
        try:
            metadata = _get_session_metadata(base_dir, name)
        except (FileNotFoundError, PermissionError):
            metadata = {}
        entries.append((name, metadata))

    # Sort by timestamp (most recent first)
    def sort_key(entry):
        _, metadata = entry
        timestamp = metadata.get("timestamp")
        if timestamp:
            try:
                return datetime.fromisoformat(timestamp)
            except ValueError:
                return datetime.min
        return datetime.min

    entries.sort(key=sort_key, reverse=True)
    return entries


def _extract_last_user_message(history: list) -> str:
    """Extract the most recent user message from history."""
    for msg in reversed(history):
        content_parts = []
        for part in msg.parts:
            if hasattr(part, "content"):
                content = part.content
                if isinstance(content, str) and content.strip():
                    content_parts.append(content)
        if content_parts:
            return "\n\n".join(content_parts)
    return "[No messages found]"


class SessionsPanel(QWidget):
    """Panel for managing and loading sessions."""

    session_selected = Signal(str)  # Emits session name when loaded, "__NEW__" for new session

    def __init__(self, parent=None):
        super().__init__(parent)
        self._base_dir = Path(AUTOSAVE_DIR)
        self._entries: list[tuple[str, dict]] = []
        self._selected_session: Optional[str] = None
        self._loaded_history: Optional[list] = None
        self._setup_ui()
        self._load_sessions()

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

        # Header
        header = QHBoxLayout()
        title = QLabel("Sessions")
        title.setStyleSheet(f"font-weight: bold; color: {COLORS.text_primary}; padding: 4px;")
        header.addWidget(title)
        header.addStretch()

        layout.addLayout(header)

        # Splitter for list and preview (vertical for sidebar)
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Session list
        list_widget = QFrame()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(2)

        list_label = QLabel("Recent")
        list_label.setStyleSheet(f"font-size: 11px; color: {COLORS.text_secondary};")
        list_layout.addWidget(list_label)

        self._session_list = QListWidget()
        self._session_list.currentItemChanged.connect(self._on_selection_changed)
        self._session_list.itemDoubleClicked.connect(self._on_load)
        list_layout.addWidget(self._session_list)

        splitter.addWidget(list_widget)

        # Session preview
        preview_widget = QFrame()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(2)

        preview_label = QLabel("Preview")
        preview_label.setStyleSheet(f"font-size: 11px; color: {COLORS.text_secondary};")
        preview_layout.addWidget(preview_label)

        self._preview_text = QTextEdit()
        self._preview_text.setReadOnly(True)
        preview_layout.addWidget(self._preview_text)

        splitter.addWidget(preview_widget)
        splitter.setSizes([200, 150])

        layout.addWidget(splitter)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 4, 0, 0)

        # New session button
        self._new_btn = QPushButton("New")
        self._new_btn.setStyleSheet(button_style(
            bg_color=COLORS.accent_warning,
            text_color="white",
        ))
        self._new_btn.setToolTip("Start a new session")
        self._new_btn.clicked.connect(self._on_new_session)
        button_layout.addWidget(self._new_btn)

        # Load button
        self._load_btn = QPushButton("Resume")
        self._load_btn.setStyleSheet(button_style(
            bg_color=COLORS.accent_success,
            text_color="white",
        ))
        self._load_btn.setToolTip("Resume selected session")
        self._load_btn.clicked.connect(self._on_load)
        button_layout.addWidget(self._load_btn)

        layout.addLayout(button_layout)

    def _load_sessions(self):
        """Load available sessions into the list."""
        self._session_list.clear()
        self._entries = _get_session_entries(self._base_dir)

        if not self._entries:
            item = QListWidgetItem("No sessions found")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            item.setForeground(Qt.GlobalColor.gray)
            self._session_list.addItem(item)
            self._preview_text.setHtml(self._render_no_sessions_help())
            self._load_btn.setEnabled(False)
            return

        self._load_btn.setEnabled(True)

        for session_name, metadata in self._entries:
            item = QListWidgetItem()

            # Format timestamp
            timestamp = metadata.get("timestamp", "unknown")
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%m/%d %H:%M")
            except Exception:
                time_str = "unknown"

            # Format message count
            msg_count = metadata.get("message_count", "?")

            # Compact display format for sidebar
            item.setText(f"{time_str} ({msg_count} msgs)")

            # Store data
            item.setData(Qt.ItemDataRole.UserRole, session_name)
            item.setData(Qt.ItemDataRole.UserRole + 1, metadata)
            self._session_list.addItem(item)

        # Select first
        if self._session_list.count() > 0:
            self._session_list.setCurrentRow(0)

    def _on_selection_changed(self, current, previous):
        """Handle selection change in session list."""
        if not current:
            return

        session_name = current.data(Qt.ItemDataRole.UserRole)
        metadata = current.data(Qt.ItemDataRole.UserRole + 1)

        if not session_name:
            return

        self._selected_session = session_name
        self._preview_text.setHtml(self._render_session_preview(session_name, metadata))

    def _render_session_preview(self, session_name: str, metadata: dict) -> str:
        """Render session preview as HTML."""
        # Format timestamp
        timestamp = metadata.get("timestamp", "unknown")
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            time_str = timestamp

        msg_count = metadata.get("message_count", 0)
        tokens = metadata.get("total_tokens", 0)

        html = f"""
        <div style="font-family: sans-serif; color: {COLORS.text_primary};">
            <p style="margin: 2px 0;"><b>Saved:</b> {time_str}</p>
            <p style="margin: 2px 0;"><b>Messages:</b> {msg_count}</p>
            <p style="margin: 2px 0;"><b>Tokens:</b> {tokens:,}</p>
        """

        # Try to load and preview the last message
        try:
            history = load_session(session_name, self._base_dir)
            self._loaded_history = history
            last_message = _extract_last_user_message(history)

            # Truncate for sidebar
            if len(last_message) > 200:
                last_message = last_message[:200] + "..."

            # Escape HTML
            last_message = (last_message
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\n", "<br>"))

            html += f"""
            <p style="margin-top: 8px; margin-bottom: 2px;"><b>Last message:</b></p>
            <div style="background-color: {COLORS.bg_tertiary}; padding: 6px;
                        border-radius: 4px; font-size: 11px;">
                {last_message}
            </div>
            """
        except Exception as e:
            html += f"""
            <p style="color: {COLORS.accent_error}; font-size: 11px;">
                Error: {e}
            </p>
            """

        html += "</div>"
        return html

    def _render_no_sessions_help(self) -> str:
        """Render help text when no sessions are found."""
        return f"""
        <div style="font-family: sans-serif; color: {COLORS.text_primary}; padding: 4px;">
            <p style="color: {COLORS.text_secondary}; font-size: 12px;">
                No saved sessions found. Sessions are automatically saved as you chat.
            </p>
        </div>
        """

    def _on_load(self, item=None):
        """Load the selected session."""
        if not self._selected_session:
            return

        try:
            # Load the session if not already loaded
            if self._loaded_history is None:
                self._loaded_history = load_session(self._selected_session, self._base_dir)

            # Emit signal with session name
            self.session_selected.emit(self._selected_session)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load session: {e}")

    def _on_new_session(self):
        """Start a new session."""
        reply = QMessageBox.question(
            self,
            "New Session",
            "This will clear the current conversation and start fresh.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Rotate to a new session ID
                rotate_autosave_id()
                self._selected_session = None
                self._loaded_history = None
                self.session_selected.emit("__NEW__")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create new session: {e}")

    def get_loaded_history(self) -> Optional[list]:
        """Get the loaded message history."""
        return self._loaded_history

    def get_selected_session(self) -> Optional[str]:
        """Get the selected session name."""
        return self._selected_session

    def refresh(self):
        """Refresh the session list."""
        self._load_sessions()
