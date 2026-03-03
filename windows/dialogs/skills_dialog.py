"""Skills management dialog for the desktop application."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QTextEdit, QFrame, QSplitter, QCheckBox,
)
from PySide6.QtCore import Qt

from styles import COLORS, button_style
from code_puppy.plugins.agent_skills.config import (
    get_disabled_skills,
    get_skills_enabled,
    set_skill_disabled,
    set_skills_enabled,
)
from code_puppy.plugins.agent_skills.discovery import (
    discover_skills,
    refresh_skill_cache,
)
from code_puppy.plugins.agent_skills.metadata import (
    parse_skill_metadata,
    get_skill_resources,
)


class SkillsDialog(QDialog):
    """Dialog for managing agent skills."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Skills")
        self.setMinimumSize(800, 550)
        self._skills = []
        self._disabled_skills = set()
        self._skills_enabled = True
        self._setup_ui()
        self._load_skills()

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
            QCheckBox {{
                color: {COLORS.text_primary};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {COLORS.border_default};
                background-color: {COLORS.bg_secondary};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS.accent_primary};
                border-color: {COLORS.accent_primary};
            }}
            QPushButton {{
                padding: 8px 16px;
                border-radius: 4px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Global toggle
        toggle_layout = QHBoxLayout()
        self._skills_toggle = QCheckBox("Skills System Enabled")
        self._skills_toggle.setStyleSheet(f"font-weight: bold; color: {COLORS.text_primary};")
        self._skills_toggle.stateChanged.connect(self._on_toggle_skills_system)
        toggle_layout.addWidget(self._skills_toggle)
        toggle_layout.addStretch()

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(button_style(
            bg_color=COLORS.bg_tertiary,
            text_color=COLORS.text_primary,
        ))
        refresh_btn.clicked.connect(self._on_refresh)
        toggle_layout.addWidget(refresh_btn)

        layout.addLayout(toggle_layout)

        # Splitter for list and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: Skills list
        left_widget = QFrame()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        list_label = QLabel("Available Skills")
        list_label.setStyleSheet(f"font-weight: bold; color: {COLORS.text_secondary};")
        left_layout.addWidget(list_label)

        self._skills_list = QListWidget()
        self._skills_list.currentItemChanged.connect(self._on_selection_changed)
        self._skills_list.itemDoubleClicked.connect(self._on_toggle_skill)
        left_layout.addWidget(self._skills_list)

        splitter.addWidget(left_widget)

        # Right side: Skill details
        right_widget = QFrame()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        details_label = QLabel("Skill Details")
        details_label.setStyleSheet(f"font-weight: bold; color: {COLORS.text_secondary};")
        right_layout.addWidget(details_label)

        self._details_text = QTextEdit()
        self._details_text.setReadOnly(True)
        right_layout.addWidget(self._details_text)

        splitter.addWidget(right_widget)
        splitter.setSizes([300, 500])

        layout.addWidget(splitter)

        # Buttons
        button_layout = QHBoxLayout()

        # Toggle button
        self._toggle_btn = QPushButton("Enable/Disable Skill")
        self._toggle_btn.setStyleSheet(button_style(
            bg_color=COLORS.bg_tertiary,
            text_color=COLORS.text_primary,
        ))
        self._toggle_btn.clicked.connect(self._on_toggle_skill)
        button_layout.addWidget(self._toggle_btn)

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

    def _load_skills(self):
        """Load available skills into the list."""
        self._skills_list.clear()

        # Get current state
        self._skills_enabled = get_skills_enabled()
        self._disabled_skills = get_disabled_skills()

        # Update toggle
        self._skills_toggle.setChecked(self._skills_enabled)

        # Discover skills
        try:
            self._skills = discover_skills()
        except Exception:
            self._skills = []

        if not self._skills:
            item = QListWidgetItem("No skills found")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            item.setForeground(Qt.GlobalColor.gray)
            self._skills_list.addItem(item)
            self._details_text.setHtml(self._render_no_skills_help())
            return

        # Sort by name
        self._skills.sort(key=lambda s: s.name.lower())

        for skill in self._skills:
            item = QListWidgetItem()

            # Get metadata for display name
            metadata = self._get_skill_metadata(skill)
            display_name = metadata.name if metadata else skill.name

            # Check if disabled
            skill_name = metadata.name if metadata else skill.name
            is_disabled = skill_name in self._disabled_skills

            # Format display
            if is_disabled:
                item.setText(f"✗ {display_name}")
                item.setForeground(Qt.GlobalColor.red)
            else:
                item.setText(f"✓ {display_name}")
                item.setForeground(Qt.GlobalColor.green)

            # Store data
            item.setData(Qt.ItemDataRole.UserRole, skill)
            item.setData(Qt.ItemDataRole.UserRole + 1, metadata)
            self._skills_list.addItem(item)

        # Select first
        if self._skills_list.count() > 0:
            self._skills_list.setCurrentRow(0)

    def _get_skill_metadata(self, skill):
        """Get metadata for a skill."""
        try:
            return parse_skill_metadata(skill.path)
        except Exception:
            return None

    def _on_selection_changed(self, current, previous):
        """Handle selection change in skills list."""
        if not current:
            return

        skill = current.data(Qt.ItemDataRole.UserRole)
        metadata = current.data(Qt.ItemDataRole.UserRole + 1)

        if not skill:
            return

        self._details_text.setHtml(self._render_skill_details(skill, metadata))

    def _render_skill_details(self, skill, metadata) -> str:
        """Render skill details as HTML."""
        skill_name = metadata.name if metadata else skill.name
        is_disabled = skill_name in self._disabled_skills

        status_color = "#f87171" if is_disabled else "#4ade80"
        status_text = "Disabled" if is_disabled else "Enabled"

        html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; color: {COLORS.text_primary};">
            <h3 style="color: {COLORS.accent_info}; margin-bottom: 8px;">
                {skill_name}
            </h3>
            <p>
                <b>Status:</b>
                <span style="color: {status_color}; font-weight: bold;">{status_text}</span>
            </p>
        """

        if metadata:
            if metadata.description:
                html += f"""
                <p style="margin-top: 12px;">
                    <b>Description:</b><br>
                    <span style="color: {COLORS.text_secondary};">{metadata.description}</span>
                </p>
                """

            if metadata.tags:
                tags_html = " ".join(
                    f'<span style="background-color: {COLORS.bg_tertiary}; '
                    f'color: #60a5fa; padding: 2px 8px; border-radius: 12px; '
                    f'font-size: 12px; margin-right: 4px;">{tag}</span>'
                    for tag in metadata.tags
                )
                html += f"""
                <p style="margin-top: 12px;">
                    <b>Tags:</b><br>
                    {tags_html}
                </p>
                """

            if metadata.version:
                html += f"""
                <p style="margin-top: 8px;">
                    <b>Version:</b> {metadata.version}
                </p>
                """

            if metadata.author:
                html += f"""
                <p>
                    <b>Author:</b> {metadata.author}
                </p>
                """

            # Resources
            try:
                resources = get_skill_resources(metadata.path)
                if resources:
                    resources_html = "<br>".join(
                        f'<span style="color: #fbbf24;">• {r.name}</span>'
                        for r in resources[:10]
                    )
                    if len(resources) > 10:
                        resources_html += f'<br><span style="color: {COLORS.text_muted};">... and {len(resources) - 10} more</span>'
                    html += f"""
                    <p style="margin-top: 12px;">
                        <b>Resources ({len(resources)}):</b><br>
                        {resources_html}
                    </p>
                    """
            except Exception:
                pass

        # Path
        html += f"""
        <p style="margin-top: 12px;">
            <b>Path:</b><br>
            <span style="color: {COLORS.text_muted}; font-size: 12px;">{skill.path}</span>
        </p>
        """

        html += """
        <p style="margin-top: 16px; color: #a0a0a0; font-size: 12px;">
            Double-click or press the button to enable/disable this skill.
        </p>
        </div>
        """

        return html

    def _render_no_skills_help(self) -> str:
        """Render help text when no skills are found."""
        return f"""
        <div style="font-family: 'Segoe UI', sans-serif; color: {COLORS.text_primary}; padding: 12px;">
            <h3 style="color: {COLORS.accent_warning};">No Skills Found</h3>
            <p style="color: {COLORS.text_secondary};">
                Skills are custom instructions and resources that extend the agent's capabilities.
            </p>
            <p style="margin-top: 12px;"><b>Create skills in:</b></p>
            <ul style="color: {COLORS.text_secondary};">
                <li><code>~/.code_puppy/skills/</code></li>
                <li><code>./.code_puppy/skills/</code></li>
                <li><code>./skills/</code></li>
            </ul>
            <p style="margin-top: 12px;">
                Each skill directory should contain a <code>SKILL.md</code> file with:
            </p>
            <pre style="background-color: {COLORS.bg_secondary}; padding: 8px; border-radius: 4px; font-size: 12px;">
---
name: my-skill
description: What this skill does
tags: [tag1, tag2]
---

# Skill Instructions

Your skill instructions here...
            </pre>
        </div>
        """

    def _on_toggle_skill(self, item=None):
        """Toggle the enabled/disabled state of the selected skill."""
        current = self._skills_list.currentItem()
        if not current:
            return

        skill = current.data(Qt.ItemDataRole.UserRole)
        metadata = current.data(Qt.ItemDataRole.UserRole + 1)

        if not skill:
            return

        skill_name = metadata.name if metadata else skill.name
        is_disabled = skill_name in self._disabled_skills

        # Toggle
        set_skill_disabled(skill_name, not is_disabled)
        refresh_skill_cache()

        # Reload
        self._load_skills()

    def _on_toggle_skills_system(self, state):
        """Toggle the entire skills system."""
        enabled = state == Qt.CheckState.Checked.value
        set_skills_enabled(enabled)
        self._skills_enabled = enabled

    def _on_refresh(self):
        """Refresh the skills list."""
        refresh_skill_cache()
        self._load_skills()
