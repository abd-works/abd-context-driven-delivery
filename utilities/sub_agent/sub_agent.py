"""Sub-agent decorator - marks a tool as a non-blocking background sub-agent launch.

Usage::

    @sub_agent
    @tool
    def diagnose(self) -> str:
        \"\"\"Full instructions for the sub-agent go here - inline in the docstring.\"\"\"

When the agent reads the manifest it will see ``kind: sub_agent`` with
``launch: non_blocking``.  It must launch a background sub-agent using
the ``instructions`` text rather than executing the work inline.
"""
from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable

from tools.tool import _SignatureReader


@dataclass(frozen=True)
class SubAgentTool:
    """One sub-agent-dispatched capability on a toolset.

    Appears in the manifest as ``kind: sub_agent`` so the calling agent knows
    to launch a non-blocking background sub-agent instead of running inline.
    """

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
    """Mark a method as a non-blocking sub-agent launch.

    Stack on top of ``@tool``::

        @sub_agent
        @tool
        def my_task(self) -> str:
            \"\"\"Instructions sent verbatim to the sub-agent.\"\"\"

    ``@tool`` runs first and sets ``_is_tool = True``.  ``@sub_agent`` then
    sets ``_is_sub_agent = True`` and suppresses ``_is_tool`` so standard tool
    discovery skips it and ``discover_sub_agent_tools`` picks it up instead.
    """
    func._is_sub_agent = True  # type: ignore[attr-defined]
    func._is_tool = False  # type: ignore[attr-defined]
    return func


def discover_sub_agent_tools(instance: Any) -> dict[str, SubAgentTool]:
    """Return all ``@sub_agent``-marked methods on *instance* as ``SubAgentTool`` objects."""
    discovered: dict[str, SubAgentTool] = {}
    for name, member in inspect.getmembers(instance.__class__, predicate=inspect.isfunction):
        if getattr(member, "_is_sub_agent", False):
            discovered[name] = SubAgentTool(name=name, callable=getattr(instance, name))
    return discovered
