"""Tabbed chat interface for agent conversations."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QTabBar
from PySide6.QtCore import Signal

from widgets.message_list import MessageListView
from models.message_model import MessageModel
from services.agent_service import get_agent_service
from styles import get_theme_manager, get_chat_tab_style


class ChatTabWidget(QWidget):
    """Tabbed container for agent chat conversations.

    Each tab represents a conversation with an agent or subagent.
    The main tab shows the primary agent; subagent tabs are added dynamically.
    """

    # Emitted when the active tab changes
    tab_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._tabs: dict[str, MessageListView] = {}  # agent_id -> MessageListView

        self._setup_ui()
        self._apply_styles()

        # Theme listener
        self._theme_manager = get_theme_manager()
        self._theme_manager.add_listener(self._on_theme_changed)

        # Create initial tab for current agent
        self._create_main_agent_tab()

    def _setup_ui(self):
        """Set up the UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab widget
        self._tab_widget = QTabWidget()
        self._tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self._tab_widget.setDocumentMode(True)
        self._tab_widget.setTabsClosable(False)  # Main tab not closable
        self._tab_widget.currentChanged.connect(self._on_tab_changed)

        layout.addWidget(self._tab_widget)

    def _apply_styles(self):
        """Apply current theme styles to the tab widget."""
        self._tab_widget.setStyleSheet(get_chat_tab_style())

    def _on_theme_changed(self, theme):
        """Update styles when theme changes."""
        self._apply_styles()

    def _create_main_agent_tab(self):
        """Create the initial tab for the main agent."""
        agent_service = get_agent_service()
        agent_name = agent_service.get_current_agent_name() or "Agent"

        self.add_agent_tab("main", agent_name)

    def add_agent_tab(self, agent_id: str, display_name: str) -> MessageListView:
        """Add a new tab for an agent.

        Args:
            agent_id: Unique identifier for the agent (e.g., "main", "subagent_1")
            display_name: Display name shown on the tab

        Returns:
            The MessageListView for this tab
        """
        if agent_id in self._tabs:
            # Tab already exists, just switch to it
            index = self._get_tab_index(agent_id)
            if index >= 0:
                self._tab_widget.setCurrentIndex(index)
            return self._tabs[agent_id]

        # Create new message list for this tab
        message_list = MessageListView()
        self._tabs[agent_id] = message_list

        # Add to tab widget
        index = self._tab_widget.addTab(message_list, display_name)

        # Store agent_id in tab data
        self._tab_widget.tabBar().setTabData(index, agent_id)

        # Make subagent tabs closable (not the main one)
        if agent_id != "main":
            self._tab_widget.setTabsClosable(True)
            self._tab_widget.tabCloseRequested.connect(self._on_tab_close_requested)

        return message_list

    def remove_agent_tab(self, agent_id: str):
        """Remove a tab by agent ID. Cannot remove the main tab."""
        if agent_id == "main":
            return  # Cannot remove main tab

        index = self._get_tab_index(agent_id)
        if index >= 0:
            # Clean up the message list
            message_list = self._tabs.pop(agent_id, None)
            if message_list:
                message_list.cleanup()
            self._tab_widget.removeTab(index)

        # Hide close buttons if only main tab remains
        if self._tab_widget.count() <= 1:
            self._tab_widget.setTabsClosable(False)

    def update_main_tab_name(self, name: str):
        """Update the display name of the main agent tab."""
        index = self._get_tab_index("main")
        if index >= 0:
            self._tab_widget.setTabText(index, name)

    def _get_tab_index(self, agent_id: str) -> int:
        """Get the tab index for an agent ID."""
        for i in range(self._tab_widget.count()):
            if self._tab_widget.tabBar().tabData(i) == agent_id:
                return i
        return -1

    def _on_tab_changed(self, index: int):
        """Handle tab selection change."""
        self.tab_changed.emit(index)

    def _on_tab_close_requested(self, index: int):
        """Handle tab close button click."""
        agent_id = self._tab_widget.tabBar().tabData(index)
        if agent_id and agent_id != "main":
            self.remove_agent_tab(agent_id)

    @property
    def message_list(self) -> MessageListView:
        """Get the MessageListView for the currently active tab."""
        widget = self._tab_widget.currentWidget()
        if isinstance(widget, MessageListView):
            return widget
        # Fallback to main tab
        return self._tabs.get("main")

    @property
    def main_message_list(self) -> MessageListView:
        """Get the MessageListView for the main agent tab."""
        return self._tabs.get("main")

    @property
    def message_model(self) -> MessageModel:
        """Get the message model for the current tab."""
        return self.message_list.message_model

    def get_message_list(self, agent_id: str) -> MessageListView | None:
        """Get the MessageListView for a specific agent."""
        return self._tabs.get(agent_id)

    def get_message_model(self, agent_id: str) -> MessageModel | None:
        """Get the MessageModel for a specific agent."""
        message_list = self._tabs.get(agent_id)
        return message_list.message_model if message_list else None

    def switch_to_tab(self, agent_id: str):
        """Switch to a specific agent's tab."""
        index = self._get_tab_index(agent_id)
        if index >= 0:
            self._tab_widget.setCurrentIndex(index)

    def update_tab_name(self, agent_id: str, name: str):
        """Update the display name of a tab."""
        index = self._get_tab_index(agent_id)
        if index >= 0:
            self._tab_widget.setTabText(index, name)

    def has_tab(self, agent_id: str) -> bool:
        """Check if a tab exists for the given agent ID."""
        return agent_id in self._tabs

    def clear(self):
        """Clear messages in the current tab."""
        self.message_list.clear()

    def clear_all(self):
        """Clear messages in all tabs and remove subagent tabs."""
        # Clear all message lists
        for message_list in self._tabs.values():
            message_list.clear()

        # Remove all subagent tabs
        subagent_ids = [aid for aid in self._tabs.keys() if aid != "main"]
        for agent_id in subagent_ids:
            self.remove_agent_tab(agent_id)

    def cleanup(self):
        """Clean up resources before widget destruction."""
        # Remove theme listener
        try:
            self._theme_manager.remove_listener(self._on_theme_changed)
        except Exception:
            pass

        # Clean up all message lists
        for message_list in self._tabs.values():
            message_list.cleanup()
        self._tabs.clear()

    def closeEvent(self, event):
        """Clean up when widget is closed."""
        self.cleanup()
        super().closeEvent(event)
