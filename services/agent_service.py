"""Agent service abstraction for Dependency Inversion.

Provides an interface for agent operations, allowing panels to depend on
abstractions rather than concrete code_puppy implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass
class AgentInfo:
    """Data transfer object for agent information."""
    name: str
    display_name: str
    description: str
    is_current: bool = False


class AgentServiceProtocol(Protocol):
    """Protocol defining agent service operations.

    Panels depend on this protocol, not concrete implementations (DIP).
    """

    def get_available_agents(self) -> list[AgentInfo]:
        """Get list of available agents with their info."""
        ...

    def get_current_agent_name(self) -> Optional[str]:
        """Get the name of the currently active agent."""
        ...

    def set_current_agent(self, agent_name: str) -> bool:
        """Set the current agent by name. Returns True on success."""
        ...


class AgentService:
    """Concrete implementation of AgentServiceProtocol.

    Wraps code_puppy agent functions to provide a clean interface.
    """

    def get_available_agents(self) -> list[AgentInfo]:
        """Get list of available agents with their info."""
        from code_puppy.agents import (
            get_available_agents,
            get_agent_descriptions,
            get_current_agent,
        )

        available = get_available_agents()
        descriptions = get_agent_descriptions()
        current = get_current_agent()
        current_name = current.name if current else ""

        agents = []
        for agent_name, display_name in available.items():
            agents.append(AgentInfo(
                name=agent_name,
                display_name=display_name,
                description=descriptions.get(agent_name, "No description"),
                is_current=(agent_name == current_name),
            ))

        return sorted(agents, key=lambda a: a.name.lower())

    def get_current_agent_name(self) -> Optional[str]:
        """Get the name of the currently active agent."""
        from code_puppy.agents import get_current_agent

        current = get_current_agent()
        return current.name if current else None

    def set_current_agent(self, agent_name: str) -> bool:
        """Set the current agent by name. Returns True on success."""
        from code_puppy.agents import set_current_agent

        try:
            set_current_agent(agent_name)
            return True
        except Exception:
            return False


# Singleton instance for convenience
_agent_service: Optional[AgentService] = None


def get_agent_service() -> AgentService:
    """Get the singleton agent service instance."""
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service
