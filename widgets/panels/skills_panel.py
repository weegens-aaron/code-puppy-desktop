"""Skills management panel for the sidebar."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QTextEdit, QFrame, QSplitter, QCheckBox,
)
from PySide6.QtCore import Qt, Signal

from styles import COLORS, button_style

# Try to import agent_skills - may not be available in all installations
SKILLS_AVAILABLE = False
try:
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
    SKILLS_AVAILABLE = True
except ImportError:
    # Provide stub functions if agent_skills is not available
    def get_disabled_skills(): return set()
    def get_skills_enabled(): return False
    def set_skill_disabled(name, disabled): pass
    def set_skills_enabled(enabled): pass
    def discover_skills(): return []
    def refresh_skill_cache(): pass
    def parse_skill_metadata(path): return None
    def get_skill_resources(path): return []


class SkillsPanel(QWidget):
    """Panel for managing agent skills."""

    skills_changed = Signal()  # Emits when skills are modified

    def __init__(self, parent=None):
        super().__init__(parent)
        self._skills = []
        self._disabled_skills = set()
        self._skills_enabled = True
        self._setup_ui()
        self._load_skills()

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
            QCheckBox {{
                color: {COLORS.text_primary};
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid {COLORS.border_default};
                background-color: {COLORS.bg_secondary};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS.accent_primary};
                border-color: {COLORS.accent_primary};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header with toggle and refresh
        header = QHBoxLayout()

        self._skills_toggle = QCheckBox("Enabled")
        self._skills_toggle.setStyleSheet(f"font-weight: bold; font-size: 12px;")
        self._skills_toggle.stateChanged.connect(self._on_toggle_skills_system)
        header.addWidget(self._skills_toggle)

        header.addStretch()

        refresh_btn = QPushButton("\u21bb")
        refresh_btn.setFixedSize(28, 28)
        refresh_btn.setToolTip("Refresh skills")
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
        refresh_btn.clicked.connect(self._on_refresh)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # Splitter for list and preview (vertical for sidebar)
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Skills list
        list_widget = QFrame()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(2)

        list_label = QLabel("Available Skills")
        list_label.setStyleSheet(f"font-size: 11px; color: {COLORS.text_secondary};")
        list_layout.addWidget(list_label)

        self._skills_list = QListWidget()
        self._skills_list.currentItemChanged.connect(self._on_selection_changed)
        self._skills_list.itemDoubleClicked.connect(self._on_toggle_skill)
        list_layout.addWidget(self._skills_list)

        splitter.addWidget(list_widget)

        # Skill details
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

        # Toggle button
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 4, 0, 0)

        self._toggle_btn = QPushButton("Toggle Skill")
        self._toggle_btn.setStyleSheet(button_style(
            bg_color=COLORS.bg_tertiary,
            text_color=COLORS.text_primary,
        ))
        self._toggle_btn.clicked.connect(self._on_toggle_skill)
        button_layout.addWidget(self._toggle_btn)

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
                item.setText(f"\u2717 {display_name}")
                item.setForeground(Qt.GlobalColor.red)
            else:
                item.setText(f"\u2713 {display_name}")
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
            <h3 style="color: {COLORS.accent_info}; margin: 0 0 8px 0; font-size: 14px;">
                {skill_name}
            </h3>
            <p style="margin: 4px 0;">
                <b>Status:</b>
                <span style="color: {status_color};">{status_text}</span>
            </p>
        """

        if metadata:
            if metadata.description:
                html += f"""
                <p style="margin: 8px 0; color: {COLORS.text_secondary}; font-size: 12px;">
                    {metadata.description}
                </p>
                """

            if metadata.tags:
                tags_html = " ".join(
                    f'<span style="background-color: {COLORS.bg_tertiary}; '
                    f'color: #60a5fa; padding: 1px 6px; border-radius: 8px; '
                    f'font-size: 10px;">{tag}</span>'
                    for tag in metadata.tags[:5]
                )
                html += f"""
                <p style="margin: 4px 0;">
                    {tags_html}
                </p>
                """

        html += """
        <p style="margin-top: 12px; color: #a0a0a0; font-size: 11px;">
            Double-click to toggle.
        </p>
        </div>
        """

        return html

    def _render_no_skills_help(self) -> str:
        """Render help text when no skills are found."""
        if not SKILLS_AVAILABLE:
            return f"""
            <div style="font-family: 'Segoe UI', sans-serif; color: {COLORS.text_primary}; padding: 8px;">
                <h3 style="color: {COLORS.accent_warning}; font-size: 14px;">Skills Unavailable</h3>
                <p style="color: {COLORS.text_secondary}; font-size: 12px;">
                    The agent_skills plugin is not installed.
                </p>
                <p style="color: {COLORS.text_muted}; font-size: 11px; margin-top: 8px;">
                    Skills management requires code_puppy.plugins.agent_skills
                </p>
            </div>
            """
        return f"""
        <div style="font-family: 'Segoe UI', sans-serif; color: {COLORS.text_primary}; padding: 8px;">
            <h3 style="color: {COLORS.accent_warning}; font-size: 14px;">No Skills</h3>
            <p style="color: {COLORS.text_secondary}; font-size: 12px;">
                Skills extend agent capabilities.
            </p>
            <p style="color: {COLORS.text_muted}; font-size: 11px; margin-top: 8px;">
                Create in ~/.code_puppy/skills/
            </p>
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

        # Reload and emit signal
        self._load_skills()
        self.skills_changed.emit()

    def _on_toggle_skills_system(self, state):
        """Toggle the entire skills system."""
        enabled = state == Qt.CheckState.Checked.value
        set_skills_enabled(enabled)
        self._skills_enabled = enabled
        self.skills_changed.emit()

    def _on_refresh(self):
        """Refresh the skills list."""
        refresh_skill_cache()
        self._load_skills()

    def refresh(self):
        """Refresh the skills list."""
        self._on_refresh()
