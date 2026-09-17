"""Register sub-agent tools with ToolsetExtensions — import this package to attach them."""
from __future__ import annotations

from sub_agent.sub_agent import discover_sub_agent_tools
from primitives.installer.extensions import ToolsetExtensions

_registered = False


def register() -> None:
    global _registered
    if _registered:
        return
    ToolsetExtensions.instance().register_members("sub_agent", discover_sub_agent_tools)
    _registered = True


register()
