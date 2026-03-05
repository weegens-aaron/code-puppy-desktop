"""Services for the desktop application."""

from services.agent_bridge import AgentBridge
from services.mcp_config_service import (
    MCPConfigService,
    get_mcp_config_service,
    format_uptime,
)
from services.status_bar_manager import StatusBarManager
from services.streaming_handler import StreamingHandler
from services.session_manager import SessionManager
from services.agent_service import (
    AgentService,
    AgentServiceProtocol,
    AgentInfo,
    get_agent_service,
)
from services.model_service import (
    ModelService,
    ModelServiceProtocol,
    ModelInfo,
    get_model_service,
)

__all__ = [
    # Core services
    "AgentBridge",
    "MCPConfigService",
    "get_mcp_config_service",
    "format_uptime",
    # App services (SRP extractions)
    "StatusBarManager",
    "StreamingHandler",
    "SessionManager",
    # Domain services (DIP abstractions)
    "AgentService",
    "AgentServiceProtocol",
    "AgentInfo",
    "get_agent_service",
    "ModelService",
    "ModelServiceProtocol",
    "ModelInfo",
    "get_model_service",
]
