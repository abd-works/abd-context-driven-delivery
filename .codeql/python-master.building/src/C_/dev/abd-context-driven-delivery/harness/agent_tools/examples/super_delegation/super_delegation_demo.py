"""Plain demo for super() delegation in action bodies."""
from __future__ import annotations

from harness.agent_tools.agent_tools import (
    agent_instructions,
    agent_tool,
    agent_toolset,
    tools,
)


@agent_toolset
class SuperBase:
    """Base toolset with a plain @agent_instructions."""

    @agent_tool
    def do_work(self) -> str:
        """Perform a unit of work."""
        return "work done"

    @agent_instructions
    def generate(self) -> str:
        """Base generate instructions."""
        "Base generate instructions."
        tools(self.do_work())
        return "generate done"


@agent_toolset
class ExplicitSuperChild(SuperBase):
    """Child that calls super().generate() explicitly."""

    @agent_instructions
    def generate(self) -> str:
        """Child generate instructions."""
        "Child generate instructions."
        super().generate()
        return "child generate done"


@agent_toolset
class EmptySuperChild(SuperBase):
    """Child with empty body - auto-delegates to parent generate."""

    @agent_instructions
    def generate(self) -> str: ...


@agent_toolset
class EmptyWithReturn(SuperBase):
    """Empty steps but custom return - parent tools/prose, child result template."""

    @agent_instructions
    def generate(self) -> str:
        ...
        return "child result only"
