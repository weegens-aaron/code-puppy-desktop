"""Interactive question widget for inline ask_user_question responses."""

from typing import Callable, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QLineEdit, QButtonGroup,
    QRadioButton, QCheckBox, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal

from models.data_types import Message, MessageRole
from styles import COLORS, get_theme_manager


class QuestionWidget(QFrame):
    """Interactive widget for displaying agent questions in chat.

    Shows questions with clickable options and collects user responses inline.
    """

    # Emitted when user submits an answer
    answer_submitted = Signal(dict)  # {"cancelled": bool, "answers": [...]}

    def __init__(
        self,
        message: Message,
        on_submit: Callable[[dict], None] | None = None,
        parent=None
    ):
        super().__init__(parent)
        self._message = message
        self._on_submit = on_submit
        self._questions = message.metadata.get("questions", [])
        self._answers: dict[str, dict] = {}  # header -> {"selected": [...], "other": str}
        self._submitted = False

        self.setFrameShape(QFrame.Shape.NoFrame)
        self._setup_ui()

        # Listen for theme changes
        self._theme_manager = get_theme_manager()
        self._theme_manager.add_listener(self._on_theme_changed)

    def _on_theme_changed(self, theme):
        """Update styles when theme changes."""
        self._apply_styles()

    def _setup_ui(self):
        """Set up the question widget UI."""
        self._apply_styles()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Question")
        header_label.setStyleSheet(f"color: {COLORS.accent_primary}; font-size: 12px; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Questions
        for question in self._questions:
            question_widget = self._create_question_section(question)
            layout.addWidget(question_widget)

        # Submit/Cancel buttons
        self._button_container = QWidget()
        button_layout = QHBoxLayout(self._button_container)
        button_layout.setContentsMargins(0, 8, 0, 0)
        button_layout.setSpacing(8)

        button_layout.addStretch()

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setStyleSheet(self._get_button_style(primary=False))
        self._cancel_btn.clicked.connect(self._on_cancel)
        button_layout.addWidget(self._cancel_btn)

        self._submit_btn = QPushButton("Submit")
        self._submit_btn.setStyleSheet(self._get_button_style(primary=True))
        self._submit_btn.clicked.connect(self._on_submit_clicked)
        button_layout.addWidget(self._submit_btn)

        layout.addWidget(self._button_container)

    def _create_question_section(self, question: dict) -> QWidget:
        """Create UI for a single question."""
        header = question.get("header", "Question")
        question_text = question.get("question", "")
        options = question.get("options", [])
        multi_select = question.get("multi_select", question.get("multiSelect", False))

        # Initialize answer storage
        self._answers[header] = {"selected": [], "other": None}

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Question text
        question_label = QLabel(question_text)
        question_label.setWordWrap(True)
        question_label.setStyleSheet(f"color: {COLORS.text_primary}; font-size: 14px;")
        layout.addWidget(question_label)

        # Options as buttons
        options_container = QWidget()
        options_layout = QVBoxLayout(options_container)
        options_layout.setContentsMargins(0, 4, 0, 0)
        options_layout.setSpacing(6)

        if multi_select:
            # Checkboxes for multi-select
            for opt in options:
                opt_widget = self._create_checkbox_option(header, opt)
                options_layout.addWidget(opt_widget)

            # Other option
            other_widget = self._create_other_option(header, is_checkbox=True)
            options_layout.addWidget(other_widget)
        else:
            # Radio buttons for single select
            button_group = QButtonGroup(self)

            for i, opt in enumerate(options):
                opt_widget, radio = self._create_radio_option(header, opt, button_group, i)
                options_layout.addWidget(opt_widget)

            # Other option
            other_widget, other_radio = self._create_other_option(header, is_checkbox=False)
            button_group.addButton(other_radio, len(options))
            options_layout.addWidget(other_widget)

            button_group.buttonClicked.connect(
                lambda btn, h=header: self._on_radio_selected(h, btn.text())
            )

        layout.addWidget(options_container)
        return container

    def _create_radio_option(self, header: str, opt: dict, group: QButtonGroup, idx: int) -> tuple[QWidget, QRadioButton]:
        """Create a radio button option."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        radio = QRadioButton(opt.get("label", ""))
        radio.setStyleSheet(self._get_option_style())
        group.addButton(radio, idx)
        layout.addWidget(radio)

        if opt.get("description"):
            desc = QLabel(opt["description"])
            desc.setWordWrap(True)
            desc.setStyleSheet(f"color: {COLORS.text_muted}; font-size: 11px; margin-left: 24px;")
            layout.addWidget(desc)

        return widget, radio

    def _create_checkbox_option(self, header: str, opt: dict) -> QWidget:
        """Create a checkbox option."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        checkbox = QCheckBox(opt.get("label", ""))
        checkbox.setStyleSheet(self._get_option_style())
        checkbox.stateChanged.connect(
            lambda state, h=header, lbl=opt.get("label", ""): self._on_checkbox_changed(h, lbl, state)
        )
        layout.addWidget(checkbox)

        if opt.get("description"):
            desc = QLabel(opt["description"])
            desc.setWordWrap(True)
            desc.setStyleSheet(f"color: {COLORS.text_muted}; font-size: 11px; margin-left: 24px;")
            layout.addWidget(desc)

        return widget

    def _create_other_option(self, header: str, is_checkbox: bool) -> tuple[QWidget, QRadioButton | QCheckBox] | QWidget:
        """Create the 'Other' option with text input."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        if is_checkbox:
            toggle = QCheckBox("Other:")
        else:
            toggle = QRadioButton("Other:")

        toggle.setStyleSheet(self._get_option_style())
        layout.addWidget(toggle)

        other_input = QLineEdit()
        other_input.setPlaceholderText("Enter custom response...")
        other_input.setEnabled(False)
        other_input.setStyleSheet(self._get_input_style())
        layout.addWidget(other_input, stretch=1)

        toggle.toggled.connect(lambda checked: other_input.setEnabled(checked))
        toggle.toggled.connect(lambda checked, h=header: self._on_other_toggled(h, checked))
        other_input.textChanged.connect(lambda text, h=header: self._on_other_text_changed(h, text))

        # Store references
        self._answers[header]["_other_toggle"] = toggle
        self._answers[header]["_other_input"] = other_input

        if is_checkbox:
            return widget
        return widget, toggle

    def _on_radio_selected(self, header: str, label: str):
        """Handle radio button selection."""
        self._answers[header]["selected"] = [label]
        if label != "Other:":
            self._answers[header]["other"] = None

    def _on_checkbox_changed(self, header: str, label: str, state: int):
        """Handle checkbox state change."""
        selected = self._answers[header]["selected"]
        if state == Qt.CheckState.Checked.value:
            if label not in selected:
                selected.append(label)
        else:
            if label in selected:
                selected.remove(label)

    def _on_other_toggled(self, header: str, checked: bool):
        """Handle 'Other' toggle."""
        if checked:
            if "Other" not in self._answers[header]["selected"]:
                self._answers[header]["selected"].append("Other")
        elif "Other" in self._answers[header]["selected"]:
            self._answers[header]["selected"].remove("Other")

    def _on_other_text_changed(self, header: str, text: str):
        """Handle 'Other' text input change."""
        self._answers[header]["other"] = text if text else None

    def _on_submit_clicked(self):
        """Handle submit button click."""
        if self._submitted:
            return

        self._submitted = True
        result = self._get_results()

        # Replace interactive content with summary
        self._show_answer_summary(result)

        # Emit signal and call callback
        self.answer_submitted.emit(result)
        if self._on_submit:
            self._on_submit(result)

    def _on_cancel(self):
        """Handle cancel button click."""
        if self._submitted:
            return

        self._submitted = True
        result = {"cancelled": True, "answers": []}

        # Replace interactive content with cancelled message
        self._show_cancelled_summary()

        self.answer_submitted.emit(result)
        if self._on_submit:
            self._on_submit(result)

    def _show_answer_summary(self, result: dict):
        """Replace interactive elements with a text summary of answers."""
        # Clear existing layout
        self._clear_layout()

        # Rebuild with summary
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Header
        header_label = QLabel("Question (Answered)")
        header_label.setStyleSheet(f"color: {COLORS.accent_success}; font-size: 12px; font-weight: bold;")
        layout.addWidget(header_label)

        # Show each answer
        for answer in result.get("answers", []):
            header = answer.get("question_header", "")
            selected = answer.get("selected_options", [])
            other_text = answer.get("other_text")

            # Find original question text
            question_text = ""
            for q in self._questions:
                if q.get("header") == header:
                    question_text = q.get("question", "")
                    break

            # Question
            q_label = QLabel(question_text)
            q_label.setWordWrap(True)
            q_label.setStyleSheet(f"color: {COLORS.text_secondary}; font-size: 13px;")
            layout.addWidget(q_label)

            # Answer
            if other_text:
                answer_text = f"Other: {other_text}"
            elif selected:
                answer_text = ", ".join(selected)
            else:
                answer_text = "(no selection)"

            a_label = QLabel(f"  {answer_text}")
            a_label.setWordWrap(True)
            a_label.setStyleSheet(f"color: {COLORS.text_primary}; font-size: 13px; font-weight: bold;")
            layout.addWidget(a_label)

    def _show_cancelled_summary(self):
        """Replace interactive elements with cancelled message."""
        self._clear_layout()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        header_label = QLabel("Question (Cancelled)")
        header_label.setStyleSheet(f"color: {COLORS.text_muted}; font-size: 12px; font-weight: bold;")
        layout.addWidget(header_label)

        # Show original questions
        for question in self._questions:
            q_label = QLabel(question.get("question", ""))
            q_label.setWordWrap(True)
            q_label.setStyleSheet(f"color: {COLORS.text_muted}; font-size: 13px;")
            layout.addWidget(q_label)

    def _clear_layout(self):
        """Clear all widgets from the current layout."""
        if self.layout():
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            # Delete the old layout
            QWidget().setLayout(self.layout())

    def _get_results(self) -> dict:
        """Get the collected answers."""
        answers = []
        for header, data in self._answers.items():
            if header.startswith("_"):
                continue
            selected = data.get("selected", [])
            other = data.get("other")

            answers.append({
                "question_header": header,
                "selected_options": [s for s in selected if s != "Other"],
                "other_text": other if "Other" in selected else None,
            })

        return {
            "cancelled": False,
            "answers": answers,
        }

    def _apply_styles(self):
        """Apply theme styles."""
        colors = get_theme_manager().current
        if colors.is_neumorphic:
            self.setStyleSheet(f"""
                QuestionWidget {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 {colors.shadow_light},
                        stop:0.15 {colors.bg_primary},
                        stop:0.85 {colors.bg_primary},
                        stop:1 {colors.shadow_dark}
                    );
                    border-left: 3px solid {COLORS.accent_primary};
                    border-radius: 12px;
                    margin: 4px 8px;
                }}
                QuestionWidget QWidget {{
                    background: transparent;
                }}
                QuestionWidget QLabel {{
                    background: transparent;
                }}
                QuestionWidget QFrame {{
                    background: transparent;
                    border: none;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QuestionWidget {{
                    background-color: {COLORS.bg_secondary};
                    border-left: 3px solid {COLORS.accent_primary};
                    border-radius: 0px;
                    margin: 2px 8px;
                }}
                QuestionWidget QWidget {{
                    background: transparent;
                }}
                QuestionWidget QLabel {{
                    background: transparent;
                }}
            """)

    def _get_button_style(self, primary: bool = False) -> str:
        """Get button style."""
        colors = get_theme_manager().current
        if colors.is_neumorphic:
            # Beveled button styles
            if primary:
                return f"""
                    QPushButton {{
                        background-color: {COLORS.accent_primary};
                        color: white;
                        border-top: 2px solid #f0a8b8;
                        border-left: 2px solid #f0a8b8;
                        border-bottom: 2px solid {COLORS.accent_primary_hover};
                        border-right: 2px solid {COLORS.accent_primary_hover};
                        border-radius: 10px;
                        padding: 8px 16px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: #e8a0b0;
                    }}
                    QPushButton:pressed {{
                        border-top: 2px solid {COLORS.accent_primary_hover};
                        border-left: 2px solid {COLORS.accent_primary_hover};
                        border-bottom: 2px solid #f0a8b8;
                        border-right: 2px solid #f0a8b8;
                    }}
                    QPushButton:disabled {{
                        background-color: {COLORS.bg_tertiary};
                        border: none;
                        color: {COLORS.text_muted};
                    }}
                """
            return f"""
                QPushButton {{
                    background-color: {colors.bg_primary};
                    color: {COLORS.text_primary};
                    border-top: 2px solid {colors.shadow_light};
                    border-left: 2px solid {colors.shadow_light};
                    border-bottom: 2px solid {colors.shadow_dark};
                    border-right: 2px solid {colors.shadow_dark};
                    border-radius: 10px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {colors.bg_tertiary};
                }}
                QPushButton:pressed {{
                    border-top: 2px solid {colors.shadow_dark};
                    border-left: 2px solid {colors.shadow_dark};
                    border-bottom: 2px solid {colors.shadow_light};
                    border-right: 2px solid {colors.shadow_light};
                }}
                QPushButton:disabled {{
                    background-color: {COLORS.bg_secondary};
                    border: none;
                    color: {COLORS.text_muted};
                }}
            """
        else:
            if primary:
                return f"""
                    QPushButton {{
                        background-color: {COLORS.accent_primary};
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS.accent_primary_hover};
                    }}
                    QPushButton:disabled {{
                        background-color: {COLORS.bg_tertiary};
                        color: {COLORS.text_muted};
                    }}
                """
            return f"""
                QPushButton {{
                    background-color: {COLORS.bg_tertiary};
                    color: {COLORS.text_primary};
                    border: 1px solid {COLORS.border_default};
                    border-radius: 6px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS.bg_secondary};
                    border-color: {COLORS.accent_primary};
                }}
                QPushButton:disabled {{
                    background-color: {COLORS.bg_secondary};
                    color: {COLORS.text_muted};
                }}
            """

    def _get_option_style(self) -> str:
        """Get style for radio/checkbox options."""
        colors = get_theme_manager().current
        if colors.is_neumorphic:
            return f"""
                QRadioButton, QCheckBox {{
                    color: {COLORS.text_primary};
                    padding: 6px 4px;
                    font-size: 13px;
                    spacing: 8px;
                    background: transparent;
                }}
                QRadioButton:hover, QCheckBox:hover {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 {colors.shadow_light},
                        stop:0.5 {colors.bg_primary},
                        stop:1 {colors.shadow_dark}
                    );
                    border-radius: 8px;
                }}
                QRadioButton::indicator, QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                }}
                QRadioButton::indicator:checked {{
                    background-color: {COLORS.accent_primary};
                    border: none;
                    border-radius: 9px;
                }}
                QRadioButton::indicator:unchecked {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 {colors.shadow_dark},
                        stop:0.5 {colors.bg_primary},
                        stop:1 {colors.shadow_light}
                    );
                    border: none;
                    border-radius: 9px;
                }}
                QCheckBox::indicator:checked {{
                    background-color: {COLORS.accent_primary};
                    border: none;
                    border-radius: 5px;
                }}
                QCheckBox::indicator:unchecked {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 {colors.shadow_dark},
                        stop:0.5 {colors.bg_primary},
                        stop:1 {colors.shadow_light}
                    );
                    border: none;
                    border-radius: 5px;
                }}
            """
        return f"""
            QRadioButton, QCheckBox {{
                color: {COLORS.text_primary};
                padding: 6px 4px;
                font-size: 13px;
                spacing: 8px;
            }}
            QRadioButton:hover, QCheckBox:hover {{
                background-color: {COLORS.bg_tertiary};
                border-radius: 4px;
            }}
            QRadioButton::indicator, QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
            QRadioButton::indicator:checked {{
                background-color: {COLORS.accent_primary};
                border: 2px solid {COLORS.accent_primary};
                border-radius: 8px;
            }}
            QRadioButton::indicator:unchecked {{
                background-color: {COLORS.bg_tertiary};
                border: 2px solid {COLORS.border_default};
                border-radius: 8px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS.accent_primary};
                border: 2px solid {COLORS.accent_primary};
                border-radius: 4px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {COLORS.bg_tertiary};
                border: 2px solid {COLORS.border_default};
                border-radius: 4px;
            }}
        """

    def _get_input_style(self) -> str:
        """Get style for text input."""
        colors = get_theme_manager().current
        if colors.is_neumorphic:
            # Simple flat style inside the already-styled container to avoid gradient clash
            return f"""
                QLineEdit {{
                    background: {colors.bg_secondary};
                    color: {COLORS.text_primary};
                    border: 1px solid {colors.shadow_dark};
                    border-radius: 10px;
                    padding: 6px 12px;
                    font-size: 13px;
                }}
                QLineEdit:focus {{
                    background: {colors.bg_tertiary};
                    border-color: {COLORS.accent_primary};
                }}
                QLineEdit:disabled {{
                    background: transparent;
                    border-color: transparent;
                    color: {COLORS.text_muted};
                }}
            """
        return f"""
            QLineEdit {{
                background-color: {COLORS.bg_tertiary};
                color: {COLORS.text_primary};
                border: 1px solid {COLORS.border_default};
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS.accent_primary};
            }}
            QLineEdit:disabled {{
                background-color: {COLORS.bg_secondary};
                color: {COLORS.text_muted};
            }}
        """

    @property
    def message(self) -> Message:
        return self._message

    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, '_theme_manager') and hasattr(self, '_on_theme_changed'):
            try:
                self._theme_manager.remove_listener(self._on_theme_changed)
            except Exception:
                pass
