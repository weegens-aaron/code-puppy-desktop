"""Reusable settings input widgets."""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton,
    QSlider, QDoubleSpinBox, QSpinBox, QColorDialog,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor


class MaskedApiKeyInput(QWidget):
    """Password input with show/hide toggle for API keys."""

    value_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._input = QLineEdit()
        self._input.setEchoMode(QLineEdit.EchoMode.Password)
        self._input.setPlaceholderText("Not set")
        self._input.textChanged.connect(self.value_changed.emit)
        layout.addWidget(self._input)

        self._toggle_btn = QPushButton("\U0001F441")  # Eye emoji
        self._toggle_btn.setFixedSize(28, 28)
        self._toggle_btn.setCheckable(True)
        self._toggle_btn.setToolTip("Show/Hide")
        self._toggle_btn.clicked.connect(self._toggle_visibility)
        layout.addWidget(self._toggle_btn)

    def _toggle_visibility(self):
        if self._toggle_btn.isChecked():
            self._input.setEchoMode(QLineEdit.EchoMode.Normal)
            self._toggle_btn.setText("\U0001F441")  # Eye open
        else:
            self._input.setEchoMode(QLineEdit.EchoMode.Password)
            self._toggle_btn.setText("\U0001F441")  # Eye (same, just toggle mode)

    def value(self) -> str:
        return self._input.text()

    def set_value(self, value: str):
        self._input.setText(value or "")
        if value:
            self._input.setPlaceholderText("••••••••")
        else:
            self._input.setPlaceholderText("Not set")

    def set_style(self, input_style: str, button_style: str):
        self._input.setStyleSheet(input_style)
        self._toggle_btn.setStyleSheet(button_style)


class SliderSpinBox(QWidget):
    """Synchronized slider and spinbox for numeric values."""

    value_changed = Signal(float)

    def __init__(
        self,
        min_val: float = 0.0,
        max_val: float = 1.0,
        step: float = 0.1,
        decimals: int = 1,
        parent=None
    ):
        super().__init__(parent)
        self._min = min_val
        self._max = max_val
        self._step = step
        self._decimals = decimals
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Slider (uses integer steps, we convert)
        self._slider = QSlider(Qt.Orientation.Horizontal)
        steps = int((self._max - self._min) / self._step)
        self._slider.setRange(0, steps)
        self._slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self._slider, stretch=1)

        # Spinbox
        self._spinbox = QDoubleSpinBox()
        self._spinbox.setRange(self._min, self._max)
        self._spinbox.setSingleStep(self._step)
        self._spinbox.setDecimals(self._decimals)
        self._spinbox.setFixedWidth(70)
        self._spinbox.valueChanged.connect(self._on_spinbox_changed)
        layout.addWidget(self._spinbox)

    def _on_slider_changed(self, value: int):
        float_val = self._min + (value * self._step)
        self._spinbox.blockSignals(True)
        self._spinbox.setValue(float_val)
        self._spinbox.blockSignals(False)
        self.value_changed.emit(float_val)

    def _on_spinbox_changed(self, value: float):
        slider_val = int((value - self._min) / self._step)
        self._slider.blockSignals(True)
        self._slider.setValue(slider_val)
        self._slider.blockSignals(False)
        self.value_changed.emit(value)

    def value(self) -> float:
        return self._spinbox.value()

    def set_value(self, value: float):
        self._spinbox.setValue(value)

    def set_style(self, slider_style: str, spinbox_style: str):
        self._slider.setStyleSheet(slider_style)
        self._spinbox.setStyleSheet(spinbox_style)


class IntSliderSpinBox(QWidget):
    """Synchronized slider and integer spinbox."""

    value_changed = Signal(int)

    def __init__(
        self,
        min_val: int = 0,
        max_val: int = 100,
        parent=None
    ):
        super().__init__(parent)
        self._min = min_val
        self._max = max_val
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(self._min, self._max)
        self._slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self._slider, stretch=1)

        self._spinbox = QSpinBox()
        self._spinbox.setRange(self._min, self._max)
        self._spinbox.setFixedWidth(70)
        self._spinbox.valueChanged.connect(self._on_spinbox_changed)
        layout.addWidget(self._spinbox)

    def _on_slider_changed(self, value: int):
        self._spinbox.blockSignals(True)
        self._spinbox.setValue(value)
        self._spinbox.blockSignals(False)
        self.value_changed.emit(value)

    def _on_spinbox_changed(self, value: int):
        self._slider.blockSignals(True)
        self._slider.setValue(value)
        self._slider.blockSignals(False)
        self.value_changed.emit(value)

    def value(self) -> int:
        return self._spinbox.value()

    def set_value(self, value: int):
        self._spinbox.setValue(value)

    def set_style(self, slider_style: str, spinbox_style: str):
        self._slider.setStyleSheet(slider_style)
        self._spinbox.setStyleSheet(spinbox_style)


class ColorPickerButton(QPushButton):
    """Button that shows current color and opens color picker on click."""

    color_changed = Signal(str)

    def __init__(self, initial_color: str = "#ffffff", parent=None):
        super().__init__(parent)
        self._color = initial_color
        self.setFixedSize(60, 28)
        self._update_display()
        self.clicked.connect(self._pick_color)

    def _update_display(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                border: 1px solid #555;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border-color: #888;
            }}
        """)
        self.setToolTip(self._color)

    def _pick_color(self):
        color = QColorDialog.getColor(
            QColor(self._color),
            self,
            "Select Color"
        )
        if color.isValid():
            self._color = color.name()
            self._update_display()
            self.color_changed.emit(self._color)

    def color(self) -> str:
        return self._color

    def set_color(self, color: str):
        self._color = color
        self._update_display()
