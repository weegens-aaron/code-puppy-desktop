"""Utilities for the desktop application."""

from utils.system_open import open_with_default_app
from utils.neumorphic_effects import (
    NeuStyle,
    apply_neumorphic_shadow,
    remove_neumorphic_shadow,
    NeumorphicMixin,
)

__all__ = [
    "open_with_default_app",
    "NeuStyle",
    "apply_neumorphic_shadow",
    "remove_neumorphic_shadow",
    "NeumorphicMixin",
]
