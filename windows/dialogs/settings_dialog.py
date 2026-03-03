"""Settings dialog for configuring application preferences."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QGroupBox, QComboBox, QLabel, QFrame,
)
from PySide6.QtCore import Signal

from styles import (
    get_theme_manager, ThemeManager, THEMES, ColorScheme
)


class ThemePreview(QFrame):
    """Small preview of a theme's colors."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Color swatches
        self._swatches = []
        for _ in range(6):
            swatch = QFrame()
            swatch.setFixedSize(24, 24)
            swatch.setStyleSheet("border-radius: 4px;")
            layout.addWidget(swatch)
            self._swatches.append(swatch)

        layout.addStretch()

    def set_theme(self, theme: ColorScheme):
        """Update preview with theme colors."""
        colors = [
            theme.bg_primary,
            theme.bg_secondary,
            theme.accent_primary,
            theme.accent_success,
            theme.accent_warning,
            theme.accent_error,
        ]
        for swatch, color in zip(self._swatches, colors):
            swatch.setStyleSheet(f"background-color: {color}; border-radius: 4px;")


class SettingsDialog(QDialog):
    """Settings dialog for application configuration.

    Provides theme selection with preview.
    """

    settings_changed = Signal(dict)  # Emits settings dict when applied

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(450, 280)
        self.setModal(True)

        self._theme_manager = get_theme_manager()
        self._pending_changes = {}
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        # Theme group
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout(theme_group)

        # Theme selector row
        selector_layout = QHBoxLayout()
        selector_layout.setSpacing(12)

        theme_label = QLabel("Select Theme:")
        selector_layout.addWidget(theme_label)

        self._theme_combo = QComboBox()
        self._theme_combo.setMinimumWidth(180)
        for theme_name in ThemeManager.available_themes():
            self._theme_combo.addItem(theme_name)

        # Set current theme
        current_theme = self._theme_manager.theme_name
        index = self._theme_combo.findText(current_theme)
        if index >= 0:
            self._theme_combo.setCurrentIndex(index)

        self._theme_combo.currentTextChanged.connect(self._on_theme_changed)
        selector_layout.addWidget(self._theme_combo)
        selector_layout.addStretch()

        theme_layout.addLayout(selector_layout)

        # Theme preview
        preview_label = QLabel("Preview:")
        preview_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        theme_layout.addWidget(preview_label)

        self._theme_preview = ThemePreview()
        self._theme_preview.set_theme(self._theme_manager.current)
        theme_layout.addWidget(self._theme_preview)

        layout.addWidget(theme_group)
        layout.addStretch()

        # Button row
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self._cancel_btn)

        self._ok_btn = QPushButton("Apply")
        self._ok_btn.setDefault(True)
        self._ok_btn.clicked.connect(self._on_ok)
        button_layout.addWidget(self._ok_btn)

        layout.addLayout(button_layout)

    def _apply_style(self):
        """Apply dark theme styling to dialog."""
        colors = self._theme_manager.current
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors.bg_primary};
                color: {colors.text_primary};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {colors.border_subtle};
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 12px;
                color: {colors.text_primary};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }}
            QComboBox {{
                background-color: {colors.bg_tertiary};
                color: {colors.text_primary};
                border: 1px solid {colors.border_default};
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 150px;
            }}
            QComboBox:focus {{
                border-color: {colors.accent_primary};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {colors.bg_secondary};
                color: {colors.text_primary};
                selection-background-color: {colors.accent_primary};
                border: 1px solid {colors.border_default};
            }}
            QLabel {{
                color: {colors.text_primary};
            }}
            QPushButton {{
                background-color: {colors.bg_tertiary};
                color: {colors.text_primary};
                border: 1px solid {colors.border_default};
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {colors.bg_secondary};
            }}
            QPushButton:default {{
                background-color: {colors.accent_primary};
                border-color: {colors.accent_primary};
            }}
            QPushButton:default:hover {{
                background-color: {colors.accent_primary_hover};
            }}
            ThemePreview {{
                background-color: {colors.bg_secondary};
                border: 1px solid {colors.border_subtle};
                border-radius: 4px;
            }}
        """)

    def _on_theme_changed(self, theme_name: str):
        """Handle theme selection change."""
        if theme_name in THEMES:
            self._theme_preview.set_theme(THEMES[theme_name])
            self._pending_changes["theme"] = theme_name

    def _on_ok(self):
        """Apply settings and close."""
        self._collect_settings()
        if "theme" in self._pending_changes:
            self._theme_manager.set_theme(self._pending_changes["theme"])
        self.settings_changed.emit(self._pending_changes)
        self.accept()

    def _collect_settings(self):
        """Collect all settings into pending changes dict."""
        self._pending_changes["theme"] = self._theme_combo.currentText()

    def get_settings(self) -> dict:
        """Get the current settings."""
        self._collect_settings()
        return self._pending_changes.copy()
