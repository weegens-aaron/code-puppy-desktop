"""Skills management panel for the sidebar."""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QTextEdit, QFrame, QSplitter,
)
from PySide6.QtCore import Qt, Signal

from styles import COLORS, button_style, get_theme_manager


@dataclass
class SkillInfo:
    """Information about a discovered skill."""
    name: str
    path: Path
    description: str = ""
    license: str = ""
    content_preview: str = ""


def get_skills_directory() -> Path:
    """Get the skills directory path."""
    return Path.home() / ".code_puppy" / "skills"


def discover_skills() -> list[SkillInfo]:
    """Discover all skills in the skills directory."""
    skills_dir = get_skills_directory()
    skills = []

    if not skills_dir.exists():
        return skills

    for item in skills_dir.iterdir():
        if item.is_dir():
            skill_md = item / "SKILL.md"
            if skill_md.exists():
                skill_info = parse_skill_file(skill_md)
                if skill_info:
                    skills.append(skill_info)
        elif item.suffix == ".skill" and item.is_file():
            # Single-file skill
            skill_info = parse_skill_file(item)
            if skill_info:
                skills.append(skill_info)

    return sorted(skills, key=lambda s: s.name.lower())


def parse_skill_file(path: Path) -> Optional[SkillInfo]:
    """Parse a SKILL.md file to extract metadata."""
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return None

    # Extract YAML frontmatter
    name = path.parent.name if path.name == "SKILL.md" else path.stem
    description = ""
    license_info = ""

    # Check for YAML frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            content_body = parts[2]

            # Parse simple YAML
            for line in frontmatter.strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip()
                    if key == "name":
                        name = value
                    elif key == "description":
                        description = value
                    elif key == "license":
                        license_info = value
        else:
            content_body = content
    else:
        content_body = content

    # Get content preview (first ~200 chars of actual content)
    preview_lines = []
    for line in content_body.strip().split("\n"):
        line = line.strip()
        if line and not line.startswith("#"):
            preview_lines.append(line)
            if len(" ".join(preview_lines)) > 200:
                break
    content_preview = " ".join(preview_lines)[:200]
    if len(content_preview) == 200:
        content_preview += "..."

    return SkillInfo(
        name=name,
        path=path.parent if path.name == "SKILL.md" else path,
        description=description,
        license=license_info,
        content_preview=content_preview,
    )


class SkillsPanel(QWidget):
    """Panel for viewing available skills."""

    skills_changed = Signal()  # Emits when skills are modified

    def __init__(self, parent=None):
        super().__init__(parent)
        self._skills: list[SkillInfo] = []
        self._setup_ui()
        self._load_skills()

        # Theme listener
        self._theme_manager = get_theme_manager()
        self._theme_manager.add_listener(self._on_theme_changed)

    def _on_theme_changed(self, theme):
        """Update styles when theme changes."""
        self._apply_styles()

    def _apply_styles(self):
        """Apply current theme styles."""
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
                padding: 8px 12px;
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
        folder_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS.bg_tertiary};
                border-radius: 4px;
            }}
        """)
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

        # Discover skills
        try:
            self._skills = discover_skills()
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
        skills_dir = get_skills_directory()
        return f"""
        <div style="font-family: 'Segoe UI', sans-serif; color: {COLORS.text_primary}; padding: 8px;">
            <h3 style="color: {COLORS.accent_warning}; font-size: 14px;">No Skills Found</h3>
            <p style="color: {COLORS.text_secondary}; font-size: 12px;">
                Skills extend agent capabilities with specialized knowledge.
            </p>
            <p style="color: {COLORS.text_muted}; font-size: 11px; margin-top: 12px;">
                Create skills in:<br/>
                <code style="background: {COLORS.bg_tertiary}; padding: 2px 6px; border-radius: 3px;">
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

        skills_dir = get_skills_directory()
        skills_dir.mkdir(parents=True, exist_ok=True)

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
        try:
            if hasattr(self, '_theme_manager'):
                self._theme_manager.remove_listener(self._on_theme_changed)
        except Exception:
            pass
