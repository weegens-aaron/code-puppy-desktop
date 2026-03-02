"""Agent selection dialog for the desktop application."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QTextEdit, QFrame, QSplitter,
)
from PySide6.QtCore import Qt

from code_puppy.agents import (
    get_available_agents,
    get_agent_descriptions,
    get_current_agent,
    set_current_agent,
)
from desktop.styles import COLORS, button_style


class AgentDialog(QDialog):
    """Dialog for selecting the active agent."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Agent")
        self.setMinimumSize(700, 500)
        self._selected_agent = None
        self._setup_ui()
        self._load_agents()

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

        # Left side: Agent list
        left_widget = QFrame()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        list_label = QLabel("Available Agents")
        list_label.setStyleSheet(f"font-weight: bold; color: {COLORS.text_secondary};")
        left_layout.addWidget(list_label)

        self._agent_list = QListWidget()
        self._agent_list.currentItemChanged.connect(self._on_selection_changed)
        self._agent_list.itemDoubleClicked.connect(self._on_double_click)
        left_layout.addWidget(self._agent_list)

        splitter.addWidget(left_widget)

        # Right side: Agent details
        right_widget = QFrame()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        details_label = QLabel("Agent Details")
        details_label.setStyleSheet(f"font-weight: bold; color: {COLORS.text_secondary};")
        right_layout.addWidget(details_label)

        self._details_text = QTextEdit()
        self._details_text.setReadOnly(True)
        right_layout.addWidget(self._details_text)

        splitter.addWidget(right_widget)
        splitter.setSizes([250, 450])

        layout.addWidget(splitter)

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

        select_btn = QPushButton("Select Agent")
        select_btn.setStyleSheet(button_style(
            bg_color=COLORS.accent_primary,
            text_color="white",
            hover_color=COLORS.accent_primary_hover,
        ))
        select_btn.clicked.connect(self._on_select)
        self._select_btn = select_btn
        button_layout.addWidget(select_btn)

        layout.addLayout(button_layout)

    def _load_agents(self):
        """Load available agents into the list."""
        available = get_available_agents()
        descriptions = get_agent_descriptions()
        current = get_current_agent()
        current_name = current.name if current else ""

        # Sort by name
        sorted_agents = sorted(available.items(), key=lambda x: x[0].lower())

        for agent_name, display_name in sorted_agents:
            item = QListWidgetItem()

            # Mark current agent
            if agent_name == current_name:
                item.setText(f"✓ {display_name}")
                item.setForeground(Qt.GlobalColor.green)
            else:
                item.setText(f"  {display_name}")

            item.setData(Qt.ItemDataRole.UserRole, agent_name)
            item.setData(Qt.ItemDataRole.UserRole + 1, descriptions.get(agent_name, "No description"))
            self._agent_list.addItem(item)

            # Select current agent
            if agent_name == current_name:
                self._agent_list.setCurrentItem(item)

    def _on_selection_changed(self, current, previous):
        """Handle selection change in agent list."""
        if current:
            agent_name = current.data(Qt.ItemDataRole.UserRole)
            description = current.data(Qt.ItemDataRole.UserRole + 1)
            display_name = current.text().strip().lstrip("✓").strip()

            current_agent = get_current_agent()
            is_current = current_agent and current_agent.name == agent_name

            details = f"""<h3 style="color: {COLORS.accent_info};">{display_name}</h3>
<p><b>Name:</b> {agent_name}</p>
<p><b>Status:</b> {"<span style='color: #4ade80;'>✓ Currently Active</span>" if is_current else "Not active"}</p>
<hr>
<p><b>Description:</b></p>
<p style="color: {COLORS.text_secondary};">{description}</p>
"""
            self._details_text.setHtml(details)
            self._selected_agent = agent_name

    def _on_double_click(self, item):
        """Handle double-click to select agent."""
        self._on_select()

    def _on_select(self):
        """Handle select button click."""
        if self._selected_agent:
            current = get_current_agent()
            if current and current.name == self._selected_agent:
                # Already selected, just close
                self.accept()
                return

            # Switch agent
            set_current_agent(self._selected_agent)
            self.accept()

    def get_selected_agent(self) -> str | None:
        """Get the selected agent name."""
        return self._selected_agent
