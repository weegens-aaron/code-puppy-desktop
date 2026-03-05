"""Model selection panel for the sidebar."""

from typing import Optional

from PySide6.QtWidgets import QListWidgetItem, QMessageBox
from PySide6.QtCore import Qt, Signal

from styles import COLORS
from widgets.panels.base_panel import BaseSidebarPanel, render_empty_state
from services.model_service import ModelServiceProtocol, ModelService, get_model_service


class ModelsPanel(BaseSidebarPanel):
    """Panel for selecting the AI model.

    Extends BaseSidebarPanel to reuse common UI structure (DRY).
    Uses dependency injection for model service (DIP).
    """

    model_changed = Signal(str)  # Emits model name when changed

    def __init__(
        self,
        model_service: Optional[ModelServiceProtocol] = None,
        parent=None
    ):
        """Initialize the models panel.

        Args:
            model_service: Service for model operations. If None, uses default.
            parent: Parent widget.
        """
        self._model_service = model_service or get_model_service()
        self._current_model = ""

        super().__init__(
            title="Models",
            list_label="Available",
            details_label="Details",
            parent=parent,
        )
        self._load_items()

    def _get_action_buttons(self) -> list[dict]:
        """Define the Apply button."""
        return [
            {
                "label": "Apply",
                "callback": self._on_apply,
                "style": {
                    "bg_color": COLORS.accent_success,
                    "text_color": "white",
                },
                "tooltip": "Apply selected model",
            }
        ]

    def _load_items(self):
        """Load available models into the list."""
        self._item_list.clear()

        # Get current model name
        self._current_model = self._model_service.get_current_model_name() or ""

        models = self._model_service.get_available_models()

        if not models:
            item = QListWidgetItem("No models found")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            item.setForeground(Qt.GlobalColor.gray)
            self._item_list.addItem(item)
            self._details_text.setHtml(render_empty_state(
                "No Models",
                "No AI models configured.",
                "Configure models in your settings."
            ))
            return

        for model in models:
            item = QListWidgetItem()

            # Format display
            if model.is_current:
                item.setText(f"\u2713 {model.name}")
                item.setForeground(Qt.GlobalColor.green)
            else:
                item.setText(f"  {model.name}")

            # Store model data
            item.setData(Qt.ItemDataRole.UserRole, model.name)
            item.setData(Qt.ItemDataRole.UserRole + 1, model)  # Store full ModelInfo
            self._item_list.addItem(item)

        # Select first (current model)
        if self._item_list.count() > 0:
            self._item_list.setCurrentRow(0)

    def _on_selection_changed(self, current, previous):
        """Handle selection change in model list."""
        if not current:
            return

        model = current.data(Qt.ItemDataRole.UserRole + 1)
        if not model:
            return

        self._details_text.setHtml(self._render_model_details(model))

    def _render_model_details(self, model) -> str:
        """Render model details as HTML."""
        status_color = COLORS.accent_success if model.is_current else COLORS.text_muted
        status_text = "Active" if model.is_current else "Available"

        html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; color: {COLORS.text_primary};">
            <h3 style="color: {COLORS.accent_info}; margin: 0 0 8px 0; font-size: 14px;">
                {model.name}
            </h3>
            <p style="margin: 4px 0;">
                <b>Status:</b>
                <span style="color: {status_color};">{status_text}</span>
            </p>
            <p style="margin: 4px 0;">
                <b>Type:</b> {model.type_icon} {model.model_type}
            </p>
        """

        if model.context_length > 0:
            html += f"""
            <p style="margin: 4px 0;">
                <b>Context:</b> {model.context_display} tokens
            </p>
            """

        html += """
        <p style="margin-top: 12px; color: #a0a0a0; font-size: 11px;">
            Double-click to apply.
        </p>
        </div>
        """

        return html

    def _on_item_double_clicked(self, item):
        """Handle double-click to apply model."""
        self._on_apply()

    def _on_apply(self):
        """Apply the selected model."""
        current = self._item_list.currentItem()
        if not current:
            return

        model_name = current.data(Qt.ItemDataRole.UserRole)
        if not model_name:
            return

        # Don't do anything if it's already the current model
        if model_name.lower() == self._current_model.lower():
            return

        if self._model_service.set_current_model(model_name):
            self._current_model = model_name
            self._load_items()  # Refresh to show new selection
            self.model_changed.emit(model_name)
        else:
            QMessageBox.critical(self, "Error", f"Failed to set model: {model_name}")
