"""Base class for sidebar panels with common UI structure and styling."""

from abc import ABCMeta, abstractmethod
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QTextEdit, QFrame, QSplitter,
)
from PySide6.QtCore import Qt

from styles import COLORS, button_style


# Combined metaclass to resolve conflict between Qt's metaclass and ABCMeta
class QWidgetABCMeta(type(QWidget), ABCMeta):
    """Metaclass combining Qt's metaclass with ABCMeta for abstract widgets."""
    pass


def get_panel_stylesheet(include_checkbox: bool = False) -> str:
    """Generate common stylesheet for sidebar panels.

    Args:
        include_checkbox: Whether to include checkbox-specific styles

    Returns:
        CSS stylesheet string
    """
    base_style = f"""
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
            background-color: {COLORS.bg_secondary};
            color: {COLORS.text_primary};
            border: 1px solid {COLORS.border_subtle};
            border-radius: 4px;
            padding: 4px;
            outline: none;
        }}
        QListWidget::item {{
            padding: 6px;
            border-radius: 4px;
            margin: 1px 0;
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
    """

    if include_checkbox:
        base_style += f"""
        QListWidget::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {COLORS.border_default};
            border-radius: 3px;
            background-color: {COLORS.bg_secondary};
        }}
        QListWidget::indicator:checked {{
            background-color: {COLORS.accent_primary};
            border-color: {COLORS.accent_primary};
        }}
        """

    return base_style


def get_refresh_button_stylesheet() -> str:
    """Get stylesheet for refresh button."""
    return """
        QPushButton {
            background-color: transparent;
            border: none;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #3d3d3d;
            border-radius: 4px;
        }
    """


class BaseSidebarPanel(QWidget, metaclass=QWidgetABCMeta):
    """Abstract base class for sidebar panels.

    Provides common UI structure:
    - Header with title and refresh button
    - Vertical splitter with list on top, details on bottom
    - Action buttons at bottom

    Subclasses must implement:
    - _load_items(): Load items into the list
    - _on_selection_changed(): Handle list selection changes
    - _get_action_buttons(): Return list of (label, callback, style_kwargs) tuples
    """

    def __init__(
        self,
        title: str,
        list_label: str = "Available",
        details_label: str = "Details",
        include_checkbox: bool = False,
        parent: Optional[QWidget] = None,
    ):
        """Initialize the panel.

        Args:
            title: Panel header title
            list_label: Label above the list widget
            details_label: Label above the details text
            include_checkbox: Whether list items have checkboxes
            parent: Parent widget
        """
        super().__init__(parent)
        self._title = title
        self._list_label = list_label
        self._details_label = details_label
        self._include_checkbox = include_checkbox

        self._setup_ui()

    def _setup_ui(self):
        """Set up the common panel UI structure."""
        self.setStyleSheet(get_panel_stylesheet(self._include_checkbox))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header
        header = QHBoxLayout()
        title_label = QLabel(self._title)
        title_label.setStyleSheet(f"font-weight: bold; color: {COLORS.text_primary}; padding: 4px;")
        header.addWidget(title_label)
        header.addStretch()

        refresh_btn = QPushButton("\u21bb")
        refresh_btn.setFixedSize(28, 28)
        refresh_btn.setToolTip(f"Refresh {self._title.lower()}")
        refresh_btn.setStyleSheet(get_refresh_button_stylesheet())
        refresh_btn.clicked.connect(self.refresh)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # Splitter for list and details
        splitter = QSplitter(Qt.Orientation.Vertical)

        # List section
        list_widget = QFrame()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(2)

        list_section_label = QLabel(self._list_label)
        list_section_label.setStyleSheet(f"font-size: 11px; color: {COLORS.text_secondary};")
        list_layout.addWidget(list_section_label)

        self._item_list = QListWidget()
        self._item_list.currentItemChanged.connect(self._on_selection_changed)
        self._item_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        list_layout.addWidget(self._item_list)

        splitter.addWidget(list_widget)

        # Details section
        details_widget = QFrame()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(2)

        details_section_label = QLabel(self._details_label)
        details_section_label.setStyleSheet(f"font-size: 11px; color: {COLORS.text_secondary};")
        details_layout.addWidget(details_section_label)

        self._details_text = QTextEdit()
        self._details_text.setReadOnly(True)
        details_layout.addWidget(self._details_text)

        splitter.addWidget(details_widget)
        splitter.setSizes([200, 150])

        layout.addWidget(splitter)

        # Action buttons
        self._setup_action_buttons(layout)

    def _setup_action_buttons(self, layout: QVBoxLayout):
        """Set up action buttons at the bottom of the panel."""
        buttons = self._get_action_buttons()
        if not buttons:
            return

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 4, 0, 0)

        self._action_buttons = {}
        for btn_config in buttons:
            label = btn_config["label"]
            callback = btn_config["callback"]
            style_kwargs = btn_config.get("style", {})
            tooltip = btn_config.get("tooltip", "")

            btn = QPushButton(label)
            btn.setStyleSheet(button_style(**style_kwargs))
            if tooltip:
                btn.setToolTip(tooltip)
            btn.clicked.connect(callback)
            button_layout.addWidget(btn)
            self._action_buttons[label] = btn

        layout.addLayout(button_layout)

    def get_action_button(self, label: str) -> Optional[QPushButton]:
        """Get an action button by its label."""
        return self._action_buttons.get(label)

    @abstractmethod
    def _load_items(self):
        """Load items into the list widget. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def _on_selection_changed(self, current: QListWidgetItem, previous: QListWidgetItem):
        """Handle selection change in the list. Must be implemented by subclasses."""
        pass

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Handle item double-click. Override in subclasses if needed."""
        pass

    def _get_action_buttons(self) -> list[dict]:
        """Return action button configurations.

        Override in subclasses to add action buttons.

        Returns:
            List of button configs: [{"label": str, "callback": Callable,
                                      "style": dict, "tooltip": str}, ...]
        """
        return []

    def refresh(self):
        """Refresh the panel contents."""
        self._load_items()

    @property
    def item_list(self) -> QListWidget:
        """Access the list widget."""
        return self._item_list

    @property
    def details_text(self) -> QTextEdit:
        """Access the details text widget."""
        return self._details_text


def render_empty_state(title: str, message: str, hint: str = "") -> str:
    """Render HTML for empty state display.

    Args:
        title: Header title
        message: Main message
        hint: Optional hint text

    Returns:
        HTML string
    """
    html = f"""
    <div style="font-family: sans-serif; color: {COLORS.text_primary}; padding: 4px;">
        <h3 style="color: {COLORS.accent_warning}; margin: 0 0 8px 0;">{title}</h3>
        <p style="color: {COLORS.text_secondary}; font-size: 12px; margin: 0;">
            {message}
        </p>
    """
    if hint:
        html += f"""
        <p style="color: {COLORS.text_muted}; font-size: 11px; margin-top: 8px;">
            {hint}
        </p>
        """
    html += "</div>"
    return html
