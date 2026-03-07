"""Skill discovery and management service.

Separates file I/O and parsing concerns from the UI layer (SoC).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class SkillInfo:
    """Information about a discovered skill."""
    name: str
    path: Path
    description: str = ""
    license: str = ""
    content_preview: str = ""


class SkillService:
    """Service for discovering and managing skills.

    Handles all file I/O related to skills, keeping UI panels
    focused on presentation.
    """

    def __init__(self, skills_dir: Optional[Path] = None):
        """Initialize the skill service.

        Args:
            skills_dir: Custom skills directory (defaults to ~/.code_puppy/skills)
        """
        self._skills_dir = skills_dir or (Path.home() / ".code_puppy" / "skills")

    @property
    def skills_directory(self) -> Path:
        """Get the skills directory path."""
        return self._skills_dir

    def discover_skills(self) -> list[SkillInfo]:
        """Discover all skills in the skills directory.

        Returns:
            List of SkillInfo objects, sorted by name
        """
        skills = []

        if not self._skills_dir.exists():
            return skills

        for item in self._skills_dir.iterdir():
            if item.is_dir():
                skill_md = item / "SKILL.md"
                if skill_md.exists():
                    skill_info = self._parse_skill_file(skill_md)
                    if skill_info:
                        skills.append(skill_info)
            elif item.suffix == ".skill" and item.is_file():
                # Single-file skill
                skill_info = self._parse_skill_file(item)
                if skill_info:
                    skills.append(skill_info)

        return sorted(skills, key=lambda s: s.name.lower())

    def _parse_skill_file(self, path: Path) -> Optional[SkillInfo]:
        """Parse a SKILL.md file to extract metadata.

        Args:
            path: Path to the skill file

        Returns:
            SkillInfo if parsing succeeded, None otherwise
        """
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

    def ensure_directory_exists(self) -> Path:
        """Ensure the skills directory exists.

        Returns:
            Path to the skills directory
        """
        self._skills_dir.mkdir(parents=True, exist_ok=True)
        return self._skills_dir


# Global instance
_skill_service: Optional[SkillService] = None


def get_skill_service() -> SkillService:
    """Get or create the global skill service instance."""
    global _skill_service
    if _skill_service is None:
        _skill_service = SkillService()
    return _skill_service
