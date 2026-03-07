"""Color schemes and theme management.

This module contains:
- ColorScheme NamedTuple
- Preset themes (Dark, Light, Neumorphic Dark, Neumorphic Light)
- ThemeManager singleton
- COLORS dynamic proxy
"""

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
