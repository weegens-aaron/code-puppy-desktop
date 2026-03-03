"""Tabbed sidebar widget containing file tree and configuration panels."""

import os
from typing import Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import Signal

from widgets.file_tree import FileTree
from widgets.panels.agents_panel import AgentsPanel
from widgets.panels.models_panel import ModelsPanel
from widgets.panels.skills_panel import SkillsPanel
from widgets.panels.mcp_panel import MCPPanel
from styles import COLORS


class SidebarTabs(QWidget):
    """Tabbed sidebar with file tree and configuration panels.

    Contains tabs for:
    - Files: File browser for the workspace
    - Agents: Agent selection
    - Models: Model selection
    - Skills: Skills management
    - MCP: MCP server management

    Signals are forwarded from child panels for the main app to connect to.
    """

    # Forward file tree signals
    file_selected = Signal(str)
    file_attached = Signal(str)
    path_referenced = Signal(str)
    directory_changed = Signal(str)

    # Forward panel signals
    agent_selected = Signal(str)
    model_changed = Signal(str)
    skills_changed = Signal()
    servers_changed = Signal()

    def __init__(self, root_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self._root_path = root_path or os.getcwd()
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Set up the tabbed sidebar UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create tab widget
        self._tabs = QTabWidget()
        self._tabs.setTabPosition(QTabWidget.TabPosition.North)
        self._tabs.setDocumentMode(True)
        self._tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {COLORS.bg_primary};
            }}
            QTabBar::tab {{
                background-color: {COLORS.bg_secondary};
                color: {COLORS.text_secondary};
                padding: 6px 12px;
                margin: 0;
                border: none;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS.bg_primary};
                color: {COLORS.text_primary};
                border-bottom: 2px solid {COLORS.accent_primary};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {COLORS.bg_tertiary};
                color: {COLORS.text_primary};
            }}
        """)

        # Create panels
        self._file_tree = FileTree(self._root_path)
        self._agents_panel = AgentsPanel()
        self._models_panel = ModelsPanel()
        self._skills_panel = SkillsPanel()
        self._mcp_panel = MCPPanel()

        # Add tabs
        self._tabs.addTab(self._file_tree, "Files")
        self._tabs.addTab(self._agents_panel, "Agents")
        self._tabs.addTab(self._models_panel, "Models")
        self._tabs.addTab(self._skills_panel, "Skills")
        self._tabs.addTab(self._mcp_panel, "MCP")

        layout.addWidget(self._tabs)

    def _connect_signals(self):
        """Connect child widget signals to forwarding signals."""
        # File tree signals
        self._file_tree.file_selected.connect(self.file_selected)
        self._file_tree.file_attached.connect(self.file_attached)
        self._file_tree.path_referenced.connect(self.path_referenced)
        self._file_tree.directory_changed.connect(self.directory_changed)

        # Panel signals
        self._agents_panel.agent_selected.connect(self.agent_selected)
        self._models_panel.model_changed.connect(self.model_changed)
        self._skills_panel.skills_changed.connect(self.skills_changed)
        self._mcp_panel.servers_changed.connect(self.servers_changed)

    @property
    def file_tree(self) -> FileTree:
        """Get the file tree widget for direct access."""
        return self._file_tree

    @property
    def agents_panel(self) -> AgentsPanel:
        """Get the agents panel."""
        return self._agents_panel

    @property
    def models_panel(self) -> ModelsPanel:
        """Get the models panel."""
        return self._models_panel

    @property
    def skills_panel(self) -> SkillsPanel:
        """Get the skills panel."""
        return self._skills_panel

    @property
    def mcp_panel(self) -> MCPPanel:
        """Get the MCP panel."""
        return self._mcp_panel

    def set_root_path(self, path: str):
        """Set the root path for the file tree."""
        self._root_path = path
        self._file_tree.set_root_path(path)

    def get_root_path(self) -> str:
        """Get the current root path."""
        return self._file_tree.get_root_path()

    def refresh_all(self):
        """Refresh all panels."""
        self._agents_panel.refresh()
        self._models_panel.refresh()
        self._skills_panel.refresh()
        self._mcp_panel.refresh()

    def switch_to_tab(self, tab_name: str):
        """Switch to a specific tab by name.

        Args:
            tab_name: One of 'files', 'agents', 'models', 'skills', 'mcp'
        """
        tab_indices = {
            'files': 0,
            'agents': 1,
            'models': 2,
            'skills': 3,
            'mcp': 4,
        }
        index = tab_indices.get(tab_name.lower(), 0)
        self._tabs.setCurrentIndex(index)
