"""Model selection dialog for the desktop application."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QTextEdit, QFrame, QSplitter,
)
from PySide6.QtCore import Qt

from desktop.styles import COLORS, button_style
from code_puppy.model_factory import ModelFactory
from code_puppy.command_line.model_picker_completion import (
    get_active_model,
    set_active_model,
    load_model_names,
)


class ModelDialog(QDialog):
    """Dialog for selecting the AI model."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Model")
        self.setMinimumSize(800, 550)
        self._models_config = {}
        self._current_model = ""
        self._setup_ui()
        self._load_models()

    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS.bg_primary};
                color: {COLORS.text_primary};
            }}
            QFrame {{
                background-color: {COLORS.bg_primary};
                border: none;
            }}
            QSplitter {{
                background-color: {COLORS.bg_primary};
            }}
            QSplitter::handle {{
                background-color: {COLORS.border_subtle};
                width: 2px;
            }}
            QListWidget {{
                background-color: {COLORS.bg_secondary};
                color: {COLORS.text_primary};
                border: 1px solid {COLORS.border_subtle};
                border-radius: 4px;
                padding: 4px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
                margin: 2px 0;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS.accent_primary};
                color: white;
            }}
            QListWidget::item:hover:!selected {{
                background-color: {COLORS.bg_tertiary};
            }}
            QTextEdit {{
                background-color: {COLORS.bg_secondary};
                color: {COLORS.text_primary};
                border: 1px solid {COLORS.border_subtle};
                border-radius: 4px;
                padding: 8px;
            }}
            QLabel {{
                color: {COLORS.text_primary};
                background-color: transparent;
            }}
            QPushButton {{
                padding: 8px 16px;
                border-radius: 4px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Splitter for list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: Model list
        left_widget = QFrame()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        list_label = QLabel("Available Models")
        list_label.setStyleSheet(f"font-weight: bold; color: {COLORS.text_secondary};")
        left_layout.addWidget(list_label)

        self._model_list = QListWidget()
        self._model_list.currentItemChanged.connect(self._on_selection_changed)
        self._model_list.itemDoubleClicked.connect(self._on_apply)
        left_layout.addWidget(self._model_list)

        splitter.addWidget(left_widget)

        # Right side: Model details
        right_widget = QFrame()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        details_label = QLabel("Model Details")
        details_label.setStyleSheet(f"font-weight: bold; color: {COLORS.text_secondary};")
        right_layout.addWidget(details_label)

        self._details_text = QTextEdit()
        self._details_text.setReadOnly(True)
        right_layout.addWidget(self._details_text)

        splitter.addWidget(right_widget)
        splitter.setSizes([350, 450])

        layout.addWidget(splitter)

        # Buttons
        button_layout = QHBoxLayout()

        # Apply button
        self._apply_btn = QPushButton("Apply")
        self._apply_btn.setStyleSheet(button_style(
            bg_color=COLORS.accent_success,
            text_color="white",
        ))
        self._apply_btn.clicked.connect(self._on_apply)
        button_layout.addWidget(self._apply_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(button_style(
            bg_color=COLORS.accent_primary,
            text_color="white",
            hover_color=COLORS.accent_primary_hover,
        ))
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _load_models(self):
        """Load available models into the list."""
        self._model_list.clear()

        # Get current model
        self._current_model = get_active_model() or ""

        # Load model configs
        try:
            self._models_config = ModelFactory.load_config()
        except Exception:
            self._models_config = {}

        # Get model names
        try:
            model_names = load_model_names()
        except Exception:
            model_names = list(self._models_config.keys())

        if not model_names:
            item = QListWidgetItem("No models found")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            item.setForeground(Qt.GlobalColor.gray)
            self._model_list.addItem(item)
            self._details_text.setHtml(self._render_no_models_help())
            return

        # Sort models (current model first, then alphabetically)
        def sort_key(name):
            is_current = name.lower() == self._current_model.lower()
            return (not is_current, name.lower())

        model_names.sort(key=sort_key)

        for model_name in model_names:
            self._add_model_item(model_name)

        # Select first (current model)
        if self._model_list.count() > 0:
            self._model_list.setCurrentRow(0)

    def _add_model_item(self, model_name: str):
        """Add a model item to the list."""
        item = QListWidgetItem()

        # Get model config for type info
        config = self._models_config.get(model_name, {})
        model_type = config.get("type", "unknown")

        # Check if this is the current model
        is_current = model_name.lower() == self._current_model.lower()

        # Format display
        if is_current:
            item.setText(f"✓ {model_name}")
            item.setForeground(Qt.GlobalColor.green)
        else:
            item.setText(f"  {model_name}")

        # Store model name
        item.setData(Qt.ItemDataRole.UserRole, model_name)
        item.setData(Qt.ItemDataRole.UserRole + 1, config)
        self._model_list.addItem(item)

    def _on_selection_changed(self, current, previous):
        """Handle selection change in model list."""
        if not current:
            return

        model_name = current.data(Qt.ItemDataRole.UserRole)
        config = current.data(Qt.ItemDataRole.UserRole + 1)

        if not model_name:
            return

        self._details_text.setHtml(self._render_model_details(model_name, config))

    def _render_model_details(self, model_name: str, config: dict) -> str:
        """Render model details as HTML."""
        is_current = model_name.lower() == self._current_model.lower()
        status_color = COLORS.accent_success if is_current else COLORS.text_muted
        status_text = "Active" if is_current else "Available"

        model_type = config.get("type", "unknown")
        context_length = config.get("context_length", 0)
        actual_name = config.get("name", model_name)

        # Format context length
        if context_length >= 1_000_000:
            context_str = f"{context_length / 1_000_000:.1f}M tokens"
        elif context_length >= 1_000:
            context_str = f"{context_length / 1_000:.0f}K tokens"
        else:
            context_str = f"{context_length} tokens"

        # Type icons
        type_icons = {
            "anthropic": "🟣",
            "openai": "🟢",
            "gemini": "🔵",
            "custom_openai": "⚙️",
            "custom_anthropic": "⚙️",
            "azure_openai": "☁️",
            "openrouter": "🌐",
            "round_robin": "🔄",
            "cerebras": "⚡",
        }
        type_icon = type_icons.get(model_type, "🤖")

        html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; color: {COLORS.text_primary};">
            <h3 style="color: {COLORS.accent_info}; margin-bottom: 8px;">
                {model_name}
            </h3>
            <p>
                <b>Status:</b>
                <span style="color: {status_color}; font-weight: bold;">{status_text}</span>
            </p>
            <p>
                <b>Type:</b> {type_icon} <span style="color: #60a5fa;">{model_type}</span>
            </p>
        """

        if actual_name != model_name:
            html += f"""
            <p>
                <b>API Name:</b> <span style="color: {COLORS.text_secondary};">{actual_name}</span>
            </p>
            """

        if context_length > 0:
            html += f"""
            <p>
                <b>Context Window:</b> <span style="color: #fbbf24;">{context_str}</span>
            </p>
            """

        # Show additional config details
        if config.get("custom_endpoint"):
            endpoint = config["custom_endpoint"].get("url", "")
            if endpoint:
                # Truncate long URLs
                display_url = endpoint[:50] + "..." if len(endpoint) > 50 else endpoint
                html += f"""
                <p>
                    <b>Endpoint:</b><br>
                    <span style="color: {COLORS.text_muted}; font-size: 12px;">{display_url}</span>
                </p>
                """

        # Round-robin info
        if model_type == "round_robin" and config.get("models"):
            models_list = ", ".join(config["models"][:5])
            if len(config["models"]) > 5:
                models_list += f" (+{len(config['models']) - 5} more)"
            html += f"""
            <p>
                <b>Models:</b><br>
                <span style="color: {COLORS.text_secondary};">{models_list}</span>
            </p>
            """

        html += f"""
        <p style="margin-top: 16px; color: #a0a0a0; font-size: 12px;">
            Double-click or press Apply to select this model.
        </p>
        </div>
        """

        return html

    def _render_no_models_help(self) -> str:
        """Render help text when no models are found."""
        return f"""
        <div style="font-family: 'Segoe UI', sans-serif; color: {COLORS.text_primary}; padding: 12px;">
            <h3 style="color: {COLORS.accent_warning};">No Models Found</h3>
            <p style="color: {COLORS.text_secondary};">
                No AI models are configured. This usually means the models
                configuration file is missing or corrupted.
            </p>
            <p style="margin-top: 12px;"><b>Common Model Types:</b></p>
            <ul style="color: {COLORS.text_secondary};">
                <li><b>anthropic</b> - Claude models (requires ANTHROPIC_API_KEY)</li>
                <li><b>openai</b> - GPT models (requires OPENAI_API_KEY)</li>
                <li><b>gemini</b> - Google Gemini (requires GEMINI_API_KEY)</li>
            </ul>
        </div>
        """

    def _on_apply(self, item=None):
        """Apply the selected model."""
        current = self._model_list.currentItem()
        if not current:
            return

        model_name = current.data(Qt.ItemDataRole.UserRole)
        if not model_name:
            return

        # Don't do anything if it's already the current model
        if model_name.lower() == self._current_model.lower():
            self.accept()
            return

        try:
            set_active_model(model_name)
            self._current_model = model_name
            self.accept()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to set model: {e}")

    def get_selected_model(self) -> str:
        """Get the currently selected model name."""
        return self._current_model
