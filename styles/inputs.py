"""Input field and card styles with neumorphic support.

This module contains:
- input_style: Basic input field stylesheet
- neu_input_inset_style: Neumorphic inset input style
- neu_card_style: Neumorphic card/panel style
- neu_card_inset_style: Neumorphic inset card style
- Modern input area styles for chat interface
"""

from styles.colors import get_theme_manager

_theme_manager = get_theme_manager()


# =============================================================================
# Neumorphic Input Styles
# =============================================================================

def input_style(
    bg_color: str | None = None,
    text_color: str | None = None,
    border_color: str | None = None,
    focus_color: str | None = None,
    border_radius: int = 8,
    padding: str = "8px",
    font_size: str = "14px",
) -> str:
    """Generate input field stylesheet with neumorphic support."""
    colors = _theme_manager.current
    bg_color = bg_color or colors.bg_input
    text_color = text_color or colors.text_primary
    border_color = border_color or colors.border_default
    focus_color = focus_color or colors.border_focus

    if colors.is_neumorphic:
        # Neumorphic inset input field
        return f"""
            QTextEdit {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.3 {colors.bg_primary},
                    stop:1 {colors.shadow_light}
                );
                color: {text_color};
                border: none;
                border-radius: {border_radius + 8}px;
                padding: {padding};
                padding-left: 16px;
                font-size: {font_size};
            }}
            QTextEdit:focus {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.2 {colors.bg_primary},
                    stop:1 {colors.shadow_light}
                );
            }}
        """
    else:
        return f"""
            QTextEdit {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: {border_radius}px;
                padding: {padding};
                font-size: {font_size};
            }}
            QTextEdit:focus {{
                border-color: {focus_color};
            }}
        """


def neu_input_inset_style(
    border_radius: int = 20,
    padding: str = "12px 20px",
    font_size: str = "14px",
) -> str:
    """Generate neumorphic inset input style."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.4 {colors.bg_primary},
                    stop:1 {colors.shadow_light}
                );
                color: {colors.text_primary};
                border: none;
                border-radius: {border_radius}px;
                padding: {padding};
                font-size: {font_size};
                selection-background-color: {colors.accent_primary};
            }}
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
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
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {colors.bg_input};
                color: {colors.text_primary};
                border: 1px solid {colors.border_default};
                border-radius: {border_radius}px;
                padding: {padding};
                font-size: {font_size};
            }}
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border-color: {colors.border_focus};
            }}
        """


# =============================================================================
# Neumorphic Card/Panel Styles
# =============================================================================

def neu_card_style(border_radius: int = 20) -> str:
    """Generate neumorphic card/panel style."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            QFrame, QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_light},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_dark}
                );
                border: none;
                border-radius: {border_radius}px;
            }}
        """
    else:
        return f"""
            QFrame, QWidget {{
                background-color: {colors.bg_secondary};
                border: 1px solid {colors.border_subtle};
                border-radius: {border_radius}px;
            }}
        """


def neu_card_inset_style(border_radius: int = 20) -> str:
    """Generate neumorphic inset card style."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_light}
                );
                border: none;
                border-radius: {border_radius}px;
            }}
        """
    else:
        return f"""
            QFrame {{
                background-color: {colors.bg_content};
                border: 1px solid {colors.border_subtle};
                border-radius: {border_radius}px;
            }}
        """


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


def get_modern_send_button_style() -> str:
    """Get modern circular send button style."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        # Raised neumorphic button with accent color
        return f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f0a8b8,
                    stop:0.2 {colors.accent_primary},
                    stop:0.8 {colors.accent_primary},
                    stop:1 {colors.accent_primary_hover}
                );
                color: white;
                border: none;
                border-radius: 16px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 70px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f5b8c5,
                    stop:0.15 {colors.accent_primary},
                    stop:0.85 {colors.accent_primary},
                    stop:1 {colors.accent_primary_hover}
                );
            }}
            QPushButton:pressed {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.accent_primary_hover},
                    stop:0.3 {colors.accent_primary},
                    stop:0.7 {colors.accent_primary},
                    stop:1 #f0a8b8
                );
            }}
            QPushButton:disabled {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_light},
                    stop:0.2 {colors.bg_tertiary},
                    stop:0.8 {colors.bg_tertiary},
                    stop:1 {colors.shadow_dark}
                );
                color: {colors.text_muted};
            }}
        """
    else:
        return f"""
            QPushButton {{
                background-color: {colors.accent_primary};
                color: white;
                border: none;
                border-radius: 20px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                max-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {colors.accent_primary_hover};
            }}
            QPushButton:disabled {{
                background-color: {colors.bg_tertiary};
                color: {colors.text_muted};
            }}
        """


def get_modern_attach_button_style() -> str:
    """Get modern attach button style."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_light},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_dark}
                );
                color: {colors.text_secondary};
                border: none;
                border-radius: 22px;
                padding: 10px;
                font-size: 20px;
                min-width: 44px;
                min-height: 44px;
                max-width: 44px;
                max-height: 44px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_light},
                    stop:0.4 {colors.bg_tertiary},
                    stop:1 {colors.shadow_dark}
                );
                color: {colors.text_primary};
            }}
            QPushButton:pressed {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_light}
                );
            }}
        """
    else:
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {colors.text_secondary};
                border: none;
                border-radius: 20px;
                padding: 8px;
                font-size: 18px;
                min-width: 36px;
                min-height: 36px;
                max-width: 36px;
                max-height: 36px;
            }}
            QPushButton:hover {{
                background-color: {colors.bg_tertiary};
                color: {colors.text_primary};
            }}
        """


def get_modern_cancel_button_style() -> str:
    """Get modern cancel button style."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.accent_error},
                    stop:1 {colors.accent_error_hover}
                );
                color: white;
                border: none;
                border-radius: 18px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {colors.accent_error_hover};
            }}
        """
    else:
        return f"""
            QPushButton {{
                background-color: {colors.accent_error};
                color: white;
                border: none;
                border-radius: 16px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {colors.accent_error_hover};
            }}
        """
