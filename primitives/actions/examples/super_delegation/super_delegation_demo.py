"""Plain demo for super() delegation in action bodies - no chain decorators."""
from __future__ import annotations

from primitives.actions.action import _ActionRunner, agent_instructions
from tools.tool import Toolset, agent_tool, toolset


@toolset
class SuperBase:
    """Base toolset with a plain @agent_instructions."""

    @agent_tool
    def do_work(self) -> str:
        """Perform a unit of work."""
        return "work done"

    @agent_instructions
    def generate(self) -> str:
        """Base generate instructions."""
        self.do_work()
        return "generate done"


SuperBase._is_toolset = True  # type: ignore[attr-defined]
_ActionRunner.instance().validate_toolset(SuperBase)


@toolset
class ExplicitSuperChild(SuperBase):
    """Child that calls super().generate() explicitly."""

    @agent_instructions
    def generate(self) -> str:
        """Child generate instructions."""
        super().generate()
        return "child generate done"


ExplicitSuperChild._is_toolset = True  # type: ignore[attr-defined]
_ActionRunner.instance().validate_toolset(ExplicitSuperChild)


@toolset
class EmptySuperChild(SuperBase):
    """Child with empty body - auto-delegates to parent generate."""

    @agent_instructions
    def generate(self) -> str: ...


EmptySuperChild._is_toolset = True  # type: ignore[attr-defined]
_ActionRunner.instance().validate_toolset(EmptySuperChild)


@toolset
class EmptyWithReturn(SuperBase):
    """Empty steps but custom return - parent tools/prose, child result template."""

    @agent_instructions
    def generate(self) -> str:
        ...
        return "child result only"


EmptyWithReturn._is_toolset = True  # type: ignore[attr-defined]
_ActionRunner.instance().validate_toolset(EmptyWithReturn)
