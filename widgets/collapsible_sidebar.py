"""Collapsible sidebar with icon-only mode."""

import os
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFrame, QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor

from widgets.sidebar_tabs import SidebarTabs
from styles import (
    get_sidebar_container_style, get_sidebar_toggle_button_style,
    get_sidebar_icon_button_style, get_theme_manager,
)


# Tab icons for collapsed mode
TAB_ICONS = {
    'files': '📁',
    'sessions': '💬',
    'agents': '🐕',
    'models': '🤖',
    'skills': '⚡',
    'mcp': '🔌',
}

TAB_NAMES = ['files', 'sessions', 'agents', 'models', 'skills', 'mcp']
TAB_TOOLTIPS = {
    'files': 'Files (Workspace)',
    'sessions': 'Chat Sessions',
    'agents': 'Agents',
    'models': 'Models',
    'skills': 'Skills',
    'mcp': 'MCP Servers',
}


class CollapsibleSidebar(QWidget):
    """A sidebar that can collapse to icon-only mode.

    Features:
    - Expanded mode: Shows full tabbed sidebar
    - Collapsed mode: Shows only icon buttons
    - Smooth animation on toggle
    - Click icons to expand and switch tabs
    """

    # Forward all signals from SidebarTabs
    file_selected = Signal(str)
    file_attached = Signal(str)
    path_referenced = Signal(str)
    directory_changed = Signal(str)
    agent_selected = Signal(str)
    model_changed = Signal(str)
    model_queued = Signal(str)  # Model change queued (agent busy)
    skills_changed = Signal()
    servers_changed = Signal()
    session_selected = Signal(str)

    # Collapse state changed
    collapsed_changed = Signal(bool)

    def __init__(self, root_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self._root_path = root_path or os.getcwd()
        self._collapsed = False
        self._expanded_width = 280
        self._collapsed_width = 56
        self._current_tab = 'files'

        self._setup_ui()
        self._connect_signals()
        self._apply_shadow()

        # Theme listener
        self._theme_manager = get_theme_manager()
        self._theme_manager.add_listener(self._on_theme_changed)

    def _setup_ui(self):
        """Set up the collapsible sidebar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Icon rail (always visible in collapsed mode)
        self._icon_rail = QFrame()
        self._icon_rail.setFixedWidth(self._collapsed_width)
        self._icon_rail.setStyleSheet(get_sidebar_container_style())

        icon_layout = QVBoxLayout(self._icon_rail)
        icon_layout.setContentsMargins(6, 8, 6, 8)
        icon_layout.setSpacing(4)

        # Toggle button at top
        self._toggle_btn = QPushButton("☰")
        self._toggle_btn.setToolTip("Toggle sidebar (Ctrl+B)")
        self._toggle_btn.setStyleSheet(get_sidebar_toggle_button_style())
        self._toggle_btn.clicked.connect(self.toggle)
        icon_layout.addWidget(self._toggle_btn)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: rgba(255,255,255,0.1); margin: 4px 0;")
        sep.setFixedHeight(1)
        icon_layout.addWidget(sep)

        # Tab icons
        self._icon_buttons: dict[str, QPushButton] = {}
        for tab_name in TAB_NAMES:
            btn = QPushButton(TAB_ICONS[tab_name])
            btn.setToolTip(TAB_TOOLTIPS[tab_name])
            btn.setStyleSheet(get_sidebar_icon_button_style(active=tab_name == self._current_tab))
            btn.clicked.connect(lambda checked, t=tab_name: self._on_icon_clicked(t))
            icon_layout.addWidget(btn)
            self._icon_buttons[tab_name] = btn

        icon_layout.addStretch()

        layout.addWidget(self._icon_rail)

        # Content panel (SidebarTabs, hidden when collapsed)
        self._content_wrapper = QFrame()
        self._content_wrapper.setStyleSheet(get_sidebar_container_style())

        content_layout = QVBoxLayout(self._content_wrapper)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self._sidebar_tabs = SidebarTabs(self._root_path)
        # Hide the tab bar since we have the icon rail
        self._sidebar_tabs._tabs.tabBar().setVisible(False)
        content_layout.addWidget(self._sidebar_tabs)

        layout.addWidget(self._content_wrapper)

        # Set initial size (start expanded)
        self.setMinimumWidth(self._collapsed_width)
        self.setMaximumWidth(self._expanded_width + self._collapsed_width)
        self.setFixedWidth(self._expanded_width + self._collapsed_width)
        self._toggle_btn.setText("◀")
        self._toggle_btn.setToolTip("Collapse sidebar (Ctrl+B)")

    def _connect_signals(self):
        """Connect SidebarTabs signals to our forwarding signals."""
        self._sidebar_tabs.file_selected.connect(self.file_selected)
        self._sidebar_tabs.file_attached.connect(self.file_attached)
        self._sidebar_tabs.path_referenced.connect(self.path_referenced)
        self._sidebar_tabs.directory_changed.connect(self.directory_changed)
        self._sidebar_tabs.agent_selected.connect(self.agent_selected)
        self._sidebar_tabs.model_changed.connect(self.model_changed)
        self._sidebar_tabs.model_queued.connect(self.model_queued)
        self._sidebar_tabs.skills_changed.connect(self.skills_changed)
        self._sidebar_tabs.servers_changed.connect(self.servers_changed)
        self._sidebar_tabs.session_selected.connect(self.session_selected)

        # Track tab changes to update icon highlighting
        self._sidebar_tabs._tabs.currentChanged.connect(self._on_tab_changed)

    def _apply_shadow(self):
        """Apply shadow to the sidebar."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(4, 0)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)

    def _on_theme_changed(self, theme):
        """Update styles when theme changes."""
        self._icon_rail.setStyleSheet(get_sidebar_container_style())
        self._content_wrapper.setStyleSheet(get_sidebar_container_style())
        self._toggle_btn.setStyleSheet(get_sidebar_toggle_button_style())
        self._update_icon_styles()

    def _update_icon_styles(self):
        """Update icon button styles based on active tab."""
        for tab_name, btn in self._icon_buttons.items():
            btn.setStyleSheet(get_sidebar_icon_button_style(active=tab_name == self._current_tab))

    def _on_tab_changed(self, index: int):
        """Handle tab change in SidebarTabs."""
        if 0 <= index < len(TAB_NAMES):
            self._current_tab = TAB_NAMES[index]
            self._update_icon_styles()

    def _on_icon_clicked(self, tab_name: str):
        """Handle icon button click."""
        self._current_tab = tab_name
        self._update_icon_styles()

        # If collapsed, expand first
        if self._collapsed:
            self.expand()

        # Switch to the clicked tab
        self._sidebar_tabs.switch_to_tab(tab_name)

    def toggle(self):
        """Toggle between collapsed and expanded state."""
        if self._collapsed:
            self.expand()
        else:
            self.collapse()

    def collapse(self):
        """Collapse the sidebar to icon-only mode."""
        if self._collapsed:
            return

        self._collapsed = True
        self._content_wrapper.setVisible(False)
        self.setFixedWidth(self._collapsed_width)
        self._toggle_btn.setText("☰")
        self._toggle_btn.setToolTip("Expand sidebar (Ctrl+B)")
        self.collapsed_changed.emit(True)

    def expand(self):
        """Expand the sidebar to full mode."""
        if not self._collapsed:
            return

        self._collapsed = False
        self._content_wrapper.setVisible(True)
        self.setMinimumWidth(self._collapsed_width)
        self.setMaximumWidth(self._expanded_width + self._collapsed_width)
        self.setFixedWidth(self._expanded_width + self._collapsed_width)
        self._toggle_btn.setText("◀")
        self._toggle_btn.setToolTip("Collapse sidebar (Ctrl+B)")
        self.collapsed_changed.emit(False)

    @property
    def is_collapsed(self) -> bool:
        """Check if sidebar is collapsed."""
        return self._collapsed

    # Forward SidebarTabs properties and methods
    @property
    def file_tree(self):
        return self._sidebar_tabs.file_tree

    @property
    def sessions_panel(self):
        return self._sidebar_tabs.sessions_panel

    @property
    def agents_panel(self):
        return self._sidebar_tabs.agents_panel

    @property
    def models_panel(self):
        return self._sidebar_tabs.models_panel

    @property
    def skills_panel(self):
        return self._sidebar_tabs.skills_panel

    @property
    def mcp_panel(self):
        return self._sidebar_tabs.mcp_panel

    def set_root_path(self, path: str):
        self._root_path = path
        self._sidebar_tabs.set_root_path(path)

    def get_root_path(self) -> str:
        return self._sidebar_tabs.get_root_path()

    def refresh_all(self):
        self._sidebar_tabs.refresh_all()

    def set_agent_busy(self, busy: bool):
        """Set the agent busy state for panels that need to know."""
        self._sidebar_tabs.set_agent_busy(busy)

    def switch_to_tab(self, tab_name: str):
        self._current_tab = tab_name.lower()
        self._update_icon_styles()
        self._sidebar_tabs.switch_to_tab(tab_name)

    def cleanup(self):
        """Explicitly clean up resources. Call before discarding widget."""
        if hasattr(self, '_theme_manager') and hasattr(self, '_on_theme_changed'):
            try:
                self._theme_manager.remove_listener(self._on_theme_changed)
            except Exception:
                pass

    def closeEvent(self, event):
        """Clean up when widget is closed."""
        self.cleanup()
        super().closeEvent(event)
