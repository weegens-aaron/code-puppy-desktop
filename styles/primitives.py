"""Primitive style building blocks for DRY styling.

This module contains reusable element types:
- Sidebar material colors and inset bevel constants
- Common element styles (flat label, inset container, inset panel)
"""

from styles.colors import get_theme_manager

_theme_manager = get_theme_manager()


# =============================================================================
# Sidebar Material Constants
# =============================================================================

# Dark pink sidebar material (the recessed pocket)
SIDEBAR_MATERIAL = "#3a2832"
SIDEBAR_HOVER = "#4a3842"
SIDEBAR_SELECTED = "#5a4852"

# Inset bevel colors (for recessed elements)
INSET_DARK = "#1a1a1e"   # Top/left shadow
INSET_LIGHT = "#4a4a58"  # Bottom/right highlight



# =============================================================================
# Flat Label Style (painted on device body, no bevel)
# =============================================================================

def flat_icon_label_style(
    size: int = 52,
    font_size: int = 28,
    padding: int = 12,
) -> str:
    """Flat painted label on device body - no bevel, just icon.

    Used for: unselected sidebar tabs, toggle button
    Pressed state uses dark pink (SIDEBAR_MATERIAL) to indicate recessed.
    """
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {colors.text_secondary};
                border: none;
                padding: {padding}px;
                font-size: {font_size}px;
                min-width: {size}px;
                min-height: {size}px;
                max-width: {size}px;
                max-height: {size}px;
            }}
            QPushButton:hover {{
                color: {colors.accent_primary};
            }}
            QPushButton:pressed {{
                background-color: {SIDEBAR_MATERIAL};
                border-top: 2px solid {INSET_DARK};
                border-left: 2px solid {INSET_DARK};
                border-bottom: 2px solid {INSET_LIGHT};
                border-right: 2px solid {INSET_LIGHT};
                border-radius: 12px;
            }}
        """
    else:
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {colors.text_primary};
                border: none;
                border-radius: 10px;
                padding: {padding}px;
                font-size: {font_size}px;
                min-width: {size}px;
                min-height: {size}px;
                max-width: {size}px;
                max-height: {size}px;
            }}
            QPushButton:hover {{
                background-color: {colors.bg_tertiary};
                color: white;
            }}
        """


# =============================================================================
# Inset/Recessed Container Style
# =============================================================================

def inset_container_style(
    border_radius: int = 16,
    bevel_width: int = 3,
) -> str:
    """Recessed container with inset bevel - like sidebar pocket or selected tab.

    Used for: selected sidebar tabs, sidebar content panel
    """
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            QPushButton {{
                background-color: {SIDEBAR_MATERIAL};
                color: {colors.accent_primary};
                border-top: {bevel_width}px solid {INSET_DARK};
                border-left: {bevel_width}px solid {INSET_DARK};
                border-bottom: {bevel_width}px solid {INSET_LIGHT};
                border-right: {bevel_width}px solid {INSET_LIGHT};
                border-radius: {border_radius}px;
                padding: 10px;
                font-size: 28px;
                min-width: 52px;
                min-height: 52px;
                max-width: 52px;
                max-height: 52px;
            }}
            QPushButton:hover {{
                color: {colors.accent_primary_hover};
            }}
        """
    else:
        return f"""
            QPushButton {{
                background-color: #4a4a4a;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 27px;
                min-width: 52px;
                min-height: 52px;
                max-width: 52px;
                max-height: 52px;
            }}
            QPushButton:hover {{
                background-color: #5a5a5a;
                color: white;
            }}
        """



# =============================================================================
# Inset Panel Style (for containers, not buttons)
# =============================================================================

def inset_panel_style(border_radius: int = 12) -> str:
    """Recessed panel/container style with inset bevel.

    Used for: sidebar content wrapper, recessed content areas
    """
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            background-color: {SIDEBAR_MATERIAL};
            border-top: 3px solid {INSET_DARK};
            border-left: 3px solid {INSET_DARK};
            border-bottom: 3px solid {INSET_LIGHT};
            border-right: 3px solid {INSET_LIGHT};
            border-radius: {border_radius}px;
        """
    else:
        return f"""
            background-color: {colors.bg_secondary};
            border: none;
        """
