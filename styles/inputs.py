"""Input field styles with neumorphic support.

This module contains:
- Modern input area styles for chat interface
"""

from styles.colors import get_theme_manager

_theme_manager = get_theme_manager()



# =============================================================================
# Modern Input Area Styles
# =============================================================================

def get_modern_input_container_style() -> str:
    """Get modern floating input container style."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        # Beveled inset container for the input area
        return f"""
            QWidget {{
                background-color: {colors.bg_secondary};
                border-top: 2px solid {colors.shadow_dark};
                border-left: 2px solid {colors.shadow_dark};
                border-bottom: 2px solid {colors.shadow_light};
                border-right: 2px solid {colors.shadow_light};
                border-radius: 16px;
                margin: 8px 12px;
            }}
        """
    else:
        return f"""
            QWidget {{
                background-color: {colors.bg_primary};
            }}
        """


def get_modern_input_field_style() -> str:
    """Get modern input field style with neumorphic support."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        # Transparent background - container handles the neumorphic styling
        return f"""
            QTextEdit {{
                background: transparent;
                color: {colors.text_primary};
                border: none;
                border-radius: 0px;
                padding: 12px 16px;
                font-size: 14px;
                font-family: 'Segoe UI', -apple-system, sans-serif;
            }}
            QTextEdit:focus {{
                background: transparent;
                border: none;
            }}
        """
    else:
        return f"""
            QTextEdit {{
                background-color: {colors.bg_secondary};
                color: {colors.text_primary};
                border: 1px solid {colors.border_subtle};
                border-radius: 24px;
                padding: 12px 20px;
                font-size: 14px;
                font-family: 'Segoe UI', -apple-system, sans-serif;
            }}
            QTextEdit:focus {{
                border-color: {colors.accent_primary};
                background-color: {colors.bg_tertiary};
            }}
        """

