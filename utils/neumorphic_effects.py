"""Neumorphic shadow effects for Qt widgets.

This module provides utilities to apply true neumorphic shadow effects
using QGraphicsDropShadowEffect, since Qt CSS doesn't support box-shadow.

Usage:
    from utils.neumorphic_effects import apply_neumorphic_shadow, NeuStyle

    # Apply raised (convex) effect
    apply_neumorphic_shadow(my_button, NeuStyle.RAISED)

    # Apply inset (concave) effect
    apply_neumorphic_shadow(my_input, NeuStyle.INSET)
"""

from enum import Enum
from typing import Optional

from PySide6.QtWidgets import QWidget, QGraphicsDropShadowEffect, QGraphicsEffect
from PySide6.QtGui import QColor
from PySide6.QtCore import QObject

from styles import get_theme_manager, ColorScheme


class NeuStyle(Enum):
    """Neumorphic style types."""
    RAISED = "raised"      # Convex, extruding from surface
    INSET = "inset"        # Concave, pressed into surface
    FLAT = "flat"          # No shadow (for non-neumorphic themes)


class NeuShadowEffect(QGraphicsDropShadowEffect):
    """Custom shadow effect that can be identified as neumorphic."""

    def __init__(self, parent: Optional[QObject] = None, style: NeuStyle = NeuStyle.RAISED):
        super().__init__(parent)
        self.neu_style = style


def apply_neumorphic_shadow(
    widget: QWidget,
    style: NeuStyle = NeuStyle.RAISED,
    intensity: float = 1.0,
    blur_radius: int = 15,
    offset: int = 6,
) -> Optional[QGraphicsEffect]:
    """Apply neumorphic shadow effect to a widget.

    For true neumorphism, we need TWO shadows (light and dark), but Qt only
    supports one QGraphicsEffect per widget. As a workaround, we apply the
    more prominent shadow and rely on CSS gradients for the other.

    Args:
        widget: The widget to apply the effect to
        style: RAISED (extruded) or INSET (pressed)
        intensity: Shadow intensity multiplier (0.0 to 1.0)
        blur_radius: Shadow blur amount
        offset: Shadow offset distance

    Returns:
        The applied QGraphicsEffect, or None if not neumorphic theme
    """
    theme = get_theme_manager()
    colors = theme.current

    if not colors.is_neumorphic:
        # For non-neumorphic themes, optionally apply a subtle standard shadow
        widget.setGraphicsEffect(None)
        return None

    effect = NeuShadowEffect(widget, style)

    if style == NeuStyle.RAISED:
        # For raised elements, show the dark shadow (bottom-right)
        shadow_color = QColor(colors.shadow_dark)
        shadow_color.setAlphaF(0.6 * intensity)
        effect.setColor(shadow_color)
        effect.setBlurRadius(blur_radius)
        effect.setXOffset(offset)
        effect.setYOffset(offset)
    elif style == NeuStyle.INSET:
        # For inset elements, show the light shadow (which appears as inner glow)
        shadow_color = QColor(colors.shadow_light)
        shadow_color.setAlphaF(0.4 * intensity)
        effect.setColor(shadow_color)
        effect.setBlurRadius(blur_radius)
        effect.setXOffset(-offset // 2)
        effect.setYOffset(-offset // 2)
    else:
        widget.setGraphicsEffect(None)
        return None

    widget.setGraphicsEffect(effect)
    return effect


def remove_neumorphic_shadow(widget: QWidget):
    """Remove any neumorphic shadow effect from a widget."""
    effect = widget.graphicsEffect()
    if isinstance(effect, NeuShadowEffect):
        widget.setGraphicsEffect(None)


def update_neumorphic_shadows(widget: QWidget):
    """Update existing neumorphic shadow to match current theme.

    Call this when the theme changes to update shadow colors.
    """
    effect = widget.graphicsEffect()
    if isinstance(effect, NeuShadowEffect):
        apply_neumorphic_shadow(widget, effect.neu_style)


class NeumorphicMixin:
    """Mixin class to add neumorphic shadow support to widgets.

    Usage:
        class MyButton(QPushButton, NeumorphicMixin):
            def __init__(self):
                super().__init__()
                self.setup_neumorphic(NeuStyle.RAISED)
    """

    _neu_style: NeuStyle = NeuStyle.FLAT
    _neu_intensity: float = 1.0
    _theme_listener_added: bool = False

    def setup_neumorphic(
        self,
        style: NeuStyle = NeuStyle.RAISED,
        intensity: float = 1.0,
    ):
        """Set up neumorphic effects for this widget."""
        self._neu_style = style
        self._neu_intensity = intensity

        # Apply initial shadow
        self._apply_neu_shadow()

        # Listen for theme changes
        if not self._theme_listener_added:
            get_theme_manager().add_listener(self._on_theme_change)
            self._theme_listener_added = True

    def _apply_neu_shadow(self):
        """Apply neumorphic shadow based on current settings."""
        if hasattr(self, '_neu_style'):
            apply_neumorphic_shadow(self, self._neu_style, self._neu_intensity)

    def _on_theme_change(self, colors: ColorScheme):
        """Handle theme change - update shadow."""
        self._apply_neu_shadow()

    def cleanup_neumorphic(self):
        """Remove neumorphic effects and listeners."""
        if hasattr(self, '_theme_listener_added') and self._theme_listener_added:
            try:
                get_theme_manager().remove_listener(self._on_theme_change)
            except ValueError:
                pass
            self._theme_listener_added = False

        if hasattr(self, 'setGraphicsEffect'):
            self.setGraphicsEffect(None)


def create_neumorphic_card_shadow(
    widget: QWidget,
    blur: int = 20,
    offset: int = 8,
) -> Optional[QGraphicsEffect]:
    """Create a neumorphic shadow for card/panel widgets.

    Larger, softer shadow suitable for containing elements.
    """
    return apply_neumorphic_shadow(
        widget,
        NeuStyle.RAISED,
        intensity=0.8,
        blur_radius=blur,
        offset=offset,
    )


def create_neumorphic_button_shadow(
    widget: QWidget,
    pressed: bool = False,
) -> Optional[QGraphicsEffect]:
    """Create a neumorphic shadow for buttons.

    Args:
        widget: Button widget
        pressed: If True, apply inset (pressed) style
    """
    style = NeuStyle.INSET if pressed else NeuStyle.RAISED
    return apply_neumorphic_shadow(
        widget,
        style,
        intensity=1.0,
        blur_radius=12,
        offset=5,
    )


def create_neumorphic_input_shadow(widget: QWidget) -> Optional[QGraphicsEffect]:
    """Create a neumorphic shadow for input fields (inset style)."""
    return apply_neumorphic_shadow(
        widget,
        NeuStyle.INSET,
        intensity=0.7,
        blur_radius=10,
        offset=4,
    )
