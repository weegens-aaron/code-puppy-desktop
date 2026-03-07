"""Sidebar, file tree, and tab widget styles.

This module contains:
- File tree filter and view styles
- Context menu styles
- Tab widget styles
- Collapsible sidebar styles
- Icon rail and toggle button styles
"""

from styles.colors import get_theme_manager
from styles.primitives import (
    SIDEBAR_MATERIAL,
    SIDEBAR_HOVER,
    SIDEBAR_SELECTED,
    INSET_DARK,
    INSET_LIGHT,
    flat_icon_label_style,
    inset_container_style,
    inset_panel_style,
)

_theme_manager = get_theme_manager()


# =============================================================================
# File Tree Styles
# =============================================================================

def get_file_tree_filter_style() -> str:
    """Get file tree filter input style for current theme."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            QLineEdit {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_light}
                );
                color: {colors.text_primary};
                border: none;
                border-radius: 14px;
                padding: 8px 16px;
                margin: 4px;
            }}
            QLineEdit:focus {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.3 {colors.bg_primary},
                    stop:1 {colors.shadow_light}
                );
            }}
        """
    else:
        return f"""
            QLineEdit {{
                background-color: {colors.bg_tertiary};
                color: {colors.text_primary};
                border: 1px solid {colors.border_default};
                border-radius: 4px;
                padding: 4px 8px;
                margin: 0 4px;
            }}
            QLineEdit:focus {{
                border-color: {colors.border_focus};
            }}
        """


def get_file_tree_view_style() -> str:
    """Get file tree view style for current theme."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            QTreeView {{
                background-color: {SIDEBAR_MATERIAL};
                color: {colors.text_primary};
                border: none;
                outline: none;
            }}
            QTreeView::item {{
                padding: 6px 8px;
                border-radius: 0px;
                margin: 0px;
                border-left: 3px solid transparent;
            }}
            QTreeView::item:hover {{
                background-color: {SIDEBAR_HOVER};
            }}
            QTreeView::item:selected {{
                background-color: {SIDEBAR_SELECTED};
                border-left: 3px solid {colors.accent_primary};
                color: {colors.text_primary};
            }}
            QTreeView::branch {{
                background-color: transparent;
            }}
        """
    else:
        return f"""
            QTreeView {{
                background-color: {colors.bg_primary};
                color: {colors.text_primary};
                border: none;
            }}
            QTreeView::item {{
                padding: 4px;
            }}
            QTreeView::item:hover {{
                background-color: {colors.bg_secondary};
            }}
            QTreeView::item:selected {{
                background-color: {colors.accent_primary};
            }}
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {{
                border-image: none;
                image: url(none);
            }}
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings  {{
                border-image: none;
                image: url(none);
            }}
        """


def get_context_menu_style() -> str:
    """Get context menu style for current theme."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            QMenu {{
                background-color: {colors.bg_primary};
                color: {colors.text_primary};
                border: none;
                border-radius: 12px;
                padding: 8px;
            }}
            QMenu::item {{
                padding: 8px 20px;
                border-radius: 8px;
                margin: 2px;
            }}
            QMenu::item:selected {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.5 {colors.accent_primary},
                    stop:1 {colors.shadow_light}
                );
                color: white;
            }}
        """
    else:
        return f"""
            QMenu {{
                background-color: {colors.bg_secondary};
                color: {colors.text_primary};
                border: 1px solid {colors.border_default};
            }}
            QMenu::item {{
                padding: 6px 20px;
            }}
            QMenu::item:selected {{
                background-color: {colors.accent_primary};
            }}
        """


# =============================================================================
# Tab Widget Styles
# =============================================================================

def get_tab_widget_style() -> str:
    """Get tab widget style for current theme."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            QTabWidget::pane {{
                border: none;
                background-color: {SIDEBAR_MATERIAL};
            }}
            QTabBar::tab {{
                background-color: #3a3038;
                color: {colors.text_secondary};
                padding: 12px 20px;
                margin: 4px;
                border-top: 2px solid {colors.shadow_light};
                border-left: 2px solid {colors.shadow_light};
                border-bottom: 2px solid {colors.shadow_dark};
                border-right: 2px solid {colors.shadow_dark};
                border-radius: 12px;
            }}
            QTabBar::tab:selected {{
                background-color: #322830;
                color: {colors.accent_primary};
                border-top: 2px solid {colors.shadow_dark};
                border-left: 2px solid {colors.shadow_dark};
                border-bottom: 2px solid {colors.shadow_light};
                border-right: 2px solid {colors.shadow_light};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: #453a42;
                color: {colors.text_primary};
            }}
        """
    else:
        return f"""
            QTabWidget::pane {{
                border: none;
                background-color: {colors.bg_primary};
            }}
            QTabBar::tab {{
                background-color: {colors.bg_secondary};
                color: {colors.text_secondary};
                padding: 6px 12px;
                margin: 0;
                border: none;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                background-color: {colors.bg_primary};
                color: {colors.text_primary};
                border-bottom: 2px solid {colors.accent_primary};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {colors.bg_tertiary};
                color: {colors.text_primary};
            }}
        """


# =============================================================================
# Collapsible Sidebar Styles
# =============================================================================

def get_sidebar_container_style() -> str:
    """Get collapsible sidebar content panel - recessed pocket in device."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        panel_style = inset_panel_style(border_radius=12)
        return f"""
            QFrame#content_wrapper {{
                {panel_style}
                margin: 4px;
                padding: 2px;
            }}
            QFrame {{
                background-color: {SIDEBAR_MATERIAL};
                border: none;
            }}
            QWidget {{
                background-color: {SIDEBAR_MATERIAL};
                border: none;
            }}
        """
    else:
        return f"""
            QWidget {{
                background-color: {colors.bg_secondary};
                border: none;
            }}
        """


def get_icon_rail_style() -> str:
    """Get icon rail style - dark gray device body material."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            QFrame {{
                background-color: {colors.bg_primary};
                border: none;
            }}
            QWidget {{
                background-color: {colors.bg_primary};
            }}
        """
    else:
        return f"""
            QFrame {{
                background-color: {colors.bg_secondary};
                border: none;
            }}
        """


def get_sidebar_outer_style() -> str:
    """Get collapsible sidebar outer container style - device body."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            CollapsibleSidebar {{
                background-color: {colors.bg_primary};
                border-right: 2px solid {colors.accent_primary};
            }}
        """
    else:
        return f"""
            CollapsibleSidebar {{
                background-color: {colors.bg_secondary};
                border-right: 1px solid {colors.border_subtle};
            }}
        """


def get_sidebar_toggle_button_style() -> str:
    """Get sidebar toggle button style - flat label like unselected tabs."""
    # Toggle button is a flat label on the device body, like unselected tabs
    return flat_icon_label_style(size=52, font_size=22, padding=12)


def get_sidebar_icon_button_style(active: bool = False) -> str:
    """Get sidebar icon button style for collapsed mode.

    Uses primitives:
    - active=True: inset_container_style (recessed into sidebar material)
    - active=False: flat_icon_label_style (painted on device body)
    """
    if active:
        return inset_container_style(border_radius=16, bevel_width=3)
    else:
        return flat_icon_label_style(size=56, font_size=28, padding=12)
