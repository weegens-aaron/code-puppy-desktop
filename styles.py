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
    border_focus="#1a73e8",
    text_primary="#e0e0e0",
    text_secondary="#a0a0a0",
    text_muted="#6a6a6a",
    text_code="#ce9178",
    accent_primary="#1a73e8",
    accent_primary_hover="#1565c0",
    accent_success="#90EE90",
    accent_warning="#ffc107",
    accent_error="#d32f2f",
    accent_error_hover="#b71c1c",
    accent_info="#4fc3f7",
    role_user_bg="#1a73e8",
    role_user_text="white",
    role_assistant_bg="#2d5016",
    role_assistant_text="#90EE90",
    role_thinking_bg="#5c4d2b",
    role_thinking_text="#ffc107",
    role_tool_bg="#1e3a5f",
    role_tool_text="#4fc3f7",
    role_tool_output_bg="#1e3a5f",
    role_tool_output_text="#4fc3f7",
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
    border_focus="#1a73e8",
    text_primary="#1a1a1a",
    text_secondary="#505050",
    text_muted="#909090",
    text_code="#c41a16",
    accent_primary="#1a73e8",
    accent_primary_hover="#1565c0",
    accent_success="#2e7d32",
    accent_warning="#f57c00",
    accent_error="#c62828",
    accent_error_hover="#b71c1c",
    accent_info="#0288d1",
    role_user_bg="#1a73e8",
    role_user_text="white",
    role_assistant_bg="#e8f5e9",
    role_assistant_text="#1b5e20",
    role_thinking_bg="#fff8e1",
    role_thinking_text="#e65100",
    role_tool_bg="#e3f2fd",
    role_tool_text="#0d47a1",
    role_tool_output_bg="#e3f2fd",
    role_tool_output_text="#0d47a1",
    role_error_bg="#ffebee",
    role_error_text="#c62828",
)

THEME_DRACULA = ColorScheme(
    name="Dracula",
    bg_primary="#282a36",
    bg_secondary="#343746",
    bg_tertiary="#44475a",
    bg_input="#44475a",
    bg_content="#282a36",
    bg_code="#21222c",
    border_default="#6272a4",
    border_subtle="#44475a",
    border_focus="#bd93f9",
    text_primary="#f8f8f2",
    text_secondary="#bfbfbf",
    text_muted="#6272a4",
    text_code="#f1fa8c",
    accent_primary="#bd93f9",
    accent_primary_hover="#a77de8",
    accent_success="#50fa7b",
    accent_warning="#ffb86c",
    accent_error="#ff5555",
    accent_error_hover="#ff3333",
    accent_info="#8be9fd",
    role_user_bg="#bd93f9",
    role_user_text="#282a36",
    role_assistant_bg="#2a4030",
    role_assistant_text="#50fa7b",
    role_thinking_bg="#4a3a20",
    role_thinking_text="#ffb86c",
    role_tool_bg="#2a3a4a",
    role_tool_text="#8be9fd",
    role_tool_output_bg="#2a3a4a",
    role_tool_output_text="#8be9fd",
    role_error_bg="#4a2020",
    role_error_text="#ff5555",
)

THEME_NORD = ColorScheme(
    name="Nord",
    bg_primary="#2e3440",
    bg_secondary="#3b4252",
    bg_tertiary="#434c5e",
    bg_input="#3b4252",
    bg_content="#2e3440",
    bg_code="#2e3440",
    border_default="#4c566a",
    border_subtle="#3b4252",
    border_focus="#88c0d0",
    text_primary="#eceff4",
    text_secondary="#d8dee9",
    text_muted="#4c566a",
    text_code="#a3be8c",
    accent_primary="#88c0d0",
    accent_primary_hover="#81b9c9",
    accent_success="#a3be8c",
    accent_warning="#ebcb8b",
    accent_error="#bf616a",
    accent_error_hover="#a85460",
    accent_info="#81a1c1",
    role_user_bg="#5e81ac",
    role_user_text="#eceff4",
    role_assistant_bg="#3a4530",
    role_assistant_text="#a3be8c",
    role_thinking_bg="#4a4530",
    role_thinking_text="#ebcb8b",
    role_tool_bg="#3a4555",
    role_tool_text="#88c0d0",
    role_tool_output_bg="#3a4555",
    role_tool_output_text="#88c0d0",
    role_error_bg="#4a3035",
    role_error_text="#bf616a",
)

THEME_MONOKAI = ColorScheme(
    name="Monokai",
    bg_primary="#272822",
    bg_secondary="#3e3d32",
    bg_tertiary="#49483e",
    bg_input="#3e3d32",
    bg_content="#272822",
    bg_code="#1e1f1c",
    border_default="#75715e",
    border_subtle="#49483e",
    border_focus="#a6e22e",
    text_primary="#f8f8f2",
    text_secondary="#cfcfc2",
    text_muted="#75715e",
    text_code="#e6db74",
    accent_primary="#a6e22e",
    accent_primary_hover="#98d421",
    accent_success="#a6e22e",
    accent_warning="#e6db74",
    accent_error="#f92672",
    accent_error_hover="#e01f63",
    accent_info="#66d9ef",
    role_user_bg="#ae81ff",
    role_user_text="#272822",
    role_assistant_bg="#3a4520",
    role_assistant_text="#a6e22e",
    role_thinking_bg="#4a4520",
    role_thinking_text="#e6db74",
    role_tool_bg="#2a3a4a",
    role_tool_text="#66d9ef",
    role_tool_output_bg="#2a3a4a",
    role_tool_output_text="#66d9ef",
    role_error_bg="#4a2030",
    role_error_text="#f92672",
)

THEME_SOLARIZED_DARK = ColorScheme(
    name="Solarized Dark",
    bg_primary="#002b36",
    bg_secondary="#073642",
    bg_tertiary="#094555",
    bg_input="#073642",
    bg_content="#002b36",
    bg_code="#001e26",
    border_default="#586e75",
    border_subtle="#073642",
    border_focus="#268bd2",
    text_primary="#839496",
    text_secondary="#657b83",
    text_muted="#586e75",
    text_code="#2aa198",
    accent_primary="#268bd2",
    accent_primary_hover="#2080c5",
    accent_success="#859900",
    accent_warning="#b58900",
    accent_error="#dc322f",
    accent_error_hover="#cb2825",
    accent_info="#2aa198",
    role_user_bg="#268bd2",
    role_user_text="#fdf6e3",
    role_assistant_bg="#1a3520",
    role_assistant_text="#859900",
    role_thinking_bg="#3a3520",
    role_thinking_text="#b58900",
    role_tool_bg="#0a3545",
    role_tool_text="#2aa198",
    role_tool_output_bg="#0a3545",
    role_tool_output_text="#2aa198",
    role_error_bg="#3a2020",
    role_error_text="#dc322f",
)

THEME_GITHUB_DARK = ColorScheme(
    name="GitHub Dark",
    bg_primary="#0d1117",
    bg_secondary="#161b22",
    bg_tertiary="#21262d",
    bg_input="#21262d",
    bg_content="#0d1117",
    bg_code="#161b22",
    border_default="#30363d",
    border_subtle="#21262d",
    border_focus="#58a6ff",
    text_primary="#c9d1d9",
    text_secondary="#8b949e",
    text_muted="#484f58",
    text_code="#a5d6ff",
    accent_primary="#58a6ff",
    accent_primary_hover="#4d9aef",
    accent_success="#3fb950",
    accent_warning="#d29922",
    accent_error="#f85149",
    accent_error_hover="#e0463e",
    accent_info="#58a6ff",
    role_user_bg="#238636",
    role_user_text="#ffffff",
    role_assistant_bg="#1a3020",
    role_assistant_text="#3fb950",
    role_thinking_bg="#3a3520",
    role_thinking_text="#d29922",
    role_tool_bg="#1a2535",
    role_tool_text="#58a6ff",
    role_tool_output_bg="#1a2535",
    role_tool_output_text="#58a6ff",
    role_error_bg="#3a1a1a",
    role_error_text="#f85149",
)

# All available themes
THEMES: dict[str, ColorScheme] = {
    "Dark": THEME_DARK,
    "Light": THEME_LIGHT,
    "Dracula": THEME_DRACULA,
    "Nord": THEME_NORD,
    "Monokai": THEME_MONOKAI,
    "Solarized Dark": THEME_SOLARIZED_DARK,
    "GitHub Dark": THEME_GITHUB_DARK,
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
    """Get scroll area style for current theme."""
    colors = _theme_manager.current
    return f"""
        QScrollArea {{
            background-color: {colors.bg_primary};
            border: none;
        }}
        QScrollBar:vertical {{
            background-color: {colors.bg_secondary};
            width: 10px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {colors.border_default};
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {colors.text_muted};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
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

# Backwards compatibility - these now call functions
MAIN_WINDOW_STYLE = get_main_window_style()
SCROLL_AREA_STYLE = get_scroll_area_style()
CONTENT_BROWSER_STYLE = get_content_browser_style()
SEND_BUTTON_STYLE = get_send_button_style()
CANCEL_BUTTON_STYLE = get_cancel_button_style()
ATTACH_BUTTON_STYLE = get_attach_button_style()
