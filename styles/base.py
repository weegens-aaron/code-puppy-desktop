"""Base styles for main window, scroll areas, and content browser.

This module contains:
- Main window styles
- Scroll area styles
- Content browser styles
"""

from styles.colors import get_theme_manager

_theme_manager = get_theme_manager()



# =============================================================================
# Main Window & Layout Styles
# =============================================================================

def get_main_window_style() -> str:
    """Get main window style for current theme."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        # Beveled toolbar buttons
        return f"""
            QMainWindow {{
                background-color: {colors.bg_primary};
            }}
            QToolBar {{
                background-color: {colors.bg_primary};
                border: none;
                spacing: 10px;
                padding: 8px 12px;
            }}
            QToolBar QToolButton {{
                color: {colors.text_primary};
                background-color: {colors.bg_primary};
                border-top: 2px solid {colors.shadow_light};
                border-left: 2px solid {colors.shadow_light};
                border-bottom: 2px solid {colors.shadow_dark};
                border-right: 2px solid {colors.shadow_dark};
                padding: 10px 18px;
                border-radius: 10px;
                font-weight: 600;
            }}
            QToolBar QToolButton:hover {{
                background-color: {colors.bg_tertiary};
                color: {colors.accent_primary};
            }}
            QToolBar QToolButton:pressed {{
                background-color: {colors.bg_secondary};
                border-top: 2px solid {colors.shadow_dark};
                border-left: 2px solid {colors.shadow_dark};
                border-bottom: 2px solid {colors.shadow_light};
                border-right: 2px solid {colors.shadow_light};
            }}
            QStatusBar {{
                background-color: {colors.bg_primary};
                color: {colors.text_secondary};
                border-top: 2px solid {colors.shadow_dark};
            }}
            QSplitter::handle {{
                background-color: {colors.bg_primary};
            }}
            QSplitter::handle:horizontal {{
                width: 6px;
            }}
        """
    else:
        return f"""
            QMainWindow {{
                background-color: {colors.bg_primary};
            }}
            QToolBar {{
                background-color: {colors.bg_secondary};
                border: none;
                spacing: 8px;
                padding: 4px;
            }}
            QToolBar QToolButton {{
                color: {colors.text_primary};
                background-color: transparent;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }}
            QToolBar QToolButton:hover {{
                background-color: {colors.bg_tertiary};
            }}
            QStatusBar {{
                background-color: {colors.bg_secondary};
                color: {colors.text_secondary};
            }}
            QSplitter::handle {{
                background-color: {colors.border_subtle};
            }}
            QSplitter::handle:horizontal {{
                width: 2px;
            }}
        """


def get_scroll_area_style() -> str:
    """Get modern scroll area style for current theme."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        # Beveled scrollbar
        return f"""
            QScrollArea {{
                background-color: {colors.bg_primary};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {colors.bg_secondary};
                width: 12px;
                margin: 4px 2px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {colors.bg_tertiary};
                border-top: 1px solid {colors.shadow_light};
                border-left: 1px solid {colors.shadow_light};
                border-bottom: 1px solid {colors.shadow_dark};
                border-right: 1px solid {colors.shadow_dark};
                min-height: 40px;
                border-radius: 5px;
                margin: 1px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {colors.accent_primary};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """
    else:
        return f"""
            QScrollArea {{
                background-color: {colors.bg_primary};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: transparent;
                width: 8px;
                margin: 4px 2px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {colors.border_default};
                min-height: 30px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {colors.text_muted};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """


def get_content_browser_style() -> str:
    """Get content browser style for current theme."""
    colors = _theme_manager.current
    return f"""
        QTextBrowser {{
            background-color: {colors.bg_content};
            color: {colors.text_primary};
            padding: 12px 16px;
            font-family: 'Segoe UI', -apple-system, sans-serif;
            font-size: 14px;
            border: none;
        }}
    """

