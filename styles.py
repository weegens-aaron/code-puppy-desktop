"""Centralized styles for the desktop application.

This module provides a single source of truth for all colors, fonts,
and widget styles used throughout the desktop app.
"""

from dataclasses import dataclass
from typing import Callable, NamedTuple


class ColorScheme(NamedTuple):
    """Color scheme for the application."""
    # Theme metadata
    name: str = "Dark"

    # Backgrounds
    bg_primary: str = "#1e1e1e"
    bg_secondary: str = "#2d2d2d"
    bg_tertiary: str = "#3d3d3d"
    bg_input: str = "#3d3d3d"
    bg_content: str = "#252526"
    bg_code: str = "#1e1e1e"

    # Borders
    border_default: str = "#5a5a5a"
    border_subtle: str = "#3d3d3d"
    border_focus: str = "#1a73e8"

    # Text
    text_primary: str = "#e0e0e0"
    text_secondary: str = "#a0a0a0"
    text_muted: str = "#6a6a6a"
    text_code: str = "#ce9178"

    # Accents
    accent_primary: str = "#1a73e8"
    accent_primary_hover: str = "#1565c0"
    accent_success: str = "#90EE90"
    accent_warning: str = "#ffc107"
    accent_error: str = "#d32f2f"
    accent_error_hover: str = "#b71c1c"
    accent_info: str = "#4fc3f7"

    # Message role colors
    role_user_bg: str = "#1a73e8"
    role_user_text: str = "white"
    role_assistant_bg: str = "#2d5016"
    role_assistant_text: str = "#90EE90"
    role_thinking_bg: str = "#5c4d2b"
    role_thinking_text: str = "#ffc107"
    role_tool_bg: str = "#1e3a5f"
    role_tool_text: str = "#4fc3f7"
    role_tool_output_bg: str = "#1e3a5f"
    role_tool_output_text: str = "#4fc3f7"
    role_error_bg: str = "#5c1a1a"
    role_error_text: str = "#f87171"


# =============================================================================
# Preset Themes
# =============================================================================

THEME_DARK = ColorScheme(
    name="Dark",
    bg_primary="#1e1e1e",
    bg_secondary="#2d2d2d",
    bg_tertiary="#3d3d3d",
    bg_input="#3d3d3d",
    bg_content="#252526",
    bg_code="#1e1e1e",
    border_default="#5a5a5a",
    border_subtle="#3d3d3d",
    border_focus="#0078d4",
    text_primary="#e0e0e0",
    text_secondary="#a0a0a0",
    text_muted="#6a6a6a",
    text_code="#ce9178",
    accent_primary="#0078d4",
    accent_primary_hover="#106ebe",
    accent_success="#0078d4",
    accent_warning="#ffc107",
    accent_error="#d32f2f",
    accent_error_hover="#b71c1c",
    accent_info="#5a5a5a",
    role_user_bg="#0078d4",
    role_user_text="white",
    role_assistant_bg="#2d2d2d",
    role_assistant_text="#e0e0e0",
    role_thinking_bg="#3d3d3d",
    role_thinking_text="#a0a0a0",
    role_tool_bg="#2d2d2d",
    role_tool_text="#a0a0a0",
    role_tool_output_bg="#2d2d2d",
    role_tool_output_text="#a0a0a0",
    role_error_bg="#5c1a1a",
    role_error_text="#f87171",
)

THEME_LIGHT = ColorScheme(
    name="Light",
    bg_primary="#ffffff",
    bg_secondary="#f5f5f5",
    bg_tertiary="#e8e8e8",
    bg_input="#ffffff",
    bg_content="#fafafa",
    bg_code="#f5f5f5",
    border_default="#d0d0d0",
    border_subtle="#e0e0e0",
    border_focus="#0078d4",
    text_primary="#1a1a1a",
    text_secondary="#505050",
    text_muted="#909090",
    text_code="#c41a16",
    accent_primary="#0078d4",
    accent_primary_hover="#106ebe",
    accent_success="#0078d4",
    accent_warning="#f57c00",
    accent_error="#c62828",
    accent_error_hover="#b71c1c",
    accent_info="#909090",
    role_user_bg="#0078d4",
    role_user_text="white",
    role_assistant_bg="#f5f5f5",
    role_assistant_text="#1a1a1a",
    role_thinking_bg="#e8e8e8",
    role_thinking_text="#505050",
    role_tool_bg="#f5f5f5",
    role_tool_text="#505050",
    role_tool_output_bg="#f5f5f5",
    role_tool_output_text="#505050",
    role_error_bg="#ffebee",
    role_error_text="#c62828",
)

# All available themes
THEMES: dict[str, ColorScheme] = {
    "Dark": THEME_DARK,
    "Light": THEME_LIGHT,
}


# =============================================================================
# Theme Manager
# =============================================================================

class ThemeManager:
    """Manages the current theme and notifies listeners of changes."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._current_theme = THEME_DARK
            cls._instance._listeners: list[Callable[[ColorScheme], None]] = []
        return cls._instance

    @property
    def current(self) -> ColorScheme:
        """Get the current color scheme."""
        return self._current_theme

    @property
    def theme_name(self) -> str:
        """Get the current theme name."""
        return self._current_theme.name

    def set_theme(self, name: str) -> bool:
        """Set the current theme by name.

        Args:
            name: Theme name (must be in THEMES)

        Returns:
            True if theme was changed, False if not found
        """
        if name in THEMES:
            self._current_theme = THEMES[name]
            self._notify_listeners()
            return True
        return False

    def add_listener(self, callback: Callable[[ColorScheme], None]):
        """Add a listener for theme changes."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[ColorScheme], None]):
        """Remove a theme change listener."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_listeners(self):
        """Notify all listeners of theme change."""
        for listener in self._listeners:
            try:
                listener(self._current_theme)
            except Exception:
                pass  # Don't let listener errors break theme switching

    @staticmethod
    def available_themes() -> list[str]:
        """Get list of available theme names."""
        return list(THEMES.keys())


# Global theme manager instance
_theme_manager = ThemeManager()


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    return _theme_manager


# For backwards compatibility, COLORS refers to current theme
def _get_colors() -> ColorScheme:
    """Get current color scheme (dynamic)."""
    return _theme_manager.current


class _DynamicColors:
    """Proxy that always returns current theme colors."""

    def __getattr__(self, name: str):
        return getattr(_theme_manager.current, name)


COLORS = _DynamicColors()


# =============================================================================
# Role Styles
# =============================================================================

@dataclass
class RoleStyle:
    """Style configuration for a message role."""
    background_color: str
    text_color: str
    font_family: str = "'Segoe UI', -apple-system, sans-serif"
    font_size: str = "14px"


def get_role_style(role: str) -> RoleStyle:
    """Get the style for a message role (uses current theme)."""
    colors = _theme_manager.current

    role_styles = {
        "user": RoleStyle(
            background_color=colors.role_user_bg,
            text_color=colors.role_user_text,
        ),
        "assistant": RoleStyle(
            background_color=colors.role_assistant_bg,
            text_color=colors.role_assistant_text,
        ),
        "thinking": RoleStyle(
            background_color=colors.role_thinking_bg,
            text_color=colors.role_thinking_text,
            font_family="'Consolas', 'Monaco', monospace",
            font_size="13px",
        ),
        "tool_call": RoleStyle(
            background_color=colors.role_tool_bg,
            text_color=colors.role_tool_text,
            font_family="'Consolas', 'Monaco', monospace",
            font_size="13px",
        ),
        "tool_output": RoleStyle(
            background_color=colors.role_tool_output_bg,
            text_color=colors.role_tool_output_text,
            font_family="'Consolas', 'Monaco', monospace",
            font_size="13px",
        ),
        "error": RoleStyle(
            background_color=colors.role_error_bg,
            text_color=colors.role_error_text,
        ),
    }
    return role_styles.get(role, role_styles["assistant"])


# =============================================================================
# Widget Style Functions (use current theme)
# =============================================================================

def button_style(
    bg_color: str | None = None,
    text_color: str | None = None,
    hover_color: str | None = None,
    border_color: str | None = None,
    border_radius: int = 6,
    padding: str = "8px 16px",
) -> str:
    """Generate button stylesheet."""
    colors = _theme_manager.current
    bg_color = bg_color or colors.bg_tertiary
    text_color = text_color or colors.text_primary
    hover_color = hover_color or "#4d4d4d"
    border = f"1px solid {border_color}" if border_color else "none"
    return f"""
        QPushButton {{
            background-color: {bg_color};
            color: {text_color};
            border: {border};
            border-radius: {border_radius}px;
            padding: {padding};
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
        QPushButton:disabled {{
            background-color: {colors.bg_secondary};
            color: {colors.text_muted};
        }}
    """


def input_style(
    bg_color: str | None = None,
    text_color: str | None = None,
    border_color: str | None = None,
    focus_color: str | None = None,
    border_radius: int = 8,
    padding: str = "8px",
    font_size: str = "14px",
) -> str:
    """Generate input field stylesheet."""
    colors = _theme_manager.current
    bg_color = bg_color or colors.bg_input
    text_color = text_color or colors.text_primary
    border_color = border_color or colors.border_default
    focus_color = focus_color or colors.border_focus
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


def get_main_window_style() -> str:
    """Get main window style for current theme."""
    colors = _theme_manager.current
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
        }}
    """


def get_send_button_style() -> str:
    """Get send button style for current theme."""
    colors = _theme_manager.current
    return button_style(
        bg_color=colors.accent_primary,
        text_color="white",
        hover_color=colors.accent_primary_hover,
    )


def get_cancel_button_style() -> str:
    """Get cancel button style for current theme."""
    colors = _theme_manager.current
    return button_style(
        bg_color=colors.accent_error,
        text_color="white",
        hover_color=colors.accent_error_hover,
    )


def get_attach_button_style() -> str:
    """Get attach button style for current theme."""
    colors = _theme_manager.current
    return button_style(
        bg_color=colors.bg_tertiary,
        text_color=colors.text_primary,
        border_color=colors.border_default,
    )


# Static styles that work across themes
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

# =============================================================================
# Thinking & Tool Call Section Styles
# =============================================================================

def get_thinking_section_style() -> str:
    """Get thinking section frame style for current theme."""
    colors = _theme_manager.current
    return f"""
        ThinkingSection {{
            background-color: {colors.role_thinking_bg};
            border: 1px solid {colors.role_thinking_text}40;
            border-radius: 8px;
        }}
    """


def get_tool_call_section_style() -> str:
    """Get tool call section frame style for current theme."""
    colors = _theme_manager.current
    return f"""
        ToolCallSection {{
            background-color: {colors.role_tool_bg};
            border: 1px solid {colors.role_tool_text}40;
            border-radius: 8px;
        }}
    """


def get_collapsible_toggle_style(accent_color: str) -> str:
    """Get collapsible toggle button style."""
    return f"""
        QPushButton {{
            background-color: transparent;
            border: none;
            color: {accent_color};
            font-size: 12px;
        }}
        QPushButton:hover {{
            background-color: {accent_color}33;
            border-radius: 4px;
        }}
    """


def get_section_icon_style(color: str) -> str:
    """Get section icon label style."""
    return f"color: {color}; font-size: 14px;"


def get_section_title_style(color: str) -> str:
    """Get section title label style."""
    return f"color: {color}; font-weight: bold; font-size: 13px;"


def get_thinking_text_style() -> str:
    """Get thinking section text edit style for current theme."""
    colors = _theme_manager.current
    return f"""
        QPlainTextEdit {{
            background-color: transparent;
            border: none;
            color: {colors.text_secondary};
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 12px;
        }}
    """


def get_tool_args_text_style() -> str:
    """Get tool arguments text edit style for current theme."""
    colors = _theme_manager.current
    return f"""
        QPlainTextEdit {{
            background-color: rgba(0, 0, 0, 0.2);
            border: none;
            color: {colors.text_secondary};
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 12px;
            border-radius: 4px;
            padding: 4px;
        }}
    """


# =============================================================================
# File Tree Styles
# =============================================================================

def get_file_tree_filter_style() -> str:
    """Get file tree filter input style for current theme."""
    colors = _theme_manager.current
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
# Attachment Chip Styles
# =============================================================================

def get_attachment_chip_style() -> str:
    """Get attachment chip container style for current theme."""
    colors = _theme_manager.current
    return f"""
        QFrame {{
            background-color: {colors.bg_tertiary};
            border-radius: 4px;
            padding: 2px 4px;
        }}
    """


def get_attachment_label_style() -> str:
    """Get attachment label style for current theme."""
    colors = _theme_manager.current
    return f"""
        QLabel {{
            color: {colors.text_primary};
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
# Dialog Styles
# =============================================================================

def get_dialog_style() -> str:
    """Get standard dialog style for current theme."""
    colors = _theme_manager.current
    return f"""
        QDialog {{
            background-color: {colors.bg_primary};
        }}
        QLabel {{
            color: {colors.text_primary};
        }}
        QGroupBox {{
            color: {colors.text_primary};
            border: 1px solid {colors.border_default};
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 8px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px;
        }}
        QLineEdit {{
            background-color: {colors.bg_input};
            color: {colors.text_primary};
            border: 1px solid {colors.border_default};
            border-radius: 4px;
            padding: 6px;
        }}
        QLineEdit:focus {{
            border-color: {colors.border_focus};
        }}
        QComboBox {{
            background-color: {colors.bg_input};
            color: {colors.text_primary};
            border: 1px solid {colors.border_default};
            border-radius: 4px;
            padding: 6px;
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox QAbstractItemView {{
            background-color: {colors.bg_secondary};
            color: {colors.text_primary};
            selection-background-color: {colors.accent_primary};
        }}
        QTextEdit {{
            background-color: {colors.bg_input};
            color: {colors.text_primary};
            border: 1px solid {colors.border_default};
            border-radius: 4px;
        }}
        QListWidget {{
            background-color: {colors.bg_secondary};
            color: {colors.text_primary};
            border: 1px solid {colors.border_default};
            border-radius: 4px;
        }}
        QListWidget::item:selected {{
            background-color: {colors.accent_primary};
        }}
    """


def get_section_label_style() -> str:
    """Get section label style for current theme."""
    colors = _theme_manager.current
    return f"font-weight: bold; color: {colors.text_secondary};"


def get_panel_title_style() -> str:
    """Get panel title style for current theme."""
    colors = _theme_manager.current
    return f"font-weight: bold; color: {colors.text_primary}; padding: 4px;"


def get_subsection_label_style() -> str:
    """Get subsection label style for current theme."""
    colors = _theme_manager.current
    return f"font-size: 11px; color: {colors.text_secondary};"


def get_validation_error_style() -> str:
    """Get validation error label style for current theme."""
    colors = _theme_manager.current
    return f"color: {colors.accent_error};"


def get_icon_button_style() -> str:
    """Get icon-only button style for current theme."""
    colors = _theme_manager.current
    return f"""
        QPushButton {{
            background-color: transparent;
            border: none;
            color: {colors.text_secondary};
            font-size: 14px;
            padding: 4px;
        }}
        QPushButton:hover {{
            background-color: {colors.bg_tertiary};
            border-radius: 4px;
        }}
    """


# =============================================================================
# Modern Chat Bubble Styles
# =============================================================================

def get_message_bubble_style(is_user: bool, is_tool: bool = False) -> str:
    """Get full-width message card style.

    Args:
        is_user: Whether this is a user message
        is_tool: Whether this is a tool/thinking message

    Returns:
        CSS style string for the message card
    """
    colors = _theme_manager.current

    # Use accent_primary (blue) for user, neutral gray for others
    if is_user:
        border_color = colors.accent_primary
    else:
        border_color = colors.border_default

    return f"""
        MessageWidget {{
            background-color: {colors.bg_secondary};
            border-left: 3px solid {border_color};
            border-top: none;
            border-right: none;
            border-bottom: none;
            border-radius: 0px;
            margin: 2px 8px;
            padding: 0px;
        }}
        MessageWidget QLabel {{
            background-color: transparent;
            border: none;
        }}
        MessageWidget QPushButton {{
            background-color: transparent;
            border: none;
        }}
        MessageWidget QTextBrowser {{
            background-color: transparent;
            border: none;
        }}
    """


def get_bubble_content_style(is_user: bool) -> str:
    """Get content text style for message card."""
    colors = _theme_manager.current
    return f"""
        QTextBrowser {{
            background-color: transparent;
            color: {colors.text_primary};
            border: none;
            padding: 4px 0px;
            font-family: 'Segoe UI', -apple-system, sans-serif;
            font-size: 14px;
        }}
    """


def get_bubble_header_style(is_user: bool, role_color: str) -> str:
    """Get header style for bubble (role indicator)."""
    return f"""
        QLabel {{
            color: {role_color};
            font-size: 11px;
            font-weight: 600;
            padding: 8px 16px 0px 16px;
            background: transparent;
        }}
    """


def get_shadow_effect_params() -> dict:
    """Get parameters for QGraphicsDropShadowEffect.

    Returns:
        Dict with blur_radius, x_offset, y_offset, color
    """
    colors = _theme_manager.current
    # Use darker shadow for light themes, subtle for dark
    is_light = colors.name == "Light"
    return {
        "blur_radius": 20 if is_light else 15,
        "x_offset": 0,
        "y_offset": 4 if is_light else 2,
        "color": "rgba(0, 0, 0, 0.15)" if is_light else "rgba(0, 0, 0, 0.3)",
    }


# =============================================================================
# Modern Input Area Styles
# =============================================================================

def get_modern_input_container_style() -> str:
    """Get modern floating input container style."""
    colors = _theme_manager.current
    return f"""
        QWidget {{
            background-color: {colors.bg_primary};
        }}
    """


def get_modern_input_field_style() -> str:
    """Get modern input field style with rounded corners."""
    colors = _theme_manager.current
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


# =============================================================================
# Collapsible Sidebar Styles
# =============================================================================

def get_sidebar_container_style() -> str:
    """Get collapsible sidebar container style."""
    colors = _theme_manager.current
    return f"""
        QWidget {{
            background-color: {colors.bg_secondary};
            border-right: 1px solid {colors.border_subtle};
        }}
    """


def get_sidebar_toggle_button_style() -> str:
    """Get sidebar toggle button style."""
    colors = _theme_manager.current
    return f"""
        QPushButton {{
            background-color: {colors.bg_tertiary};
            color: {colors.text_secondary};
            border: none;
            border-radius: 4px;
            padding: 8px;
            font-size: 14px;
            min-width: 32px;
            min-height: 32px;
        }}
        QPushButton:hover {{
            background-color: {colors.accent_primary};
            color: white;
        }}
    """


def get_sidebar_icon_button_style(active: bool = False) -> str:
    """Get sidebar icon button style for collapsed mode."""
    colors = _theme_manager.current
    bg = colors.accent_primary if active else "transparent"
    text = "white" if active else colors.text_secondary
    hover_bg = colors.accent_primary_hover if active else colors.bg_tertiary
    return f"""
        QPushButton {{
            background-color: {bg};
            color: {text};
            border: none;
            border-radius: 8px;
            padding: 10px;
            font-size: 18px;
            min-width: 44px;
            min-height: 44px;
            max-width: 44px;
            max-height: 44px;
        }}
        QPushButton:hover {{
            background-color: {hover_bg};
            color: white;
        }}
    """


# Backwards compatibility - these now call functions
MAIN_WINDOW_STYLE = get_main_window_style()
SCROLL_AREA_STYLE = get_scroll_area_style()
CONTENT_BROWSER_STYLE = get_content_browser_style()
SEND_BUTTON_STYLE = get_send_button_style()
CANCEL_BUTTON_STYLE = get_cancel_button_style()
ATTACH_BUTTON_STYLE = get_attach_button_style()
