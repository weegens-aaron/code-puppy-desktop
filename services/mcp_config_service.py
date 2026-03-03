"""MCP server configuration persistence service.

Handles reading and writing MCP server configurations to the config file.
This module follows SoC by separating persistence from UI concerns.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

from code_puppy.config import MCP_SERVERS_FILE

logger = logging.getLogger(__name__)


class MCPConfigService:
    """Service for managing MCP server configuration persistence."""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize the service.

        Args:
            config_file: Path to config file. Defaults to MCP_SERVERS_FILE.
        """
        self._config_file = Path(config_file or MCP_SERVERS_FILE)

    def load_all(self) -> dict[str, dict[str, Any]]:
        """Load all server configurations from the config file.

        Returns:
            Dictionary mapping server names to their configurations
        """
        if not self._config_file.exists():
            return {}

        try:
            with open(self._config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("mcp_servers", {})
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load MCP config: {e}")
            return {}

    def save_server(self, name: str, server_type: str, config: dict[str, Any]) -> None:
        """Save a server configuration to the config file.

        Args:
            name: Server name
            server_type: Server type (stdio, http, sse)
            config: Server configuration dict

        Raises:
            OSError: If file operations fail
        """
        data = self._load_raw_data()
        servers = data.setdefault("mcp_servers", {})

        # Add type to config
        save_config = config.copy()
        save_config["type"] = server_type
        servers[name] = save_config

        self._write_data(data)
        logger.info(f"Saved MCP server config: {name}")

    def remove_server(self, name: str) -> bool:
        """Remove a server configuration from the config file.

        Args:
            name: Server name to remove

        Returns:
            True if server was removed, False if not found
        """
        if not self._config_file.exists():
            return False

        try:
            data = self._load_raw_data()
            servers = data.get("mcp_servers", {})

            if name not in servers:
                return False

            del servers[name]
            self._write_data(data)
            logger.info(f"Removed MCP server config: {name}")
            return True
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to remove server {name}: {e}")
            return False

    def _load_raw_data(self) -> dict[str, Any]:
        """Load raw JSON data from config file."""
        if self._config_file.exists():
            with open(self._config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _write_data(self, data: dict[str, Any]) -> None:
        """Write data to config file, creating directories if needed."""
        self._config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


# Singleton instance for convenience
_service: Optional[MCPConfigService] = None


def get_mcp_config_service() -> MCPConfigService:
    """Get the singleton MCP config service instance."""
    global _service
    if _service is None:
        _service = MCPConfigService()
    return _service


def format_uptime(seconds: float) -> str:
    """Format uptime in human-readable form.

    Args:
        seconds: Uptime in seconds

    Returns:
        Formatted string like "5s", "2m 30s", or "1h 15m"
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
