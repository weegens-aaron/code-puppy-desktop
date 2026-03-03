"""Agent selection panel for the sidebar."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QTextEdit, QFrame, QSplitter,
)
from PySide6.QtCore import Qt, Signal

from code_puppy.agents import (
    get_available_agents,
    get_agent_descriptions,
    get_current_agent,
    set_current_agent,
)
from styles import COLORS, button_style


class AgentsPanel(QWidget):
    """Panel for selecting the active agent."""

    agent_selected = Signal(str)  # Emits agent name when selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_agent = None
        self._setup_ui()
        self._load_agents()

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
                background-color: {COLORS.bg_secondary};
                color: {COLORS.text_primary};
                border: 1px solid {COLORS.border_subtle};
                border-radius: 4px;
                padding: 4px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 6px;
                border-radius: 4px;
                margin: 1px 0;
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
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header
        header = QHBoxLayout()
        title = QLabel("Agents")
        title.setStyleSheet(f"font-weight: bold; color: {COLORS.text_primary}; padding: 4px;")
        header.addWidget(title)
        header.addStretch()

        refresh_btn = QPushButton("\u21bb")
        refresh_btn.setFixedSize(28, 28)
        refresh_btn.setToolTip("Refresh agents")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-radius: 4px;
            }
        """)
        refresh_btn.clicked.connect(self._load_agents)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # Splitter for list and preview (vertical for sidebar)
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Agent list
        list_widget = QFrame()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(2)

        list_label = QLabel("Available")
        list_label.setStyleSheet(f"font-size: 11px; color: {COLORS.text_secondary};")
        list_layout.addWidget(list_label)

        self._agent_list = QListWidget()
        self._agent_list.currentItemChanged.connect(self._on_selection_changed)
        self._agent_list.itemDoubleClicked.connect(self._on_select)
        list_layout.addWidget(self._agent_list)

        splitter.addWidget(list_widget)

        # Agent details
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
        splitter.setSizes([200, 150])

        layout.addWidget(splitter)

        # Select button
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 4, 0, 0)

        self._select_btn = QPushButton("Select Agent")
        self._select_btn.setStyleSheet(button_style(
            bg_color=COLORS.accent_primary,
            text_color="white",
            hover_color=COLORS.accent_primary_hover,
        ))
        self._select_btn.clicked.connect(self._on_select)
        button_layout.addWidget(self._select_btn)

        layout.addLayout(button_layout)

    def _load_agents(self):
        """Load available agents into the list."""
        self._agent_list.clear()

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
                item.setText(f"\u2713 {display_name}")
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
            display_name = current.text().strip().lstrip("\u2713").strip()

            current_agent = get_current_agent()
            is_current = current_agent and current_agent.name == agent_name

            details = f"""<h3 style="color: {COLORS.accent_info}; margin: 0;">{display_name}</h3>
<p style="margin: 4px 0;"><b>Name:</b> {agent_name}</p>
<p style="margin: 4px 0;"><b>Status:</b> {"<span style='color: #4ade80;'>\u2713 Active</span>" if is_current else "Available"}</p>
<hr style="border-color: {COLORS.border_subtle};">
<p style="color: {COLORS.text_secondary}; margin: 4px 0;">{description}</p>
"""
            self._details_text.setHtml(details)
            self._selected_agent = agent_name

    def _on_select(self, item=None):
        """Handle select button click or double-click."""
        if not self._selected_agent:
            return

        current = get_current_agent()
        if current and current.name == self._selected_agent:
            # Already selected
            return

        # Switch agent
        set_current_agent(self._selected_agent)
        self._load_agents()  # Refresh to show new selection
        self.agent_selected.emit(self._selected_agent)

    def refresh(self):
        """Refresh the agent list."""
        self._load_agents()
