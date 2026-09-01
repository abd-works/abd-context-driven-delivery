"""Sub-agent decorator — marks a tool as a non-blocking background sub-agent launch."""
from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable

from tools.tool import _SignatureReader


@dataclass(frozen=True)
class SubAgentTool:
    """One sub-agent-dispatched capability on a toolset."""

    name: str
    callable: Callable[..., Any]

    @property
    def instructions(self) -> str:
        return _SignatureReader.instance().member_instructions(self.callable)

    @property
    def signature_entry(self) -> dict[str, Any]:
        entry: dict[str, Any] = {
            "kind": "sub_agent",
            "launch": "non_blocking",
        }
        if self.instructions:
            entry["instructions"] = self.instructions
        reader = _SignatureReader.instance()
        parameters = reader.simple_parameters(self.callable)
        if parameters:
            entry["parameters"] = parameters
        returns = reader.simple_return_type(self.callable)
        if returns:
            entry["returns"] = returns
        return entry

    def add_to_signature(self, signature: dict[str, Any]) -> None:
        signature[self.name] = self.signature_entry


def sub_agent(func: Callable[..., Any]) -> Callable[..., Any]:
    """Mark a method as a non-blocking sub-agent launch."""
    func._is_sub_agent = True  # type: ignore[attr-defined]
    func._is_agent_tool = False  # type: ignore[attr-defined]
    return func


def discover_sub_agent_tools(instance: Any) -> dict[str, SubAgentTool]:
    """Return all ``@sub_agent``-marked methods on *instance* as ``SubAgentTool`` objects."""
    discovered: dict[str, SubAgentTool] = {}
    for name, member in inspect.getmembers(instance.__class__, predicate=inspect.isfunction):
        if getattr(member, "_is_sub_agent", False):
            discovered[name] = SubAgentTool(name=name, callable=getattr(instance, name))
    return discovered


def _register() -> None:
    from tools.extensions import ToolsetExtensions

    ToolsetExtensions.instance().register_signature_discoverer(discover_sub_agent_tools)
    ToolsetExtensions.instance().register_members("sub_agent", discover_sub_agent_tools)


_register()
