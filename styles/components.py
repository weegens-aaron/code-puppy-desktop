"""Miscellaneous component styles.

This module contains:
- Attachment chip styles
- Status bar label styles
- Progress bar styles
- Toggle switch styles
"""

from styles.colors import get_theme_manager

_theme_manager = get_theme_manager()


# =============================================================================
# Attachment Chip Styles
# =============================================================================

def get_attachment_chip_style() -> str:
    """Get attachment chip container style for current theme."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        # Beveled raised chip
        return f"""
            QWidget {{
                background-color: {colors.bg_primary};
                border-top: 1px solid {colors.shadow_light};
                border-left: 1px solid {colors.shadow_light};
                border-bottom: 1px solid {colors.shadow_dark};
                border-right: 1px solid {colors.shadow_dark};
                border-radius: 8px;
                padding: 4px 8px;
            }}
        """
    else:
        return f"""
            QWidget {{
                background-color: {colors.bg_tertiary};
                border-radius: 4px;
                padding: 2px 4px;
            }}
        """


def get_attachment_label_style() -> str:
    """Get attachment label style for current theme."""
    colors = _theme_manager.current
    return f"""
        QPushButton {{
            color: {colors.text_primary};
            background: transparent;
            border: none;
            font-size: 12px;
            padding: 0 4px;
        }}
    """


def get_attachment_remove_style() -> str:
    """Get attachment remove button style for current theme."""
    colors = _theme_manager.current
    return f"""
        QPushButton {{
            color: {colors.text_muted};
            background: transparent;
            border: none;
            font-size: 14px;
            padding: 0 4px;
        }}
        QPushButton:hover {{
            color: {colors.accent_error};
        }}
    """


# =============================================================================
# Status Bar Label Styles
# =============================================================================

def get_status_label_style(color: str) -> str:
    """Get status bar label style with the given color."""
    return f"color: {color}; padding: 0 8px;"


def get_status_activity_style() -> str:
    """Get status bar activity label style for current theme."""
    colors = _theme_manager.current
    return f"color: {colors.accent_info}; padding: 0 8px; font-weight: bold;"


def get_status_separator_style() -> str:
    """Get status bar separator style for current theme."""
    colors = _theme_manager.current
    return f"color: {colors.border_subtle};"


# =============================================================================
# Neumorphic Progress Bar Style
# =============================================================================

def get_progress_bar_style() -> str:
    """Get progress bar style with neumorphic support."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            QProgressBar {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_light}
                );
                border: none;
                border-radius: 8px;
                height: 16px;
                text-align: center;
                color: {colors.text_muted};
                font-size: 10px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors.accent_primary},
                    stop:1 {colors.accent_primary_hover}
                );
                border-radius: 7px;
                margin: 1px;
            }}
        """
    else:
        return f"""
            QProgressBar {{
                background-color: {colors.bg_tertiary};
                border: none;
                border-radius: 4px;
                height: 8px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {colors.accent_primary};
                border-radius: 4px;
            }}
        """


# =============================================================================
# Neumorphic Toggle Switch Style
# =============================================================================

def get_toggle_switch_style(checked: bool = False) -> str:
    """Get toggle switch style for neumorphic design."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        if checked:
            return f"""
                QPushButton {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 {colors.shadow_dark},
                        stop:0.5 {colors.accent_primary},
                        stop:1 {colors.shadow_light}
                    );
                    border: none;
                    border-radius: 16px;
                    padding: 4px;
                    min-width: 52px;
                    max-width: 52px;
                    min-height: 28px;
                    max-height: 28px;
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 {colors.shadow_dark},
                        stop:0.5 {colors.bg_primary},
                        stop:1 {colors.shadow_light}
                    );
                    border: none;
                    border-radius: 16px;
                    padding: 4px;
                    min-width: 52px;
                    max-width: 52px;
                    min-height: 28px;
                    max-height: 28px;
                }}
            """
    else:
        bg = colors.accent_primary if checked else colors.bg_tertiary
        return f"""
            QPushButton {{
                background-color: {bg};
                border: none;
                border-radius: 14px;
                min-width: 48px;
                max-width: 48px;
                min-height: 24px;
                max-height: 24px;
            }}
        """
