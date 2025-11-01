"""Agent registry for managing verification agents."""

from __future__ import annotations

from typing import Dict, Type

from verification_toolkit import VerificationAgent
from verification_toolkit.demo_agent import DemoVerificationAgent


class AgentRegistry:
    """Registry for verification agents."""

    def __init__(self):
        self._agents: Dict[str, Type[VerificationAgent]] = {}
        self._register_defaults()

    def _register_defaults(self):
        """Register built-in agents."""
        self.register("demo", DemoVerificationAgent)

    def register(self, name: str, agent_class: Type[VerificationAgent]) -> None:
        """Register an agent class."""
        self._agents[name] = agent_class

    def get_agent(self, name: str, **kwargs) -> VerificationAgent:
        """Get an agent instance by name."""
        if name not in self._agents:
            raise ValueError(f"Unknown agent: {name}")
        return self._agents[name](**kwargs)

    def list_agents(self) -> list[str]:
        """List registered agent names."""
        return list(self._agents.keys())


# Global registry instance
_registry = AgentRegistry()


def get_agent(name: str, **kwargs) -> VerificationAgent:
    """Get an agent instance from the global registry."""
    return _registry.get_agent(name, **kwargs)


def register_agent(name: str, agent_class: Type[VerificationAgent]) -> None:
    """Register an agent in the global registry."""
    _registry.register(name, agent_class)