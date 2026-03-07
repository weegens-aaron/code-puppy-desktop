"""Data types for the desktop application."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import time
import uuid


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    THINKING = "thinking"
    TOOL_CALL = "tool_call"
    TOOL_OUTPUT = "tool_output"  # Formatted tool results (diff, shell, etc.)
    ERROR = "error"  # Error messages
    QUESTION = "question"  # Agent asking user a question (interactive)


class ToolOutputType(Enum):
    """Types of formatted tool output."""
    DIFF = "diff"
    FILE_EDIT = "file_edit"  # File edit result (with diff or content preview)
    SHELL = "shell"
    FILE_LISTING = "file_listing"
    GREP = "grep"
    FILE_HEADER = "file_header"
    SKILL_LIST = "skill_list"  # List of available skills
    SKILL_ACTIVATE = "skill_activate"  # Skill activation result
    JSON = "json"  # Default fallback


class ContentPartType(Enum):
    TEXT = "text"
    THINKING = "thinking"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"


@dataclass
class ContentPart:
    """A part of a message (text, thinking, tool call, etc.)."""
    type: ContentPartType
    content: str
    metadata: dict = field(default_factory=dict)
    is_complete: bool = False


@dataclass
class Message:
    """A chat message."""
    role: MessageRole
    content: str = ""
    parts: list[ContentPart] = field(default_factory=list)
    attachments: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def append_content(self, text: str):
        """Append text to content (for streaming)."""
        self.content += text

    def get_display_text(self) -> str:
        """Get text for display (content or parts combined)."""
        if self.content:
            return self.content
        return "\n\n".join(p.content for p in self.parts if p.type == ContentPartType.TEXT)
