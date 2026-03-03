"""Services for the desktop application."""

from services.agent_bridge import AgentBridge
from services.mcp_config_service import (
    MCPConfigService,
    get_mcp_config_service,
    format_uptime,
)

__all__ = [
    "AgentBridge",
    "MCPConfigService",
    "get_mcp_config_service",
    "format_uptime",
]
