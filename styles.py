"""Centralized styles for the desktop application.

This module provides a single source of truth for all colors, fonts,
and widget styles used throughout the desktop app.

Supports both flat and neumorphism design systems.
"""

from dataclasses import dataclass
from typing import Callable, NamedTuple


class ColorScheme(NamedTuple):
    """Color scheme for the application."""
    # Theme metadata
    name: str = "Dark"
    is_neumorphic: bool = False

    # Backgrounds
    bg_primary: str = "#1e1e1e"
    bg_secondary: str = "#2d2d2d"
    bg_tertiary: str = "#3d3d3d"
    bg_input: str = "#3d3d3d"
    bg_content: str = "#252526"
    bg_code: str = "#1e1e1e"

    # Neumorphism shadow colors (for soft UI effect)
    shadow_light: str = "#3a3a3a"  # Highlight shadow (top-left)
    shadow_dark: str = "#0a0a0a"   # Dark shadow (bottom-right)

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
    is_neumorphic=False,
    bg_primary="#1e1e1e",
    bg_secondary="#2d2d2d",
    bg_tertiary="#3d3d3d",
    bg_input="#3d3d3d",
    bg_content="#252526",
    bg_code="#1e1e1e",
    shadow_light="#3a3a3a",
    shadow_dark="#0a0a0a",
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
    is_neumorphic=False,
    bg_primary="#ffffff",
    bg_secondary="#f5f5f5",
    bg_tertiary="#e8e8e8",
    bg_input="#ffffff",
    bg_content="#fafafa",
    bg_code="#f5f5f5",
    shadow_light="#ffffff",
    shadow_dark="#c8c8c8",
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

# =============================================================================
# Neumorphism Themes
# =============================================================================

THEME_NEUMORPHIC_DARK = ColorScheme(
    name="Neumorphic Dark",
    is_neumorphic=True,
    # Base: dark charcoal gray
    bg_primary="#2a2a32",
    bg_secondary="#2a2a32",  # Same as primary for neumorphism
    bg_tertiary="#32323c",
    bg_input="#2a2a32",
    bg_content="#2a2a32",
    bg_code="#222228",
    # Neumorphic shadows - MORE CONTRAST for stronger 3D effect
    shadow_light="#404050",  # Brighter highlight (more visible)
    shadow_dark="#16161c",   # Deeper shadow (more contrast)
    # Borders (minimal in neumorphism)
    border_default="#404050",
    border_subtle="#32323c",
    border_focus="#e091a3",
    # Text
    text_primary="#e8e8e8",
    text_secondary="#a0a0a8",
    text_muted="#6a6a72",
    text_code="#e091a3",
    # Accents - Soft pink theme
    accent_primary="#e091a3",      # Soft pink
    accent_primary_hover="#d17a8e",
    accent_success="#4ade80",
    accent_warning="#fbbf24",
    accent_error="#ef4444",
    accent_error_hover="#dc2626",
    accent_info="#7eb8da",
    # Role colors - soft pastels
    role_user_bg="#7eb8da",        # Soft blue for user
    role_user_text="white",
    role_assistant_bg="#f0d87a",   # Soft yellow for assistant
    role_assistant_text="#e8e8e8",
    role_thinking_bg="#e091a3",    # Soft pink for thinking
    role_thinking_text="#a0a0a8",
    role_tool_bg="#e091a3",        # Soft pink for tools
    role_tool_text="#e091a3",
    role_tool_output_bg="#e091a3", # Soft pink for tool output
    role_tool_output_text="#e091a3",
    role_error_bg="#ef4444",       # Red for errors
    role_error_text="#f87171",
)

THEME_NEUMORPHIC_LIGHT = ColorScheme(
    name="Neumorphic Light",
    is_neumorphic=True,
    # Base: soft gray
    bg_primary="#e0e5ec",
    bg_secondary="#e0e5ec",  # Same as primary for neumorphism
    bg_tertiary="#d1d9e6",
    bg_input="#e0e5ec",
    bg_content="#e0e5ec",
    bg_code="#d8dde5",
    # Neumorphic shadows
    shadow_light="#ffffff",  # White highlight
    shadow_dark="#a3b1c6",   # Blue-gray shadow
    # Borders (minimal in neumorphism)
    border_default="#d1d9e6",
    border_subtle="#d8dde5",
    border_focus="#7c3aed",
    # Text
    text_primary="#3d3d3d",
    text_secondary="#6b6b6b",
    text_muted="#9ca3af",
    text_code="#7c3aed",
    # Accents - Purple theme like the reference
    accent_primary="#7c3aed",
    accent_primary_hover="#6d28d9",
    accent_success="#10b981",
    accent_warning="#f59e0b",
    accent_error="#ef4444",
    accent_error_hover="#dc2626",
    accent_info="#3b82f6",
    # Role colors
    role_user_bg="#7c3aed",
    role_user_text="white",
    role_assistant_bg="#d8dde5",
    role_assistant_text="#3d3d3d",
    role_thinking_bg="#d1d9e6",
    role_thinking_text="#6b6b6b",
    role_tool_bg="#d8dde5",
    role_tool_text="#3b82f6",
    role_tool_output_bg="#d8dde5",
    role_tool_output_text="#3b82f6",
    role_error_bg="#fecaca",
    role_error_text="#dc2626",
)

# All available themes
THEMES: dict[str, ColorScheme] = {
    "Dark": THEME_DARK,
    "Light": THEME_LIGHT,
    "Neumorphic Dark": THEME_NEUMORPHIC_DARK,
    "Neumorphic Light": THEME_NEUMORPHIC_LIGHT,
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
            cls._instance._current_theme = THEME_NEUMORPHIC_DARK  # Default to neumorphic
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

    @property
    def is_neumorphic(self) -> bool:
        """Check if current theme is neumorphic."""
        return self._current_theme.is_neumorphic

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
        "question": RoleStyle(
            background_color=colors.bg_secondary,
            text_color=colors.accent_primary,
        ),
    }
    return role_styles.get(role, role_styles["assistant"])


# =============================================================================
# Neumorphic Button Styles
# =============================================================================

def button_style(
    bg_color: str | None = None,
    text_color: str | None = None,
    hover_color: str | None = None,
    border_color: str | None = None,
    border_radius: int = 6,
    padding: str = "8px 16px",
) -> str:
    """Generate button stylesheet with neumorphic support."""
    colors = _theme_manager.current
    bg_color = bg_color or colors.bg_tertiary
    text_color = text_color or colors.text_primary

    if colors.is_neumorphic:
        # Neumorphic raised button
        hover_color = hover_color or colors.bg_tertiary
        return f"""
            QPushButton {{
                background-color: {colors.bg_primary};
                color: {text_color};
                border: none;
                border-radius: {border_radius + 6}px;
                padding: {padding};
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {colors.bg_primary};
            }}
            QPushButton:disabled {{
                background-color: {colors.bg_primary};
                color: {colors.text_muted};
            }}
        """
    else:
        # Standard flat button
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


def neu_button_raised_style(
    accent_color: str | None = None,
    text_color: str = "white",
    size: str = "medium",
) -> str:
    """Generate neumorphic raised/convex button style.

    Args:
        accent_color: Button accent color (gradient center)
        text_color: Text color
        size: "small", "medium", or "large"
    """
    colors = _theme_manager.current
    accent = accent_color or colors.accent_primary

    # Size presets
    sizes = {
        "small": {"radius": 12, "padding": "8px 14px", "font": "12px"},
        "medium": {"radius": 14, "padding": "10px 20px", "font": "14px"},
        "large": {"radius": 18, "padding": "14px 28px", "font": "16px"},
    }
    s = sizes.get(size, sizes["medium"])

    if colors.is_neumorphic:
        # Beveled button - light top/left, dark bottom/right
        return f"""
            QPushButton {{
                background-color: {colors.bg_primary};
                color: {colors.text_primary};
                border-top: 2px solid {colors.shadow_light};
                border-left: 2px solid {colors.shadow_light};
                border-bottom: 2px solid {colors.shadow_dark};
                border-right: 2px solid {colors.shadow_dark};
                border-radius: {s['radius']}px;
                padding: {s['padding']};
                font-size: {s['font']};
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {colors.bg_tertiary};
                color: {colors.accent_primary};
            }}
            QPushButton:pressed {{
                background-color: {colors.bg_secondary};
                border-top: 2px solid {colors.shadow_dark};
                border-left: 2px solid {colors.shadow_dark};
                border-bottom: 2px solid {colors.shadow_light};
                border-right: 2px solid {colors.shadow_light};
            }}
        """
    else:
        return button_style(accent, text_color, border_radius=s['radius'])


def neu_button_accent_style(
    accent_color: str | None = None,
    text_color: str = "white",
    size: str = "medium",
) -> str:
    """Generate neumorphic accent button (colored, raised)."""
    colors = _theme_manager.current
    accent = accent_color or colors.accent_primary

    sizes = {
        "small": {"radius": 12, "padding": "8px 14px", "font": "12px"},
        "medium": {"radius": 14, "padding": "10px 20px", "font": "14px"},
        "large": {"radius": 18, "padding": "14px 28px", "font": "16px"},
        "circle": {"radius": 16, "padding": "10px 18px", "font": "14px"},
    }
    s = sizes.get(size, sizes["medium"])

    if colors.is_neumorphic:
        # Beveled button - light top/left border, dark bottom/right border
        return f"""
            QPushButton {{
                background-color: {accent};
                color: {text_color};
                border-top: 2px solid #f0a8b8;
                border-left: 2px solid #f0a8b8;
                border-bottom: 2px solid {colors.accent_primary_hover};
                border-right: 2px solid {colors.accent_primary_hover};
                border-radius: {s['radius']}px;
                padding: {s['padding']};
                font-size: {s['font']};
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #e8a0b0;
                border-top: 2px solid #f5b8c5;
                border-left: 2px solid #f5b8c5;
            }}
            QPushButton:pressed {{
                background-color: {colors.accent_primary_hover};
                border-top: 2px solid {colors.accent_primary_hover};
                border-left: 2px solid {colors.accent_primary_hover};
                border-bottom: 2px solid #f0a8b8;
                border-right: 2px solid #f0a8b8;
            }}
            QPushButton:disabled {{
                background-color: {colors.bg_tertiary};
                border-top: 2px solid {colors.shadow_light};
                border-left: 2px solid {colors.shadow_light};
                border-bottom: 2px solid {colors.shadow_dark};
                border-right: 2px solid {colors.shadow_dark};
                color: {colors.text_muted};
            }}
        """
    else:
        return f"""
            QPushButton {{
                background-color: {accent};
                color: {text_color};
                border: none;
                border-radius: {s['radius']}px;
                padding: {s['padding']};
                font-size: {s['font']};
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {colors.accent_primary_hover};
            }}
            QPushButton:pressed {{
                background-color: {colors.accent_primary_hover};
            }}
            QPushButton:disabled {{
                background-color: {colors.bg_tertiary};
                color: {colors.text_muted};
            }}
        """


def neu_button_inset_style(size: str = "medium") -> str:
    """Generate neumorphic inset/concave button style (pressed look)."""
    colors = _theme_manager.current

    sizes = {
        "small": {"radius": 12, "padding": "6px 12px"},
        "medium": {"radius": 16, "padding": "10px 20px"},
        "large": {"radius": 24, "padding": "14px 28px"},
    }
    s = sizes.get(size, sizes["medium"])

    if colors.is_neumorphic:
        return f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_light}
                );
                color: {colors.text_secondary};
                border: none;
                border-radius: {s['radius']}px;
                padding: {s['padding']};
                font-weight: 500;
            }}
            QPushButton:hover {{
                color: {colors.text_primary};
            }}
        """
    else:
        return button_style(colors.bg_tertiary, colors.text_secondary)


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


def get_send_button_style() -> str:
    """Get send button style for current theme."""
    colors = _theme_manager.current
    return neu_button_accent_style(colors.accent_primary, "white", "circle")


def get_cancel_button_style() -> str:
    """Get cancel button style for current theme."""
    colors = _theme_manager.current
    return neu_button_accent_style(colors.accent_error, "white", "medium")


def get_attach_button_style() -> str:
    """Get attach button style for current theme."""
    return neu_button_raised_style(size="small")


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

    if colors.is_neumorphic:
        # Beveled inset style for thinking sections
        return f"""
            ThinkingSection {{
                background-color: {colors.role_thinking_bg};
                border-top: 1px solid {colors.shadow_dark};
                border-left: 1px solid {colors.shadow_dark};
                border-bottom: 1px solid {colors.shadow_light};
                border-right: 1px solid {colors.shadow_light};
                border-radius: 8px;
                margin: 4px;
                padding: 8px;
            }}
            ThinkingSection QWidget {{
                background: transparent;
            }}
            ThinkingSection QLabel {{
                background: transparent;
            }}
            ThinkingSection QPushButton {{
                background: transparent;
            }}
        """
    else:
        return f"""
            ThinkingSection {{
                background-color: {colors.role_thinking_bg};
                border-left: 2px solid {colors.role_thinking_text}60;
                border-radius: 0;
                padding-left: 8px;
            }}
        """


def get_tool_call_section_style() -> str:
    """Get tool call section frame style for current theme."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        # Beveled inset style for tool call sections
        return f"""
            ToolCallSection {{
                background-color: {colors.role_tool_bg};
                border-top: 1px solid {colors.shadow_dark};
                border-left: 1px solid {colors.shadow_dark};
                border-bottom: 1px solid {colors.shadow_light};
                border-right: 1px solid {colors.shadow_light};
                border-radius: 8px;
                margin: 4px;
                padding: 8px;
            }}
            ToolCallSection QWidget {{
                background: transparent;
            }}
            ToolCallSection QLabel {{
                background: transparent;
            }}
            ToolCallSection QPushButton {{
                background: transparent;
            }}
        """
    else:
        return f"""
            ToolCallSection {{
                background-color: {colors.role_tool_bg};
                border-left: 2px solid {colors.role_tool_text}60;
                border-radius: 0;
                padding-left: 8px;
            }}
        """


def get_collapsible_toggle_style(accent_color: str) -> str:
    """Get collapsible toggle button style."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {accent_color};
                font-size: 12px;
                padding: 4px 8px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_light},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_dark}
                );
            }}
        """
    else:
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

    if colors.is_neumorphic:
        return f"""
            QPlainTextEdit {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_light}
                );
                border: none;
                color: {colors.text_secondary};
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border-radius: 12px;
                padding: 8px;
            }}
        """
    else:
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
        # Dark pink sidebar material
        sidebar_material = "#3a2832"
        sidebar_hover = "#4a3842"
        sidebar_selected = "#5a4852"

        # Flat non-rounded style for consistency with list items
        return f"""
            QTreeView {{
                background-color: {sidebar_material};
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
                background-color: {sidebar_hover};
            }}
            QTreeView::item:selected {{
                background-color: {sidebar_selected};
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
        # Dark pink sidebar material
        sidebar_material = "#3a2832"

        # Beveled tabs like sidebar icon buttons
        return f"""
            QTabWidget::pane {{
                border: none;
                background-color: {sidebar_material};
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
# Dialog Styles
# =============================================================================

def get_dialog_style() -> str:
    """Get standard dialog style for current theme."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            QDialog {{
                background-color: {colors.bg_primary};
            }}
            QLabel {{
                color: {colors.text_primary};
            }}
            QGroupBox {{
                color: {colors.text_primary};
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_light},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_dark}
                );
                border: none;
                border-radius: 16px;
                margin-top: 12px;
                padding: 16px;
                padding-top: 24px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: {colors.accent_primary};
            }}
            QLineEdit {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_light}
                );
                color: {colors.text_primary};
                border: none;
                border-radius: 12px;
                padding: 10px 16px;
            }}
            QComboBox {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_light},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_dark}
                );
                color: {colors.text_primary};
                border: none;
                border-radius: 12px;
                padding: 10px 16px;
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {colors.bg_primary};
                color: {colors.text_primary};
                selection-background-color: {colors.accent_primary};
                border: none;
                border-radius: 12px;
                padding: 4px;
            }}
            QTextEdit {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_light}
                );
                color: {colors.text_primary};
                border: none;
                border-radius: 12px;
                padding: 8px;
            }}
            QListWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_light}
                );
                color: {colors.text_primary};
                border: none;
                border-radius: 12px;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 8px;
                margin: 2px;
            }}
            QListWidget::item:selected {{
                background: {colors.accent_primary};
            }}
            QSpinBox, QDoubleSpinBox {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_light}
                );
                color: {colors.text_primary};
                border: none;
                border-radius: 12px;
                padding: 8px 12px;
            }}
            QCheckBox {{
                color: {colors.text_primary};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
                border-radius: 11px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_light}
                );
            }}
            QCheckBox::indicator:checked {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.accent_primary},
                    stop:1 {colors.accent_primary_hover}
                );
            }}
            QSlider::groove:horizontal {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_light}
                );
                height: 10px;
                border-radius: 5px;
            }}
            QSlider::handle:horizontal {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_light},
                    stop:0.5 {colors.bg_tertiary},
                    stop:1 {colors.shadow_dark}
                );
                width: 22px;
                height: 22px;
                margin: -6px 0;
                border-radius: 11px;
            }}
            QSlider::handle:horizontal:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_light},
                    stop:0.5 {colors.accent_primary},
                    stop:1 {colors.shadow_dark}
                );
            }}
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_light},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_dark}
                );
                color: {colors.text_primary};
                border: none;
                border-radius: 14px;
                padding: 10px 20px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_light},
                    stop:0.4 {colors.bg_tertiary},
                    stop:1 {colors.shadow_dark}
                );
            }}
            QPushButton:pressed {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_light}
                );
            }}
            QPushButton:default {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.accent_primary},
                    stop:1 {colors.accent_primary_hover}
                );
                color: white;
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
        """
    else:
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

    if colors.is_neumorphic:
        return f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {colors.text_secondary};
                font-size: 16px;
                padding: 8px;
                border-radius: 12px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_light},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_dark}
                );
                color: {colors.text_primary};
            }}
        """
    else:
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

def get_message_bubble_style(is_user: bool, is_tool: bool = False, role: str = "") -> str:
    """Get message card style with neumorphic support and color accents.

    Args:
        is_user: Whether this is a user message
        is_tool: Whether this is a tool/thinking message
        role: Message role string (user, assistant, thinking, tool_call, tool_output, error)
    """
    colors = _theme_manager.current

    # Determine accent color based on role
    if role == "user":
        accent_color = colors.role_user_bg
    elif role == "assistant":
        accent_color = colors.role_assistant_bg
    elif role == "thinking":
        accent_color = colors.role_thinking_bg
    elif role in ("tool_call", "tool_output"):
        accent_color = colors.role_tool_bg
    elif role == "error":
        accent_color = colors.role_error_bg
    else:
        accent_color = colors.accent_primary if is_user else colors.role_assistant_bg

    if colors.is_neumorphic:
        # Beveled style with colored left accent strip
        if is_user:
            return f"""
                MessageWidget {{
                    background-color: {colors.bg_primary};
                    border-left: 4px solid {accent_color};
                    border-top: 1px solid {colors.shadow_light};
                    border-right: 1px solid {colors.shadow_dark};
                    border-bottom: 1px solid {colors.shadow_dark};
                    border-radius: 8px;
                    margin: 4px 12px;
                    padding: 4px;
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
        else:
            return f"""
                MessageWidget {{
                    background-color: {colors.bg_secondary};
                    border-left: 4px solid {accent_color};
                    border-top: 1px solid {colors.shadow_dark};
                    border-right: 1px solid {colors.shadow_light};
                    border-bottom: 1px solid {colors.shadow_light};
                    border-radius: 8px;
                    margin: 4px 12px;
                    padding: 4px;
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
    else:
        # Standard flat style
        border_color = accent_color

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
    """Get parameters for QGraphicsDropShadowEffect."""
    colors = _theme_manager.current
    is_light = "Light" in colors.name

    if colors.is_neumorphic:
        return {
            "blur_radius": 20,
            "x_offset": 8,
            "y_offset": 8,
            "color": colors.shadow_dark,
        }
    else:
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


# =============================================================================
# Collapsible Sidebar Styles
# =============================================================================

def get_sidebar_container_style() -> str:
    """Get collapsible sidebar content panel - recessed pocket in device."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        # Dark pink recessed pocket with inset bevel on all sides
        # Inset = dark on top/left (shadow), light on bottom/right (highlight)
        sidebar_material = "#3a2832"
        inset_dark = "#1a1a1e"  # Dark for top/left shadow
        inset_light = "#4a4a58"  # Light for bottom/right highlight
        return f"""
            QFrame#content_wrapper {{
                background-color: {sidebar_material};
                border-top: 3px solid {inset_dark};
                border-left: 3px solid {inset_dark};
                border-bottom: 3px solid {inset_light};
                border-right: 3px solid {inset_light};
                border-radius: 12px;
                margin: 4px;
                padding: 2px;
            }}
            QFrame {{
                background-color: {sidebar_material};
                border: none;
            }}
            QWidget {{
                background-color: {sidebar_material};
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
        # Dark gray - the device body/chassis
        # Unselected tabs sit ON this surface as raised labels
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
        # Dark gray device body with accent border
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
    """Get sidebar toggle button style."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        # Beveled button with warm tint
        return f"""
            QPushButton {{
                background-color: #3a3038;
                color: {colors.text_primary};
                border-top: 2px solid {colors.shadow_light};
                border-left: 2px solid {colors.shadow_light};
                border-bottom: 2px solid {colors.shadow_dark};
                border-right: 2px solid {colors.shadow_dark};
                border-radius: 14px;
                padding: 12px;
                font-size: 22px;
                min-width: 50px;
                min-height: 50px;
            }}
            QPushButton:hover {{
                background-color: #453a42;
            }}
            QPushButton:pressed {{
                background-color: #322830;
                border-top: 2px solid {colors.shadow_dark};
                border-left: 2px solid {colors.shadow_dark};
                border-bottom: 2px solid {colors.shadow_light};
                border-right: 2px solid {colors.shadow_light};
            }}
        """
    else:
        return f"""
            QPushButton {{
                background-color: {colors.bg_tertiary};
                color: {colors.text_primary};
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 20px;
                min-width: 44px;
                min-height: 44px;
            }}
            QPushButton:hover {{
                background-color: {colors.accent_primary};
                color: white;
            }}
        """


def get_sidebar_icon_button_style(active: bool = False) -> str:
    """Get sidebar icon button style for collapsed mode."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        # Beveled button styles
        if active:
            # Selected tab - rounded recessed square
            sidebar_material = "#3a2832"
            inset_dark = "#1a1a1e"
            inset_light = "#4a4a58"
            return f"""
                QPushButton {{
                    background-color: {sidebar_material};
                    color: {colors.accent_primary};
                    border-top: 3px solid {inset_dark};
                    border-left: 3px solid {inset_dark};
                    border-bottom: 3px solid {inset_light};
                    border-right: 3px solid {inset_light};
                    border-radius: 16px;
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
            # Unselected tabs - flat painted labels on device body (no bevel, just icon)
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {colors.text_secondary};
                    border: none;
                    padding: 12px;
                    font-size: 28px;
                    min-width: 56px;
                    min-height: 56px;
                    max-width: 56px;
                    max-height: 56px;
                }}
                QPushButton:hover {{
                    color: {colors.accent_primary};
                }}
            """
    else:
        bg = "#4a4a4a" if active else "transparent"
        text = "white" if active else colors.text_primary
        hover_bg = "#5a5a5a" if active else colors.bg_tertiary
        return f"""
            QPushButton {{
                background-color: {bg};
                color: {text};
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
                background-color: {hover_bg};
                color: white;
            }}
        """


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


# DEPRECATED: These module-level constants are evaluated at import time.
# They're kept for backwards compatibility but code should migrate to using
# the function versions (get_main_window_style(), etc.) to support theme changes.
MAIN_WINDOW_STYLE = get_main_window_style()
SCROLL_AREA_STYLE = get_scroll_area_style()
CONTENT_BROWSER_STYLE = get_content_browser_style()
SEND_BUTTON_STYLE = get_send_button_style()
CANCEL_BUTTON_STYLE = get_cancel_button_style()
ATTACH_BUTTON_STYLE = get_attach_button_style()
