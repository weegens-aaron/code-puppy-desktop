"""Model selection panel for the sidebar."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QTextEdit, QFrame, QSplitter,
)
from PySide6.QtCore import Qt, Signal

from styles import COLORS, button_style
from code_puppy.model_factory import ModelFactory
from code_puppy.command_line.model_picker_completion import (
    get_active_model,
    set_active_model,
    load_model_names,
)


class ModelsPanel(QWidget):
    """Panel for selecting the AI model."""

    model_changed = Signal(str)  # Emits model name when changed

    def __init__(self, parent=None):
        super().__init__(parent)
        self._models_config = {}
        self._current_model = ""
        self._setup_ui()
        self._load_models()

    def _setup_ui(self):
        """Set up the panel UI."""
        self.setStyleSheet(f"""
            QWidget {{
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
                height: 2px;
            }}
            QListWidget {{
                background-color: {COLORS.bg_primary};
                color: {COLORS.text_primary};
                border: none;
                padding: 0;
                outline: none;
            }}
            QListWidget::item {{
                padding: 6px;
                border: none;
                margin: 0;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS.accent_primary};
                color: white;
            }}
            QListWidget::item:hover:!selected {{
                background-color: {COLORS.bg_tertiary};
            }}
            QTextEdit {{
                background-color: {COLORS.bg_primary};
                color: {COLORS.text_primary};
                border: none;
                padding: 8px 0;
            }}
            QLabel {{
                color: {COLORS.text_primary};
                background-color: transparent;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header
        header = QHBoxLayout()
        title = QLabel("Models")
        title.setStyleSheet(f"font-weight: bold; color: {COLORS.text_primary}; padding: 4px;")
        header.addWidget(title)
        header.addStretch()

        refresh_btn = QPushButton("\u21bb")
        refresh_btn.setFixedSize(28, 28)
        refresh_btn.setToolTip("Refresh models")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-radius: 4px;
            }
        """)
        refresh_btn.clicked.connect(self._load_models)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # Splitter for list and details (vertical for sidebar)
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Model list
        list_widget = QFrame()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(2)

        list_label = QLabel("Available")
        list_label.setStyleSheet(f"font-size: 11px; color: {COLORS.text_secondary};")
        list_layout.addWidget(list_label)

        self._model_list = QListWidget()
        self._model_list.currentItemChanged.connect(self._on_selection_changed)
        self._model_list.itemDoubleClicked.connect(self._on_apply)
        list_layout.addWidget(self._model_list)

        splitter.addWidget(list_widget)

        # Model details
        details_widget = QFrame()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(2)

        details_label = QLabel("Details")
        details_label.setStyleSheet(f"font-size: 11px; color: {COLORS.text_secondary};")
        details_layout.addWidget(details_label)

        self._details_text = QTextEdit()
        self._details_text.setReadOnly(True)
        details_layout.addWidget(self._details_text)

        splitter.addWidget(details_widget)
        splitter.setSizes([200, 150])

        layout.addWidget(splitter)

        # Apply button
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 4, 0, 0)

        self._apply_btn = QPushButton("Apply")
        self._apply_btn.setStyleSheet(button_style(
            bg_color=COLORS.accent_success,
            text_color="white",
        ))
        self._apply_btn.clicked.connect(self._on_apply)
        button_layout.addWidget(self._apply_btn)

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

        # Check if this is the current model
        is_current = model_name.lower() == self._current_model.lower()

        # Format display
        if is_current:
            item.setText(f"\u2713 {model_name}")
            item.setForeground(Qt.GlobalColor.green)
        else:
            item.setText(f"  {model_name}")

        # Get model config
        config = self._models_config.get(model_name, {})

        # Store model name and config
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

        # Format context length
        if context_length >= 1_000_000:
            context_str = f"{context_length / 1_000_000:.1f}M"
        elif context_length >= 1_000:
            context_str = f"{context_length / 1_000:.0f}K"
        else:
            context_str = str(context_length)

        # Type icons
        type_icons = {
            "anthropic": "\U0001f7e3",
            "openai": "\U0001f7e2",
            "gemini": "\U0001f535",
            "custom_openai": "\u2699\ufe0f",
            "custom_anthropic": "\u2699\ufe0f",
            "azure_openai": "\u2601\ufe0f",
            "openrouter": "\U0001f310",
            "round_robin": "\U0001f504",
            "cerebras": "\u26a1",
        }
        type_icon = type_icons.get(model_type, "\U0001f916")

        html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; color: {COLORS.text_primary};">
            <h3 style="color: {COLORS.accent_info}; margin: 0 0 8px 0; font-size: 14px;">
                {model_name}
            </h3>
            <p style="margin: 4px 0;">
                <b>Status:</b>
                <span style="color: {status_color};">{status_text}</span>
            </p>
            <p style="margin: 4px 0;">
                <b>Type:</b> {type_icon} {model_type}
            </p>
        """

        if context_length > 0:
            html += f"""
            <p style="margin: 4px 0;">
                <b>Context:</b> {context_str} tokens
            </p>
            """

        html += """
        <p style="margin-top: 12px; color: #a0a0a0; font-size: 11px;">
            Double-click to apply.
        </p>
        </div>
        """

        return html

    def _render_no_models_help(self) -> str:
        """Render help text when no models are found."""
        return f"""
        <div style="font-family: 'Segoe UI', sans-serif; color: {COLORS.text_primary}; padding: 8px;">
            <h3 style="color: {COLORS.accent_warning};">No Models</h3>
            <p style="color: {COLORS.text_secondary}; font-size: 12px;">
                No AI models configured.
            </p>
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
            return

        try:
            set_active_model(model_name)
            self._current_model = model_name
            self._load_models()  # Refresh to show new selection
            self.model_changed.emit(model_name)
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to set model: {e}")

    def refresh(self):
        """Refresh the model list."""
        self._load_models()
