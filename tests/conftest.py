"""Pytest configuration and shared fixtures."""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# =============================================================================
# Mock Qt and code_puppy modules before any test imports
# =============================================================================

# Mock PySide6 modules
sys.modules["PySide6"] = MagicMock()
sys.modules["PySide6.QtWidgets"] = MagicMock()
sys.modules["PySide6.QtCore"] = MagicMock()
sys.modules["PySide6.QtGui"] = MagicMock()

# Mock code_puppy modules
sys.modules["code_puppy"] = MagicMock()
sys.modules["code_puppy.config"] = MagicMock()
sys.modules["code_puppy.config"].MCP_SERVERS_FILE = "/tmp/mcp_servers.json"
sys.modules["code_puppy.config"].AUTOSAVE_DIR = "/tmp/autosave"
sys.modules["code_puppy.agents"] = MagicMock()
sys.modules["code_puppy.callbacks"] = MagicMock()
sys.modules["code_puppy.session_storage"] = MagicMock()

# Mock styles module with realistic color values
mock_colors = MagicMock()
mock_colors.bg_primary = "#1e1e1e"
mock_colors.bg_secondary = "#2d2d2d"
mock_colors.bg_tertiary = "#3d3d3d"
mock_colors.text_primary = "#e0e0e0"
mock_colors.text_secondary = "#a0a0a0"
mock_colors.text_muted = "#6a6a6a"
mock_colors.border_subtle = "#3d3d3d"
mock_colors.border_default = "#5a5a5a"
mock_colors.accent_primary = "#1a73e8"
mock_colors.accent_warning = "#ffc107"
mock_colors.accent_error = "#d32f2f"
mock_colors.accent_success = "#4caf50"
mock_colors.accent_info = "#4fc3f7"

sys.modules["styles"] = MagicMock()
sys.modules["styles"].COLORS = mock_colors
sys.modules["styles"].button_style = MagicMock(return_value="")


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_config_file(temp_dir: Path) -> Path:
    """Create a temporary config file path."""
    return temp_dir / "mcp_servers.json"


@pytest.fixture
def sample_mcp_config() -> dict:
    """Sample MCP server configuration."""
    return {
        "mcp_servers": {
            "test-server": {
                "type": "stdio",
                "command": "python",
                "args": ["-m", "test_server"],
            },
            "http-server": {
                "type": "http",
                "url": "http://localhost:8080",
            },
        }
    }


@pytest.fixture
def mock_code_puppy_config(temp_config_file: Path):
    """Mock code_puppy.config.MCP_SERVERS_FILE."""
    with patch("services.mcp_config_service.MCP_SERVERS_FILE", str(temp_config_file)):
        yield temp_config_file


@pytest.fixture
def mock_qt_app():
    """Mock Qt application for widget tests.

    Note: For full widget testing, use pytest-qt which provides
    a proper QApplication fixture.
    """
    with patch("PySide6.QtWidgets.QApplication"):
        yield


@pytest.fixture
def sample_message_history() -> list:
    """Sample message history for session tests."""
    # Mimics the structure from pydantic-ai messages
    class MockPart:
        def __init__(self, content: str, part_kind: str = "text"):
            self.content = content
            self.part_kind = part_kind

    class MockMessage:
        def __init__(self, kind: str, parts: list):
            self.kind = kind
            self.parts = parts

    return [
        MockMessage("request", [MockPart("Hello, help me with code")]),
        MockMessage("response", [MockPart("I'd be happy to help!")]),
        MockMessage("request", [MockPart("Write a function")]),
        MockMessage("response", [MockPart("Here's a function:\n```python\ndef foo():\n    pass\n```")]),
    ]
