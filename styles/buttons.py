"""Unified button styles with neumorphic support.

Button Variants (3 color ways):
- "primary" - Main action (pink/accent_primary color)
- "neutral" - Secondary action (gray)
- "ghost" - Transparent background (icon buttons in headers)

Legacy variants mapped for compatibility:
- "success", "error" → "primary"
- "warning" → "neutral"

Button Sizes:
- "icon-sm" - 28x28 icon button
- "icon-md" - 32x32 icon button
- "icon-lg" - 44x44 icon button
- "sm" - Small text button
- "md" - Medium text button (default)
- "lg" - Large text button
"""

from styles.colors import get_theme_manager
from styles.primitives import SIDEBAR_MATERIAL, SIDEBAR_HOVER, INSET_DARK, INSET_LIGHT

_theme_manager = get_theme_manager()


# =============================================================================
# Variant Colors
# =============================================================================

def _get_variant_colors(variant: str) -> dict:
    """Get colors for a button variant.

    Only 3 color ways: primary (pink), neutral (gray), ghost (transparent).
    Legacy variants are mapped for compatibility.
    """
    colors = _theme_manager.current

    # Map legacy variants to the 3 supported color ways
    variant_map = {
        "success": "primary",  # Green → Pink
        "error": "primary",    # Red → Pink
        "warning": "neutral",  # Orange → Gray
    }
    variant = variant_map.get(variant, variant)

    variants = {
        "primary": {
            "bg": colors.accent_primary,
            "bg_hover": colors.accent_primary_hover,
            "text": "white",
            "bevel_light": "#f0a8b8",
            "bevel_dark": colors.accent_primary_hover,
        },
        "neutral": {
            "bg": colors.bg_tertiary,
            "bg_hover": "#4d4d4d",
            "text": colors.text_primary,
            "bevel_light": colors.shadow_light,
            "bevel_dark": colors.shadow_dark,
        },
        "ghost": {
            "bg": "transparent",
            "bg_hover": colors.bg_tertiary,
            "text": colors.text_secondary,
            "bevel_light": None,
            "bevel_dark": None,
        },
    }
    return variants.get(variant, variants["neutral"])


# =============================================================================
# Size Presets
# =============================================================================

SIZES = {
    "icon-sm": {"width": 28, "height": 28, "radius": 4, "font": 14, "padding": "0"},
    "icon-md": {"width": 32, "height": 32, "radius": 6, "font": 16, "padding": "0"},
    "icon-lg": {"width": 44, "height": 44, "radius": 8, "font": 20, "padding": "0"},
    "sm": {"width": None, "height": None, "radius": 8, "font": 12, "padding": "6px 12px"},
    "md": {"width": None, "height": None, "radius": 10, "font": 14, "padding": "8px 16px"},
    "lg": {"width": None, "height": None, "radius": 12, "font": 16, "padding": "10px 20px"},
}


# =============================================================================
# Unified Button Style
# =============================================================================

def get_button_style(
    variant: str = "neutral",
    size: str = "md",
    in_sidebar: bool = False,
) -> str:
    """Get unified button stylesheet.

    Args:
        variant: Button variant - "primary" (pink), "neutral" (gray), or "ghost" (transparent).
                 Legacy variants ("success", "error" → primary; "warning" → neutral) are supported.
        size: Button size ("icon-sm", "icon-md", "icon-lg", "sm", "md", "lg")
        in_sidebar: If True, uses sidebar material colors for disabled state

    Returns:
        CSS stylesheet string
    """
    colors = _theme_manager.current
    v = _get_variant_colors(variant)
    s = SIZES.get(size, SIZES["md"])

    # Size constraints for icon buttons
    size_css = ""
    if s["width"]:
        size_css = f"""
            min-width: {s['width']}px;
            max-width: {s['width']}px;
            min-height: {s['height']}px;
            max-height: {s['height']}px;
        """

    # Disabled background based on context
    disabled_bg = SIDEBAR_HOVER if in_sidebar else colors.bg_tertiary

    if colors.is_neumorphic and variant != "ghost":
        # Beveled style for neumorphic theme
        if v["bevel_light"]:
            return f"""
                QPushButton {{
                    background-color: {v['bg']};
                    color: {v['text']};
                    border-top: 2px solid {v['bevel_light']};
                    border-left: 2px solid {v['bevel_light']};
                    border-bottom: 2px solid {v['bevel_dark']};
                    border-right: 2px solid {v['bevel_dark']};
                    border-radius: {s['radius'] + 4}px;
                    padding: {s['padding']};
                    font-size: {s['font']}px;
                    font-weight: 600;
                    {size_css}
                }}
                QPushButton:hover {{
                    background-color: {v['bg_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {SIDEBAR_MATERIAL};
                    border-top: 2px solid {INSET_DARK};
                    border-left: 2px solid {INSET_DARK};
                    border-bottom: 2px solid {INSET_LIGHT};
                    border-right: 2px solid {INSET_LIGHT};
                }}
                QPushButton:disabled {{
                    background-color: {disabled_bg};
                    border-top: 2px solid {colors.shadow_light};
                    border-left: 2px solid {colors.shadow_light};
                    border-bottom: 2px solid {colors.shadow_dark};
                    border-right: 2px solid {colors.shadow_dark};
                    color: {colors.text_muted};
                }}
            """
        else:
            # Ghost variant in neumorphic
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {v['text']};
                    border: none;
                    border-radius: {s['radius']}px;
                    padding: {s['padding']};
                    font-size: {s['font']}px;
                    {size_css}
                }}
                QPushButton:hover {{
                    background-color: {v['bg_hover']};
                    color: {colors.text_primary};
                }}
                QPushButton:pressed {{
                    background-color: {SIDEBAR_MATERIAL};
                    border-top: 2px solid {INSET_DARK};
                    border-left: 2px solid {INSET_DARK};
                    border-bottom: 2px solid {INSET_LIGHT};
                    border-right: 2px solid {INSET_LIGHT};
                }}
            """
    else:
        # Flat style for non-neumorphic theme
        return f"""
            QPushButton {{
                background-color: {v['bg']};
                color: {v['text']};
                border: none;
                border-radius: {s['radius']}px;
                padding: {s['padding']};
                font-size: {s['font']}px;
                font-weight: 500;
                {size_css}
            }}
            QPushButton:hover {{
                background-color: {v['bg_hover']};
            }}
            QPushButton:disabled {{
                background-color: {disabled_bg};
                color: {colors.text_muted};
            }}
        """


# =============================================================================
# Convenience Functions
# =============================================================================

def icon_button(variant: str = "neutral", size: str = "icon-sm", in_sidebar: bool = False) -> str:
    """Get icon button style (28x28, 32x32, or 44x44)."""
    return get_button_style(variant, size, in_sidebar)


def action_button(variant: str = "primary", size: str = "md") -> str:
    """Get action button style for text buttons."""
    return get_button_style(variant, size)


def get_send_button_style() -> str:
    """Get send button style for current theme."""
    return get_button_style("primary", "md")


def get_cancel_button_style() -> str:
    """Get cancel button style for current theme."""
    return get_button_style("neutral", "md")


def get_attach_button_style() -> str:
    """Get attach button style for current theme."""
    return get_button_style("neutral", "sm")


# =============================================================================
# Legacy Support (deprecated)
# =============================================================================

def button_style(
    bg_color: str | None = None,
    text_color: str | None = None,
    hover_color: str | None = None,
    border_color: str | None = None,
    border_radius: int = 6,
    padding: str = "8px 16px",
) -> str:
    """Generate button stylesheet (DEPRECATED - use get_button_style instead)."""
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


def neu_button_raised_style(
    accent_color: str | None = None,
    text_color: str = "white",
    size: str = "medium",
) -> str:
    """DEPRECATED - use get_button_style('neutral', size) instead."""
    size_map = {"small": "sm", "medium": "md", "large": "lg"}
    return get_button_style("neutral", size_map.get(size, "md"))


def neu_button_accent_style(
    accent_color: str | None = None,
    text_color: str = "white",
    size: str = "medium",
) -> str:
    """DEPRECATED - use get_button_style('primary', size) instead."""
    size_map = {"small": "sm", "medium": "md", "large": "lg", "circle": "md"}
    return get_button_style("primary", size_map.get(size, "md"))


def neu_button_inset_style(size: str = "medium") -> str:
    """DEPRECATED - use primitives.inset_container_style instead."""
    from styles.primitives import inset_container_style
    return inset_container_style()


# DEPRECATED: Module-level constants
SEND_BUTTON_STYLE = get_send_button_style()
CANCEL_BUTTON_STYLE = get_cancel_button_style()
ATTACH_BUTTON_STYLE = get_attach_button_style()
