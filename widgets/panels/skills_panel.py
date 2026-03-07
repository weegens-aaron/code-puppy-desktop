"""Skills management panel for the sidebar."""

import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QTextEdit, QFrame, QSplitter,
)
from PySide6.QtCore import Qt, Signal

from styles import COLORS, get_theme_manager, SIDEBAR_HOVER, icon_button
from services.skill_service import get_skill_service, SkillInfo
from widgets.theme_aware import ThemeAwareMixin
from widgets.panels.base_panel import get_panel_stylesheet


class SkillsPanel(QWidget, ThemeAwareMixin):
    """Panel for viewing available skills."""

    skills_changed = Signal()  # Emits when skills are modified

    def __init__(self, parent=None):
        super().__init__(parent)
        self._skills: list[SkillInfo] = []
        self._skill_service = get_skill_service()
        self._setup_ui()
        self._load_skills()

        # Theme listener (via mixin)
        self.setup_theme_listener()

    def _apply_styles(self):
        """Apply current theme styles using shared panel stylesheet."""
        self.setStyleSheet(get_panel_stylesheet())

    def _setup_ui(self):
        """Set up the panel UI."""
        self._apply_styles()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()

        title = QLabel("Skills")
        title.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {COLORS.text_primary};")
        header.addWidget(title)

        header.addStretch()

        # Open folder button
        folder_btn = QPushButton("📂")
        folder_btn.setFixedSize(28, 28)
        folder_btn.setToolTip("Open skills folder")
        folder_btn.setStyleSheet(icon_button("ghost", "icon-sm", in_sidebar=True))
        folder_btn.clicked.connect(self._on_open_folder)
        header.addWidget(folder_btn)

        layout.addLayout(header)

        # Splitter for list and preview
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Skills list
        list_widget = QFrame()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(4)

        list_label = QLabel("Available Skills")
        list_label.setStyleSheet(f"font-size: 11px; color: {COLORS.text_secondary};")
        list_layout.addWidget(list_label)

        self._skills_list = QListWidget()
        self._skills_list.currentItemChanged.connect(self._on_selection_changed)
        list_layout.addWidget(self._skills_list)

        splitter.addWidget(list_widget)

        # Skill details
        details_widget = QFrame()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(4)

        details_label = QLabel("Details")
        details_label.setStyleSheet(f"font-size: 11px; color: {COLORS.text_secondary};")
        details_layout.addWidget(details_label)

        self._details_text = QTextEdit()
        self._details_text.setReadOnly(True)
        details_layout.addWidget(self._details_text)

        splitter.addWidget(details_widget)
        splitter.setSizes([200, 150])

        layout.addWidget(splitter)

    def _load_skills(self):
        """Load available skills into the list."""
        self._skills_list.clear()

        # Discover skills via service
        try:
            self._skills = self._skill_service.discover_skills()
        except Exception as e:
            self._skills = []
            self._details_text.setHtml(f"""
                <div style="color: {COLORS.accent_error};">
                    Error loading skills: {str(e)}
                </div>
            """)
            return

        if not self._skills:
            item = QListWidgetItem("No skills found")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self._skills_list.addItem(item)
            self._details_text.setHtml(self._render_no_skills_help())
            return

        for skill in self._skills:
            item = QListWidgetItem()
            item.setText(f"⚡ {skill.name}")
            item.setData(Qt.ItemDataRole.UserRole, skill)
            self._skills_list.addItem(item)

        # Select first
        if self._skills_list.count() > 0:
            self._skills_list.setCurrentRow(0)

    def _on_selection_changed(self, current, previous):
        """Handle selection change in skills list."""
        if not current:
            return

        skill = current.data(Qt.ItemDataRole.UserRole)
        if not skill:
            return

        self._details_text.setHtml(self._render_skill_details(skill))

    def _render_skill_details(self, skill: SkillInfo) -> str:
        """Render skill details as HTML."""
        html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; color: {COLORS.text_primary};">
            <h3 style="color: {COLORS.accent_info}; margin: 0 0 8px 0; font-size: 14px;">
                ⚡ {skill.name}
            </h3>
        """

        if skill.description:
            html += f"""
            <p style="margin: 8px 0; color: {COLORS.text_secondary}; font-size: 12px;">
                {skill.description}
            </p>
            """

        if skill.content_preview:
            html += f"""
            <p style="margin: 12px 0 4px 0; color: {COLORS.text_muted}; font-size: 11px; font-weight: bold;">
                Preview:
            </p>
            <p style="margin: 0; color: {COLORS.text_secondary}; font-size: 11px; font-style: italic;">
                {skill.content_preview}
            </p>
            """

        html += f"""
        <p style="margin-top: 16px; color: {COLORS.text_muted}; font-size: 10px;">
            📁 {skill.path}
        </p>
        </div>
        """

        return html

    def _render_no_skills_help(self) -> str:
        """Render help text when no skills are found."""
        skills_dir = self._skill_service.skills_directory
        # Use sidebar-appropriate background for code blocks
        code_bg = SIDEBAR_HOVER if get_theme_manager().is_neumorphic else COLORS.bg_tertiary
        return f"""
        <div style="font-family: 'Segoe UI', sans-serif; color: {COLORS.text_primary}; padding: 8px;">
            <h3 style="color: {COLORS.accent_warning}; font-size: 14px;">No Skills Found</h3>
            <p style="color: {COLORS.text_secondary}; font-size: 12px;">
                Skills extend agent capabilities with specialized knowledge.
            </p>
            <p style="color: {COLORS.text_muted}; font-size: 11px; margin-top: 12px;">
                Create skills in:<br/>
                <code style="background: {code_bg}; padding: 2px 6px; border-radius: 3px;">
                    {skills_dir}
                </code>
            </p>
            <p style="color: {COLORS.text_muted}; font-size: 11px; margin-top: 8px;">
                Each skill needs a SKILL.md file with YAML frontmatter.
            </p>
        </div>
        """

    def _on_open_folder(self):
        """Open the skills folder in file explorer."""
        import subprocess
        import sys

        skills_dir = self._skill_service.ensure_directory_exists()

        if sys.platform == "win32":
            os.startfile(str(skills_dir))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(skills_dir)])
        else:
            subprocess.run(["xdg-open", str(skills_dir)])

    def _on_refresh(self):
        """Refresh the skills list."""
        self._load_skills()
        self.skills_changed.emit()

    def refresh(self):
        """Refresh the skills list."""
        self._on_refresh()

    def __del__(self):
        """Clean up theme listener."""
        self.cleanup_theme_listener()
