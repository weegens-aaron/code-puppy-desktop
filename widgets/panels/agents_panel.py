"""Agent selection panel for the sidebar."""

from typing import Optional

from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtCore import Qt, Signal

from styles import COLORS
from widgets.panels.base_panel import BaseSidebarPanel, render_empty_state
from services.agent_service import AgentServiceProtocol, AgentService, get_agent_service


class AgentsPanel(BaseSidebarPanel):
    """Panel for selecting the active agent.

    Extends BaseSidebarPanel to reuse common UI structure (DRY).
    Uses dependency injection for agent service (DIP).
    """

    agent_selected = Signal(str)  # Emits agent name when selected

    def __init__(
        self,
        agent_service: Optional[AgentServiceProtocol] = None,
        parent=None
    ):
        """Initialize the agents panel.

        Args:
            agent_service: Service for agent operations. If None, uses default.
            parent: Parent widget.
        """
        self._agent_service = agent_service or get_agent_service()
        self._selected_agent: Optional[str] = None

        super().__init__(
            title="Agents",
            list_label="Available",
            details_label="Details",
            parent=parent,
        )
        self._load_items()

    def _get_action_buttons(self) -> list[dict]:
        """Define the Select Agent button."""
        return [
            {
                "label": "Select Agent",
                "callback": self._on_select,
                "variant": "primary",
                "size": "sm",
                "tooltip": "Switch to selected agent",
            }
        ]

    def _load_items(self):
        """Load available agents into the list."""
        self._item_list.clear()

        agents = self._agent_service.get_available_agents()

        if not agents:
            self._details_text.setHtml(render_empty_state(
                "No Agents",
                "No agents found.",
                "Check your agent configuration."
            ))
            return

        for agent in agents:
            item = QListWidgetItem()

            # Mark current agent
            if agent.is_current:
                item.setText(f"\u2713 {agent.display_name}")
                item.setForeground(Qt.GlobalColor.green)
            else:
                item.setText(f"  {agent.display_name}")

            item.setData(Qt.ItemDataRole.UserRole, agent.name)
            item.setData(Qt.ItemDataRole.UserRole + 1, agent.description)
            item.setData(Qt.ItemDataRole.UserRole + 2, agent.is_current)
            self._item_list.addItem(item)

            # Select current agent
            if agent.is_current:
                self._item_list.setCurrentItem(item)

    def _on_selection_changed(self, current, previous):
        """Handle selection change in agent list."""
        if not current:
            return

        agent_name = current.data(Qt.ItemDataRole.UserRole)
        description = current.data(Qt.ItemDataRole.UserRole + 1)
        is_current = current.data(Qt.ItemDataRole.UserRole + 2)
        display_name = current.text().strip().lstrip("\u2713").strip()

        details = f"""<h3 style="color: {COLORS.accent_info}; margin: 0;">{display_name}</h3>
<p style="margin: 4px 0;"><b>Name:</b> {agent_name}</p>
<p style="margin: 4px 0;"><b>Status:</b> {"<span style='color: #4ade80;'>\u2713 Active</span>" if is_current else "Available"}</p>
<hr style="border-color: {COLORS.border_subtle};">
<p style="color: {COLORS.text_secondary}; margin: 4px 0;">{description}</p>
"""
        self._details_text.setHtml(details)
        self._selected_agent = agent_name

    def _on_item_double_clicked(self, item):
        """Handle double-click to select agent."""
        self._on_select()

    def _on_select(self):
        """Handle select button click."""
        if not self._selected_agent:
            return

        # Check if already current
        current_name = self._agent_service.get_current_agent_name()
        if current_name == self._selected_agent:
            return

        # Switch agent
        if self._agent_service.set_current_agent(self._selected_agent):
            self._load_items()  # Refresh to show new selection
            self.agent_selected.emit(self._selected_agent)
