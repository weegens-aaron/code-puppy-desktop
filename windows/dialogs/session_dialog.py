"""Session management dialog for the desktop application."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QTextEdit, QFrame, QSplitter, QMessageBox,
)
from PySide6.QtCore import Qt, Signal

from styles import COLORS, action_button
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


class SessionDialog(QDialog):
    """Dialog for managing and loading sessions."""

    session_loaded = Signal(str)  # Emits session name when loaded

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resume Session")
        self.setMinimumSize(800, 550)
        self._base_dir = Path(AUTOSAVE_DIR)
        self._entries: list[tuple[str, dict]] = []
        self._selected_session: Optional[str] = None
        self._loaded_history: Optional[list] = None
        self._setup_ui()
        self._load_sessions()

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

        # Splitter for list and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: Session list
        left_widget = QFrame()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        list_label = QLabel("Recent Sessions")
        list_label.setStyleSheet(f"font-weight: bold; color: {COLORS.text_secondary};")
        left_layout.addWidget(list_label)

        self._session_list = QListWidget()
        self._session_list.currentItemChanged.connect(self._on_selection_changed)
        self._session_list.itemDoubleClicked.connect(self._on_load)
        left_layout.addWidget(self._session_list)

        splitter.addWidget(left_widget)

        # Right side: Session preview
        right_widget = QFrame()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        preview_label = QLabel("Session Preview")
        preview_label.setStyleSheet(f"font-weight: bold; color: {COLORS.text_secondary};")
        right_layout.addWidget(preview_label)

        self._preview_text = QTextEdit()
        self._preview_text.setReadOnly(True)
        right_layout.addWidget(self._preview_text)

        splitter.addWidget(right_widget)
        splitter.setSizes([300, 500])

        layout.addWidget(splitter)

        # Buttons
        button_layout = QHBoxLayout()

        # New session button
        new_btn = QPushButton("New Session")
        new_btn.setStyleSheet(action_button("warning", "sm"))
        new_btn.clicked.connect(self._on_new_session)
        button_layout.addWidget(new_btn)

        # Load button
        self._load_btn = QPushButton("Load Session")
        self._load_btn.setStyleSheet(action_button("success", "sm"))
        self._load_btn.clicked.connect(self._on_load)
        button_layout.addWidget(self._load_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Cancel")
        close_btn.setStyleSheet(action_button("neutral", "sm"))
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)

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

        for session_name, metadata in self._entries:
            item = QListWidgetItem()

            # Format timestamp
            timestamp = metadata.get("timestamp", "unknown")
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                time_str = "unknown"

            # Format message count
            msg_count = metadata.get("message_count", "?")
            tokens = metadata.get("total_tokens", 0)

            # Display format
            item.setText(f"{time_str}  ({msg_count} msgs, {tokens:,} tokens)")

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
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            time_str = timestamp

        msg_count = metadata.get("message_count", 0)
        tokens = metadata.get("total_tokens", 0)

        html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; color: {COLORS.text_primary};">
            <h3 style="color: {COLORS.accent_info}; margin-bottom: 8px;">
                Session Details
            </h3>
            <p>
                <b>Saved:</b> <span style="color: {COLORS.text_secondary};">{time_str}</span>
            </p>
            <p>
                <b>Messages:</b> <span style="color: #60a5fa;">{msg_count}</span>
            </p>
            <p>
                <b>Tokens:</b> <span style="color: #fbbf24;">{tokens:,}</span>
            </p>
            <p style="margin-top: 12px;">
                <b>Session ID:</b><br>
                <span style="color: {COLORS.text_muted}; font-size: 11px;">{session_name}</span>
            </p>
        """

        # Try to load and preview the last message
        try:
            history = load_session(session_name, self._base_dir)
            self._loaded_history = history
            last_message = _extract_last_user_message(history)

            # Truncate long messages
            if len(last_message) > 500:
                last_message = last_message[:500] + "..."

            # Escape HTML
            last_message = (last_message
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\n", "<br>"))

            html += f"""
            <p style="margin-top: 16px;">
                <b>Last User Message:</b>
            </p>
            <div style="background-color: {COLORS.bg_tertiary}; padding: 12px;
                        border-radius: 4px; margin-top: 8px;">
                <span style="color: {COLORS.text_secondary}; font-size: 13px;">
                    {last_message}
                </span>
            </div>
            """
        except Exception as e:
            html += f"""
            <p style="margin-top: 12px; color: {COLORS.accent_error};">
                Error loading preview: {e}
            </p>
            """

        html += """
        <p style="margin-top: 16px; color: #a0a0a0; font-size: 12px;">
            Double-click or press Load to resume this session.
        </p>
        </div>
        """

        return html

    def _render_no_sessions_help(self) -> str:
        """Render help text when no sessions are found."""
        return f"""
        <div style="font-family: 'Segoe UI', sans-serif; color: {COLORS.text_primary}; padding: 12px;">
            <h3 style="color: {COLORS.accent_warning};">No Sessions Found</h3>
            <p style="color: {COLORS.text_secondary};">
                No autosaved sessions were found. Sessions are automatically
                saved as you chat with the agent.
            </p>
            <p style="margin-top: 12px;">
                Start a new conversation and it will be automatically saved
                for you to resume later.
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
            self.session_loaded.emit(self._selected_session)
            self.accept()

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
                self.session_loaded.emit("__NEW__")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create new session: {e}")

    def get_loaded_history(self) -> Optional[list]:
        """Get the loaded message history."""
        return self._loaded_history

    def get_selected_session(self) -> Optional[str]:
        """Get the selected session name."""
        return self._selected_session
