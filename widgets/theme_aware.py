"""Theme-aware widget mixin for consistent theme handling.

Provides a reusable pattern for widgets that need to respond
to theme changes, eliminating duplicate theme listener code.
"""

from styles import get_theme_manager


class ThemeAwareMixin:
    """Mixin that provides theme change handling for widgets.

    Usage:
        class MyWidget(QWidget, ThemeAwareMixin):
            def __init__(self):
                super().__init__()
                self.setup_theme_listener()
                self._apply_styles()

            def _apply_styles(self):
                # Apply theme-specific styles
                self.setStyleSheet(get_my_widget_style())

            def cleanup(self):
                self.cleanup_theme_listener()

    The mixin provides:
    - setup_theme_listener(): Register for theme changes
    - cleanup_theme_listener(): Unregister from theme changes
    - _on_theme_changed(): Default handler that calls _apply_styles()

    Widgets must implement:
    - _apply_styles(): Apply current theme styles to the widget
    """

    _theme_manager = None

    def setup_theme_listener(self):
        """Register this widget to receive theme change notifications."""
        self._theme_manager = get_theme_manager()
        self._theme_manager.add_listener(self._on_theme_changed)

    def cleanup_theme_listener(self):
        """Unregister from theme change notifications.

        Call this in cleanup() or when the widget is being destroyed.
        """
        if self._theme_manager is not None:
            try:
                self._theme_manager.remove_listener(self._on_theme_changed)
            except Exception:
                pass

    def _on_theme_changed(self, theme):
        """Handle theme change by reapplying styles.

        Override this method if you need additional logic beyond
        just reapplying styles.
        """
        self._apply_styles()

    def _apply_styles(self):
        """Apply current theme styles to this widget.

        Subclasses MUST implement this method to set their styles.
        """
        raise NotImplementedError("Subclasses must implement _apply_styles()")
