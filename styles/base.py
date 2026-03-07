"""Base styles and neumorphism utilities.

This module contains:
- Neumorphism shadow utilities
- Main window styles
- Scroll area styles
- Content browser styles
- Deprecated module-level constants
"""

from styles.colors import get_theme_manager

_theme_manager = get_theme_manager()


# =============================================================================
# Neumorphism Utilities
# =============================================================================

def _neu_shadow_outset(blur: int = 10, offset: int = 5) -> str:
    """Generate neumorphic outset (raised) shadow CSS approximation.

    Note: Qt CSS doesn't support box-shadow, so we simulate with borders.
    """
    colors = _theme_manager.current
    if not colors.is_neumorphic:
        return ""
    # Return border-based approximation
    return f"""
        border: 1px solid {colors.shadow_light};
        border-bottom-color: {colors.shadow_dark};
        border-right-color: {colors.shadow_dark};
    """


def _neu_shadow_inset() -> str:
    """Generate neumorphic inset (pressed) shadow CSS approximation."""
    colors = _theme_manager.current
    if not colors.is_neumorphic:
        return ""
    return f"""
        border: 1px solid {colors.shadow_dark};
        border-bottom-color: {colors.shadow_light};
        border-right-color: {colors.shadow_light};
    """


def get_neumorphic_effect_params(inset: bool = False) -> dict:
    """Get parameters for creating QGraphicsDropShadowEffect.

    For true neumorphism, apply two effects: one light (top-left) and one dark (bottom-right).

    Args:
        inset: If True, returns params for inset (pressed) effect

    Returns:
        Dict with: blur_radius, x_offset, y_offset, color, secondary params
    """
    colors = _theme_manager.current

    if not colors.is_neumorphic:
        # Standard shadow for non-neumorphic themes
        return {
            "primary": {
                "blur_radius": 15,
                "x_offset": 0,
                "y_offset": 4,
                "color": "rgba(0, 0, 0, 0.3)",
            },
            "secondary": None,
        }

    if inset:
        return {
            "primary": {
                "blur_radius": 8,
                "x_offset": 3,
                "y_offset": 3,
                "color": colors.shadow_dark,
            },
            "secondary": {
                "blur_radius": 8,
                "x_offset": -3,
                "y_offset": -3,
                "color": colors.shadow_light,
            },
        }
    else:
        return {
            "primary": {
                "blur_radius": 12,
                "x_offset": 6,
                "y_offset": 6,
                "color": colors.shadow_dark,
            },
            "secondary": {
                "blur_radius": 12,
                "x_offset": -6,
                "y_offset": -6,
                "color": colors.shadow_light,
            },
        }


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


COPY_BUTTON_STYLE = """
    QPushButton {
        background-color: transparent;
        border: none;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: rgba(255,255,255,0.2);
        border-radius: 4px;
    }
"""


# DEPRECATED: These module-level constants are evaluated at import time.
# They're kept for backwards compatibility but code should migrate to using
# the function versions (get_main_window_style(), etc.) to support theme changes.
MAIN_WINDOW_STYLE = get_main_window_style()
SCROLL_AREA_STYLE = get_scroll_area_style()
CONTENT_BROWSER_STYLE = get_content_browser_style()
