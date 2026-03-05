"""Dialog for ask_user_question tool."""

from typing import Any

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QCheckBox, QButtonGroup, QFrame, QScrollArea,
    QWidget, QLineEdit, QGroupBox,
)
from PySide6.QtCore import Qt

from styles import COLORS, get_theme_manager


class QuestionDialog(QDialog):
    """Dialog for displaying ask_user_question questions.

    Shows questions with selectable options and collects user responses.
    """

    def __init__(self, questions: list[dict[str, Any]], parent=None):
        super().__init__(parent)
        self.questions = questions
        self.answers: dict[str, dict] = {}  # header -> {"selected": [...], "other": str}

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Question")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Scroll area for questions
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)

        # Create UI for each question
        for question in self.questions:
            question_widget = self._create_question_widget(question)
            content_layout.addWidget(question_widget)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        submit_btn = QPushButton("Submit")
        submit_btn.setDefault(True)
        submit_btn.clicked.connect(self._on_submit)
        button_layout.addWidget(submit_btn)

        layout.addLayout(button_layout)

    def _create_question_widget(self, question: dict) -> QWidget:
        """Create widget for a single question."""
        header = question.get("header", "Question")
        question_text = question.get("question", "")
        options = question.get("options", [])
        # Handle both snake_case and camelCase field names
        multi_select = question.get("multi_select", question.get("multiSelect", False))

        # Initialize answer storage
        self.answers[header] = {"selected": [], "other": None}

        group = QGroupBox(header)
        layout = QVBoxLayout(group)

        # Question text
        question_label = QLabel(question_text)
        question_label.setWordWrap(True)
        question_label.setStyleSheet(f"color: {COLORS.text_primary}; font-weight: bold;")
        layout.addWidget(question_label)

        # "Other" option with text input (created early for single-select button group)
        other_layout = QHBoxLayout()
        other_radio = QRadioButton("Other:")
        other_input = QLineEdit()
        other_input.setPlaceholderText("Enter custom response...")
        other_input.setEnabled(False)

        other_radio.toggled.connect(lambda checked, inp=other_input: inp.setEnabled(checked))
        other_radio.toggled.connect(
            lambda checked, h=header: self._on_other_toggled(h, checked)
        )
        other_input.textChanged.connect(
            lambda text, h=header: self._on_other_text_changed(h, text)
        )

        # Options
        if multi_select:
            # Checkboxes for multi-select
            for opt in options:
                opt_widget = QWidget()
                opt_layout = QVBoxLayout(opt_widget)
                opt_layout.setContentsMargins(0, 4, 0, 4)
                opt_layout.setSpacing(2)

                checkbox = QCheckBox(opt.get("label", ""))
                checkbox.stateChanged.connect(
                    lambda state, h=header, lbl=opt.get("label", ""): self._on_checkbox_changed(h, lbl, state)
                )
                opt_layout.addWidget(checkbox)

                if opt.get("description"):
                    desc_label = QLabel(opt["description"])
                    desc_label.setWordWrap(True)
                    desc_label.setStyleSheet(f"color: {COLORS.text_muted}; font-size: 11px; margin-left: 24px;")
                    opt_layout.addWidget(desc_label)

                layout.addWidget(opt_widget)

            # For multi-select, replace the radio with a checkbox
            other_radio.deleteLater()
            other_radio = QCheckBox("Other:")
            other_radio.toggled.connect(lambda checked, inp=other_input: inp.setEnabled(checked))
            other_radio.toggled.connect(
                lambda checked, h=header: self._on_other_toggled(h, checked)
            )
        else:
            # Radio buttons for single select
            button_group = QButtonGroup(self)
            for i, opt in enumerate(options):
                opt_widget = QWidget()
                opt_layout = QVBoxLayout(opt_widget)
                opt_layout.setContentsMargins(0, 4, 0, 4)
                opt_layout.setSpacing(2)

                radio = QRadioButton(opt.get("label", ""))
                button_group.addButton(radio, i)
                opt_layout.addWidget(radio)

                if opt.get("description"):
                    desc_label = QLabel(opt["description"])
                    desc_label.setWordWrap(True)
                    desc_label.setStyleSheet(f"color: {COLORS.text_muted}; font-size: 11px; margin-left: 24px;")
                    opt_layout.addWidget(desc_label)

                layout.addWidget(opt_widget)

            # Add "Other" radio to the same button group for mutual exclusivity
            button_group.addButton(other_radio, len(options))

            button_group.buttonClicked.connect(
                lambda btn, h=header: self._on_radio_selected(h, btn.text())
            )

        other_layout.addWidget(other_radio)
        other_layout.addWidget(other_input)
        layout.addLayout(other_layout)

        # Store reference to other widgets
        self.answers[header]["_other_radio"] = other_radio
        self.answers[header]["_other_input"] = other_input

        return group

    def _on_radio_selected(self, header: str, label: str):
        """Handle radio button selection."""
        self.answers[header]["selected"] = [label]
        # Clear "other" if a regular option is selected
        if label != "Other:":
            self.answers[header]["other"] = None

    def _on_checkbox_changed(self, header: str, label: str, state: int):
        """Handle checkbox state change."""
        selected = self.answers[header]["selected"]
        if state == Qt.CheckState.Checked.value:
            if label not in selected:
                selected.append(label)
        else:
            if label in selected:
                selected.remove(label)

    def _on_other_toggled(self, header: str, checked: bool):
        """Handle 'Other' radio button toggle."""
        if checked:
            self.answers[header]["selected"] = ["Other"]
        elif "Other" in self.answers[header]["selected"]:
            self.answers[header]["selected"].remove("Other")

    def _on_other_text_changed(self, header: str, text: str):
        """Handle 'Other' text input change."""
        self.answers[header]["other"] = text if text else None

    def _on_submit(self):
        """Handle submit button click."""
        self.accept()

    def get_results(self) -> dict:
        """Get the dialog results.

        Returns:
            Dict with structure:
            {
                "cancelled": bool,
                "answers": [
                    {
                        "question_header": str,
                        "selected_options": [str, ...],
                        "other_text": str | None
                    },
                    ...
                ]
            }
        """
        answers = []
        for header, data in self.answers.items():
            # Skip internal tracking keys
            selected = data.get("selected", [])
            other = data.get("other")

            answers.append({
                "question_header": header,
                "selected_options": selected,
                "other_text": other if "Other" in selected else None,
            })

        return {
            "cancelled": False,
            "answers": answers,
        }

    def _apply_styles(self):
        """Apply theme styles to the dialog."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS.bg_primary};
                color: {COLORS.text_primary};
            }}
            QGroupBox {{
                background-color: {COLORS.bg_secondary};
                border: 2px solid {COLORS.accent_primary};
                border-radius: 8px;
                padding: 16px;
                padding-top: 24px;
                margin-top: 16px;
                font-weight: bold;
                color: {COLORS.text_primary};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                top: 4px;
                padding: 2px 8px;
                background-color: {COLORS.accent_primary};
                color: {COLORS.text_primary};
                border-radius: 4px;
                font-size: 12px;
            }}
            QLabel {{
                color: {COLORS.text_primary};
                font-size: 14px;
                padding: 8px 0;
            }}
            QRadioButton, QCheckBox {{
                color: {COLORS.text_primary};
                padding: 8px 4px;
                font-size: 13px;
                spacing: 8px;
            }}
            QRadioButton:hover, QCheckBox:hover {{
                background-color: {COLORS.bg_tertiary};
                border-radius: 4px;
            }}
            QRadioButton::indicator, QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QRadioButton::indicator:checked, QCheckBox::indicator:checked {{
                background-color: {COLORS.accent_primary};
                border: 2px solid {COLORS.accent_primary};
                border-radius: 9px;
            }}
            QRadioButton::indicator:unchecked, QCheckBox::indicator:unchecked {{
                background-color: {COLORS.bg_tertiary};
                border: 2px solid {COLORS.border_default};
                border-radius: 9px;
            }}
            QCheckBox::indicator:checked {{
                border-radius: 4px;
            }}
            QCheckBox::indicator:unchecked {{
                border-radius: 4px;
            }}
            QLineEdit {{
                background-color: {COLORS.bg_tertiary};
                color: {COLORS.text_primary};
                border: 2px solid {COLORS.border_default};
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS.accent_primary};
            }}
            QLineEdit:disabled {{
                background-color: {COLORS.bg_secondary};
                color: {COLORS.text_muted};
                border-color: {COLORS.border_subtle};
            }}
            QPushButton {{
                background-color: {COLORS.bg_tertiary};
                color: {COLORS.text_primary};
                border: 2px solid {COLORS.border_default};
                border-radius: 6px;
                padding: 10px 20px;
                min-width: 100px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS.bg_secondary};
                border-color: {COLORS.accent_primary};
            }}
            QPushButton:default {{
                background-color: {COLORS.accent_primary};
                border-color: {COLORS.accent_primary};
                color: white;
            }}
            QPushButton:default:hover {{
                background-color: {COLORS.accent_primary_hover};
            }}
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """)


def show_question_dialog(questions: list[dict[str, Any]], parent=None) -> dict | None:
    """Show the question dialog and return results.

    Args:
        questions: List of question dicts with keys:
            - question: str - The question text
            - header: str - Short label
            - options: list[dict] - Options with label and description
            - multi_select: bool - Allow multiple selections

    Returns:
        Dict with answers if submitted, None if cancelled.
    """
    dialog = QuestionDialog(questions, parent)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_results()
    return {"cancelled": True, "answers": []}
