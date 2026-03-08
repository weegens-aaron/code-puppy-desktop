"""Settings dialog for configuring application preferences."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QGroupBox, QComboBox, QLabel, QFrame,
    QTabWidget, QWidget, QLineEdit, QCheckBox, QSpinBox,
    QScrollArea,
)
from PySide6.QtCore import Signal, Qt

from styles import get_theme_manager, ThemeManager, THEMES, ColorScheme
from .settings_widgets import (
    MaskedApiKeyInput, SliderSpinBox, IntSliderSpinBox, ColorPickerButton
)

# Config access - imported lazily to avoid circular imports
def _get_config():
    from code_puppy.config import get_value, set_value, reset_value
    return get_value, set_value, reset_value


def _get_models():
    """Get available models from models.json."""
    try:
        from code_puppy.config import MODELS_FILE
        import json
        with open(MODELS_FILE, 'r') as f:
            models = json.load(f)
        return list(models.keys())
    except Exception:
        return ["claude-4-5-sonnet", "gpt-5", "gemini-2.0-flash"]


def _get_agents():
    """Get available agents."""
    try:
        from code_puppy.agents import get_available_agents
        return get_available_agents()
    except Exception:
        return ["code-puppy"]


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
    """Settings dialog with tabbed configuration panels."""

    settings_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(600, 500)
        self.setModal(True)

        self._theme_manager = get_theme_manager()
        self._pending_changes = {}
        self._inputs = {}  # Track all inputs by key

        self._setup_ui()
        self._load_settings()
        self._apply_style()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Tab widget
        self._tabs = QTabWidget()
        self._tabs.addTab(self._create_general_tab(), "General")
        self._tabs.addTab(self._create_model_tab(), "Model")
        self._tabs.addTab(self._create_api_keys_tab(), "API Keys")
        self._tabs.addTab(self._create_behavior_tab(), "Behavior")
        self._tabs.addTab(self._create_display_tab(), "Display")
        self._tabs.addTab(self._create_advanced_tab(), "Advanced")
        layout.addWidget(self._tabs)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self._cancel_btn)

        self._ok_btn = QPushButton("Apply")
        self._ok_btn.setDefault(True)
        self._ok_btn.clicked.connect(self._on_apply)
        button_layout.addWidget(self._ok_btn)

        layout.addLayout(button_layout)

    def _create_tab_with_reset(self, form_layout: QFormLayout, reset_keys: list) -> QWidget:
        """Wrap a form layout in a widget with a reset button."""
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Scrollable form area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        scroll.setWidget(form_widget)
        main_layout.addWidget(scroll, stretch=1)

        # Reset button at bottom
        reset_layout = QHBoxLayout()
        reset_layout.addStretch()
        reset_btn = QPushButton("Reset Tab to Defaults")
        reset_btn.clicked.connect(lambda: self._reset_tab(reset_keys))
        reset_layout.addWidget(reset_btn)
        main_layout.addLayout(reset_layout)

        return container

    def _create_general_tab(self) -> QWidget:
        form = QFormLayout()
        form.setSpacing(12)

        # Puppy name
        self._inputs["puppy_name"] = QLineEdit()
        self._inputs["puppy_name"].setPlaceholderText("AI assistant name")
        form.addRow("Assistant Name:", self._inputs["puppy_name"])

        # Owner name
        self._inputs["owner_name"] = QLineEdit()
        self._inputs["owner_name"].setPlaceholderText("Your name")
        form.addRow("Your Name:", self._inputs["owner_name"])

        # Default agent
        self._inputs["default_agent"] = QComboBox()
        for agent in _get_agents():
            self._inputs["default_agent"].addItem(agent)
        form.addRow("Default Agent:", self._inputs["default_agent"])

        return self._create_tab_with_reset(
            form, ["puppy_name", "owner_name", "default_agent"]
        )

    def _create_model_tab(self) -> QWidget:
        form = QFormLayout()
        form.setSpacing(12)

        # Model selector
        self._inputs["model"] = QComboBox()
        for model in _get_models():
            self._inputs["model"].addItem(model)
        form.addRow("Model:", self._inputs["model"])

        # Temperature
        self._inputs["temperature"] = SliderSpinBox(
            min_val=0.0, max_val=2.0, step=0.1, decimals=1
        )
        form.addRow("Temperature:", self._inputs["temperature"])

        # OpenAI reasoning effort
        self._inputs["openai_reasoning_effort"] = QComboBox()
        for level in ["minimal", "low", "medium", "high", "xhigh"]:
            self._inputs["openai_reasoning_effort"].addItem(level)
        form.addRow("Reasoning Effort:", self._inputs["openai_reasoning_effort"])

        # OpenAI verbosity
        self._inputs["openai_verbosity"] = QComboBox()
        for level in ["low", "medium", "high"]:
            self._inputs["openai_verbosity"].addItem(level)
        form.addRow("Verbosity:", self._inputs["openai_verbosity"])

        return self._create_tab_with_reset(
            form, ["model", "temperature", "openai_reasoning_effort", "openai_verbosity"]
        )

    def _create_api_keys_tab(self) -> QWidget:
        form = QFormLayout()
        form.setSpacing(12)

        api_keys = [
            ("ANTHROPIC_API_KEY", "Anthropic"),
            ("OPENAI_API_KEY", "OpenAI"),
            ("GEMINI_API_KEY", "Google Gemini"),
            ("OPENROUTER_API_KEY", "OpenRouter"),
            ("CEREBRAS_API_KEY", "Cerebras"),
            ("AZURE_OPENAI_API_KEY", "Azure OpenAI"),
            ("ZAI_API_KEY", "ZAI"),
        ]

        for key, label in api_keys:
            self._inputs[key] = MaskedApiKeyInput()
            form.addRow(f"{label}:", self._inputs[key])

        # Azure endpoint (not masked)
        self._inputs["AZURE_OPENAI_ENDPOINT"] = QLineEdit()
        self._inputs["AZURE_OPENAI_ENDPOINT"].setPlaceholderText("https://...")
        form.addRow("Azure Endpoint:", self._inputs["AZURE_OPENAI_ENDPOINT"])

        return self._create_tab_with_reset(
            form, [k for k, _ in api_keys] + ["AZURE_OPENAI_ENDPOINT"]
        )

    def _create_behavior_tab(self) -> QWidget:
        form = QFormLayout()
        form.setSpacing(12)

        # YOLO mode
        self._inputs["yolo_mode"] = QCheckBox("Skip tool confirmations")
        form.addRow("YOLO Mode:", self._inputs["yolo_mode"])

        # Allow recursion
        self._inputs["allow_recursion"] = QCheckBox("Allow recursive agent execution")
        form.addRow("Allow Recursion:", self._inputs["allow_recursion"])

        # Safety permission level
        self._inputs["safety_permission_level"] = QComboBox()
        for level in ["none", "low", "medium", "high", "critical"]:
            self._inputs["safety_permission_level"].addItem(level)
        form.addRow("Safety Level:", self._inputs["safety_permission_level"])

        # Message limit
        self._inputs["message_limit"] = QSpinBox()
        self._inputs["message_limit"].setRange(1, 10000)
        self._inputs["message_limit"].setValue(1000)
        form.addRow("Message Limit:", self._inputs["message_limit"])

        return self._create_tab_with_reset(
            form, ["yolo_mode", "allow_recursion", "safety_permission_level", "message_limit"]
        )

    def _create_display_tab(self) -> QWidget:
        form = QFormLayout()
        form.setSpacing(12)

        # Theme selector (existing functionality)
        theme_layout = QVBoxLayout()
        theme_row = QHBoxLayout()

        self._inputs["theme"] = QComboBox()
        self._inputs["theme"].setMinimumWidth(180)
        for theme_name in ThemeManager.available_themes():
            self._inputs["theme"].addItem(theme_name)
        current_theme = self._theme_manager.theme_name
        index = self._inputs["theme"].findText(current_theme)
        if index >= 0:
            self._inputs["theme"].setCurrentIndex(index)
        self._inputs["theme"].currentTextChanged.connect(self._on_theme_preview)
        theme_row.addWidget(self._inputs["theme"])
        theme_row.addStretch()
        theme_layout.addLayout(theme_row)

        # Theme preview
        self._theme_preview = ThemePreview()
        self._theme_preview.set_theme(self._theme_manager.current)
        theme_layout.addWidget(self._theme_preview)

        theme_widget = QWidget()
        theme_widget.setLayout(theme_layout)
        form.addRow("Theme:", theme_widget)

        # Diff context lines
        self._inputs["diff_context_lines"] = IntSliderSpinBox(min_val=0, max_val=50)
        form.addRow("Diff Context Lines:", self._inputs["diff_context_lines"])

        # Highlight colors
        self._inputs["highlight_addition_color"] = ColorPickerButton("#0b1f0b")
        form.addRow("Addition Color:", self._inputs["highlight_addition_color"])

        self._inputs["highlight_deletion_color"] = ColorPickerButton("#390e1a")
        form.addRow("Deletion Color:", self._inputs["highlight_deletion_color"])

        # Suppress options
        self._inputs["suppress_thinking_messages"] = QCheckBox("Hide thinking output")
        form.addRow("Suppress Thinking:", self._inputs["suppress_thinking_messages"])

        self._inputs["suppress_informational_messages"] = QCheckBox("Hide info messages")
        form.addRow("Suppress Info:", self._inputs["suppress_informational_messages"])

        return self._create_tab_with_reset(
            form, [
                "theme", "diff_context_lines",
                "highlight_addition_color", "highlight_deletion_color",
                "suppress_thinking_messages", "suppress_informational_messages"
            ]
        )

    def _create_advanced_tab(self) -> QWidget:
        form = QFormLayout()
        form.setSpacing(12)

        # Session settings
        self._inputs["auto_save_session"] = QCheckBox("Auto-save after responses")
        form.addRow("Auto Save:", self._inputs["auto_save_session"])

        self._inputs["max_saved_sessions"] = QSpinBox()
        self._inputs["max_saved_sessions"].setRange(1, 100)
        self._inputs["max_saved_sessions"].setValue(20)
        form.addRow("Max Sessions:", self._inputs["max_saved_sessions"])

        # Streaming
        self._inputs["enable_streaming"] = QCheckBox("Enable SSE streaming")
        form.addRow("Streaming:", self._inputs["enable_streaming"])

        # Universal constructor
        self._inputs["enable_universal_constructor"] = QCheckBox("Dynamic tool creation")
        form.addRow("Universal Constructor:", self._inputs["enable_universal_constructor"])

        # Compaction
        self._inputs["compaction_strategy"] = QComboBox()
        for strategy in ["truncation", "summarization"]:
            self._inputs["compaction_strategy"].addItem(strategy)
        form.addRow("Compaction Strategy:", self._inputs["compaction_strategy"])

        self._inputs["compaction_threshold"] = SliderSpinBox(
            min_val=0.5, max_val=0.95, step=0.05, decimals=2
        )
        form.addRow("Compaction Threshold:", self._inputs["compaction_threshold"])

        self._inputs["protected_token_count"] = QSpinBox()
        self._inputs["protected_token_count"].setRange(1000, 100000)
        self._inputs["protected_token_count"].setValue(50000)
        self._inputs["protected_token_count"].setSingleStep(1000)
        form.addRow("Protected Tokens:", self._inputs["protected_token_count"])

        return self._create_tab_with_reset(
            form, [
                "auto_save_session", "max_saved_sessions",
                "enable_streaming", "enable_universal_constructor",
                "compaction_strategy", "compaction_threshold", "protected_token_count"
            ]
        )

    def _on_theme_preview(self, theme_name: str):
        """Update theme preview when selection changes."""
        if theme_name in THEMES:
            self._theme_preview.set_theme(THEMES[theme_name])

    def _load_settings(self):
        """Load current settings from config into inputs."""
        get_value, _, _ = _get_config()

        # Helper to safely get config values
        def get(key, default=""):
            val = get_value(key)
            return val if val is not None else default

        # General
        self._inputs["puppy_name"].setText(get("puppy_name", ""))
        self._inputs["owner_name"].setText(get("owner_name", ""))
        self._set_combo_value("default_agent", get("default_agent", "code-puppy"))

        # Model
        self._set_combo_value("model", get("model", ""))
        temp = get("temperature", "0.7")
        try:
            self._inputs["temperature"].set_value(float(temp))
        except (ValueError, TypeError):
            self._inputs["temperature"].set_value(0.7)
        self._set_combo_value("openai_reasoning_effort", get("openai_reasoning_effort", "medium"))
        self._set_combo_value("openai_verbosity", get("openai_verbosity", "medium"))

        # API Keys
        for key in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
                    "OPENROUTER_API_KEY", "CEREBRAS_API_KEY", "AZURE_OPENAI_API_KEY", "ZAI_API_KEY"]:
            self._inputs[key].set_value(get(key, ""))
        self._inputs["AZURE_OPENAI_ENDPOINT"].setText(get("AZURE_OPENAI_ENDPOINT", ""))

        # Behavior
        self._inputs["yolo_mode"].setChecked(get("yolo_mode", "").lower() in ("true", "1", "yes"))
        self._inputs["allow_recursion"].setChecked(get("allow_recursion", "true").lower() in ("true", "1", "yes"))
        self._set_combo_value("safety_permission_level", get("safety_permission_level", "medium"))
        try:
            self._inputs["message_limit"].setValue(int(get("message_limit", "1000")))
        except ValueError:
            self._inputs["message_limit"].setValue(1000)

        # Display (theme handled separately in _setup_ui)
        try:
            self._inputs["diff_context_lines"].set_value(int(get("diff_context_lines", "6")))
        except ValueError:
            self._inputs["diff_context_lines"].set_value(6)
        self._inputs["highlight_addition_color"].set_color(get("highlight_addition_color", "#0b1f0b"))
        self._inputs["highlight_deletion_color"].set_color(get("highlight_deletion_color", "#390e1a"))
        self._inputs["suppress_thinking_messages"].setChecked(
            get("suppress_thinking_messages", "").lower() in ("true", "1", "yes")
        )
        self._inputs["suppress_informational_messages"].setChecked(
            get("suppress_informational_messages", "").lower() in ("true", "1", "yes")
        )

        # Advanced
        self._inputs["auto_save_session"].setChecked(
            get("auto_save_session", "true").lower() in ("true", "1", "yes")
        )
        try:
            self._inputs["max_saved_sessions"].setValue(int(get("max_saved_sessions", "20")))
        except ValueError:
            self._inputs["max_saved_sessions"].setValue(20)
        self._inputs["enable_streaming"].setChecked(
            get("enable_streaming", "true").lower() in ("true", "1", "yes")
        )
        self._inputs["enable_universal_constructor"].setChecked(
            get("enable_universal_constructor", "true").lower() in ("true", "1", "yes")
        )
        self._set_combo_value("compaction_strategy", get("compaction_strategy", "truncation"))
        try:
            self._inputs["compaction_threshold"].set_value(float(get("compaction_threshold", "0.85")))
        except ValueError:
            self._inputs["compaction_threshold"].set_value(0.85)
        try:
            self._inputs["protected_token_count"].setValue(int(get("protected_token_count", "50000")))
        except ValueError:
            self._inputs["protected_token_count"].setValue(50000)

    def _set_combo_value(self, key: str, value: str):
        """Set combo box value by text."""
        combo = self._inputs[key]
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _reset_tab(self, keys: list):
        """Reset specified keys to defaults and reload."""
        _, _, reset_value = _get_config()
        for key in keys:
            if key != "theme":  # Theme is handled by ThemeManager
                try:
                    reset_value(key)
                except Exception:
                    pass
        self._load_settings()

    def _collect_settings(self) -> dict:
        """Collect all settings from inputs."""
        settings = {}

        # General
        settings["puppy_name"] = self._inputs["puppy_name"].text()
        settings["owner_name"] = self._inputs["owner_name"].text()
        settings["default_agent"] = self._inputs["default_agent"].currentText()

        # Model
        settings["model"] = self._inputs["model"].currentText()
        settings["temperature"] = str(self._inputs["temperature"].value())
        settings["openai_reasoning_effort"] = self._inputs["openai_reasoning_effort"].currentText()
        settings["openai_verbosity"] = self._inputs["openai_verbosity"].currentText()

        # API Keys
        for key in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
                    "OPENROUTER_API_KEY", "CEREBRAS_API_KEY", "AZURE_OPENAI_API_KEY", "ZAI_API_KEY"]:
            settings[key] = self._inputs[key].value()
        settings["AZURE_OPENAI_ENDPOINT"] = self._inputs["AZURE_OPENAI_ENDPOINT"].text()

        # Behavior
        settings["yolo_mode"] = "true" if self._inputs["yolo_mode"].isChecked() else "false"
        settings["allow_recursion"] = "true" if self._inputs["allow_recursion"].isChecked() else "false"
        settings["safety_permission_level"] = self._inputs["safety_permission_level"].currentText()
        settings["message_limit"] = str(self._inputs["message_limit"].value())

        # Display
        settings["theme"] = self._inputs["theme"].currentText()
        settings["diff_context_lines"] = str(self._inputs["diff_context_lines"].value())
        settings["highlight_addition_color"] = self._inputs["highlight_addition_color"].color()
        settings["highlight_deletion_color"] = self._inputs["highlight_deletion_color"].color()
        settings["suppress_thinking_messages"] = (
            "true" if self._inputs["suppress_thinking_messages"].isChecked() else "false"
        )
        settings["suppress_informational_messages"] = (
            "true" if self._inputs["suppress_informational_messages"].isChecked() else "false"
        )

        # Advanced
        settings["auto_save_session"] = "true" if self._inputs["auto_save_session"].isChecked() else "false"
        settings["max_saved_sessions"] = str(self._inputs["max_saved_sessions"].value())
        settings["enable_streaming"] = "true" if self._inputs["enable_streaming"].isChecked() else "false"
        settings["enable_universal_constructor"] = (
            "true" if self._inputs["enable_universal_constructor"].isChecked() else "false"
        )
        settings["compaction_strategy"] = self._inputs["compaction_strategy"].currentText()
        settings["compaction_threshold"] = str(self._inputs["compaction_threshold"].value())
        settings["protected_token_count"] = str(self._inputs["protected_token_count"].value())

        return settings

    def _on_apply(self):
        """Save settings and close."""
        settings = self._collect_settings()
        _, set_value, _ = _get_config()

        # Save all settings to config
        for key, value in settings.items():
            if key == "theme":
                # Theme handled by ThemeManager
                self._theme_manager.set_theme(value)
            elif value:  # Only save non-empty values
                try:
                    set_value(key, value)
                except Exception:
                    pass

        self.settings_changed.emit(settings)
        self.accept()

    def _apply_style(self):
        """Apply theme styling to dialog."""
        colors = self._theme_manager.current
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors.bg_primary};
                color: {colors.text_primary};
            }}
            QTabWidget::pane {{
                border: 1px solid {colors.border_subtle};
                border-radius: 4px;
                background-color: {colors.bg_primary};
            }}
            QTabBar {{
                background-color: {colors.bg_primary};
            }}
            QTabBar::tab {{
                background-color: {colors.bg_secondary};
                color: {colors.text_secondary};
                padding: 8px 16px;
                border: 1px solid {colors.border_subtle};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {colors.bg_primary};
                color: {colors.text_primary};
                border-bottom: 1px solid {colors.bg_primary};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {colors.bg_tertiary};
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
            QLineEdit, QSpinBox, QDoubleSpinBox {{
                background-color: {colors.bg_tertiary};
                color: {colors.text_primary};
                border: 1px solid {colors.border_default};
                border-radius: 4px;
                padding: 6px 8px;
            }}
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {colors.accent_primary};
            }}
            QComboBox {{
                background-color: {colors.bg_tertiary};
                color: {colors.text_primary};
                border: 1px solid {colors.border_default};
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 120px;
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
            QCheckBox {{
                color: {colors.text_primary};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid {colors.border_default};
                border-radius: 4px;
                background-color: {colors.bg_tertiary};
            }}
            QCheckBox::indicator:checked {{
                background-color: {colors.accent_primary};
                border-color: {colors.accent_primary};
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {colors.border_subtle};
                height: 6px;
                background: {colors.bg_tertiary};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {colors.accent_primary};
                border: none;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }}
            QSlider::sub-page:horizontal {{
                background: {colors.accent_primary};
                border-radius: 3px;
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
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: transparent;
            }}
            ThemePreview {{
                background-color: {colors.bg_secondary};
                border: 1px solid {colors.border_subtle};
                border-radius: 4px;
            }}
        """)

    def get_settings(self) -> dict:
        """Get the current settings."""
        return self._collect_settings()
