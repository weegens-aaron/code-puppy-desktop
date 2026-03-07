"""Dialog and panel styles.

This module contains:
- Standard dialog styles
- Section and panel label styles
- Validation error styles
- Icon button styles
"""

from styles.colors import get_theme_manager

_theme_manager = get_theme_manager()


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

