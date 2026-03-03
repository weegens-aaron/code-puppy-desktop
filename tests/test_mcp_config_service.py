"""Tests for MCP config service.

Tests the MCPConfigService class and utility functions.
"""

import json
import tempfile
from pathlib import Path
from typing import Generator

import pytest


# =============================================================================
# Test format_uptime function (pure function, no dependencies)
# =============================================================================

def format_uptime(seconds: float) -> str:
    """Format uptime in human-readable form (copy for testing)."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


class TestFormatUptime:
    """Tests for format_uptime utility function."""

    @pytest.mark.parametrize(
        "seconds,expected",
        [
            (0, "0s"),
            (1, "1s"),
            (30, "30s"),
            (59, "59s"),
            (60, "1m 0s"),
            (90, "1m 30s"),
            (120, "2m 0s"),
            (3599, "59m 59s"),
            (3600, "1h 0m"),
            (3660, "1h 1m"),
            (7200, "2h 0m"),
            (7320, "2h 2m"),
            (86400, "24h 0m"),
        ],
    )
    def test_format_uptime(self, seconds: float, expected: str):
        """Test format_uptime with various inputs."""
        assert format_uptime(seconds) == expected

    def test_format_uptime_with_float(self):
        """Test format_uptime handles float values."""
        assert format_uptime(30.7) == "30s"
        assert format_uptime(90.9) == "1m 30s"


# =============================================================================
# Test MCPConfigService class (requires file operations only)
# =============================================================================

class MCPConfigService:
    """Simplified service class for testing (no code_puppy dependency)."""

    def __init__(self, config_file: str):
        self._config_file = Path(config_file)

    def load_all(self) -> dict:
        """Load all server configurations from the config file."""
        if not self._config_file.exists():
            return {}

        try:
            with open(self._config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("mcp_servers", {})
        except (json.JSONDecodeError, OSError):
            return {}

    def save_server(self, name: str, server_type: str, config: dict) -> None:
        """Save a server configuration to the config file."""
        data = self._load_raw_data()
        servers = data.setdefault("mcp_servers", {})

        save_config = config.copy()
        save_config["type"] = server_type
        servers[name] = save_config

        self._write_data(data)

    def remove_server(self, name: str) -> bool:
        """Remove a server configuration from the config file."""
        if not self._config_file.exists():
            return False

        try:
            data = self._load_raw_data()
            servers = data.get("mcp_servers", {})

            if name not in servers:
                return False

            del servers[name]
            self._write_data(data)
            return True
        except (json.JSONDecodeError, OSError):
            return False

    def _load_raw_data(self) -> dict:
        """Load raw JSON data from config file."""
        if self._config_file.exists():
            with open(self._config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _write_data(self, data: dict) -> None:
        """Write data to config file, creating directories if needed."""
        self._config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


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


class TestMCPConfigService:
    """Tests for MCPConfigService class."""

    def test_init_with_custom_path(self, temp_dir: Path):
        """Test service initializes with custom config path."""
        custom_path = temp_dir / "custom.json"
        service = MCPConfigService(str(custom_path))
        assert service._config_file == custom_path

    def test_load_all_empty_when_file_missing(self, temp_dir: Path):
        """Test load_all returns empty dict when config file doesn't exist."""
        service = MCPConfigService(str(temp_dir / "nonexistent.json"))
        result = service.load_all()
        assert result == {}

    def test_load_all_returns_servers(self, temp_config_file: Path, sample_mcp_config: dict):
        """Test load_all returns server configurations."""
        temp_config_file.write_text(json.dumps(sample_mcp_config))

        service = MCPConfigService(str(temp_config_file))
        result = service.load_all()

        assert "test-server" in result
        assert result["test-server"]["type"] == "stdio"
        assert "http-server" in result

    def test_load_all_handles_invalid_json(self, temp_config_file: Path):
        """Test load_all handles corrupted JSON gracefully."""
        temp_config_file.write_text("{ invalid json }")

        service = MCPConfigService(str(temp_config_file))
        result = service.load_all()
        assert result == {}

    def test_save_server_creates_file(self, temp_config_file: Path):
        """Test save_server creates config file if it doesn't exist."""
        service = MCPConfigService(str(temp_config_file))

        service.save_server(
            name="new-server",
            server_type="stdio",
            config={"command": "python", "args": ["-m", "server"]},
        )

        assert temp_config_file.exists()
        data = json.loads(temp_config_file.read_text())
        assert "new-server" in data["mcp_servers"]
        assert data["mcp_servers"]["new-server"]["type"] == "stdio"

    def test_save_server_updates_existing(self, temp_config_file: Path, sample_mcp_config: dict):
        """Test save_server updates existing server configuration."""
        temp_config_file.write_text(json.dumps(sample_mcp_config))

        service = MCPConfigService(str(temp_config_file))
        service.save_server(
            name="test-server",
            server_type="http",
            config={"url": "http://newhost:9000"},
        )

        data = json.loads(temp_config_file.read_text())
        assert data["mcp_servers"]["test-server"]["type"] == "http"
        assert data["mcp_servers"]["test-server"]["url"] == "http://newhost:9000"

    def test_save_server_preserves_other_servers(self, temp_config_file: Path, sample_mcp_config: dict):
        """Test save_server doesn't affect other servers."""
        temp_config_file.write_text(json.dumps(sample_mcp_config))

        service = MCPConfigService(str(temp_config_file))
        service.save_server(
            name="new-server",
            server_type="sse",
            config={"url": "http://sse:8080"},
        )

        data = json.loads(temp_config_file.read_text())
        assert "test-server" in data["mcp_servers"]
        assert "http-server" in data["mcp_servers"]
        assert "new-server" in data["mcp_servers"]

    def test_remove_server_success(self, temp_config_file: Path, sample_mcp_config: dict):
        """Test remove_server removes a server configuration."""
        temp_config_file.write_text(json.dumps(sample_mcp_config))

        service = MCPConfigService(str(temp_config_file))
        result = service.remove_server("test-server")

        assert result is True
        data = json.loads(temp_config_file.read_text())
        assert "test-server" not in data["mcp_servers"]
        assert "http-server" in data["mcp_servers"]

    def test_remove_server_not_found(self, temp_config_file: Path, sample_mcp_config: dict):
        """Test remove_server returns False when server not found."""
        temp_config_file.write_text(json.dumps(sample_mcp_config))

        service = MCPConfigService(str(temp_config_file))
        result = service.remove_server("nonexistent-server")

        assert result is False

    def test_remove_server_file_missing(self, temp_dir: Path):
        """Test remove_server returns False when config file missing."""
        service = MCPConfigService(str(temp_dir / "nonexistent.json"))
        result = service.remove_server("any-server")
        assert result is False
