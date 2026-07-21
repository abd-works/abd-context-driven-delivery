"""Demo toolsets used by record_decisions_decorator_spec — real .py so inspect.getsource works."""
from __future__ import annotations

from primitives.actions.action import action, add_action_wrapper, require_action
from record_decisions import record_decisions
from tools.tool import tool, toolset


def _stub_outer_session(self) -> str:  # type: ignore[misc]
    """Stub outer wrapper instructions — stands in for any real outermost decorator."""
    return "stub outer done"


def stub_outer(func):  # type: ignore[misc]
    """Toy decorator that acts as a second wrapper above @record_decisions."""
    require_action(func, "stub_outer")
    add_action_wrapper(func, name="stub_outer", chained_action=_stub_outer_session)
    return func


@toolset
class DemoRecord:
    """@record_decisions-only demo — one decorated action, one unwrapped action."""

    @tool
    def do_thing(self) -> str:
        """Do a thing."""
        return "done"

    @record_decisions
    @action
    def generate(self) -> str:
        """Demo record_decisions base body — appears after the CDR preamble."""
        """Step 1 — call do_thing."""
        self.do_thing()
        return "generate done"

    @action
    def ping(self) -> str:
        """Unwrapped action for chain-omission assertion."""
        return "pong"


@toolset
class DemoStack:
    """stub_outer stacked with @record_decisions — declaration order top-down."""

    @tool
    def do_thing(self) -> str:
        """Do a thing."""
        return "done"

    @stub_outer
    @record_decisions
    @action
    def generate(self) -> str:
        """Stacked-decorator base body."""
        """Step 1 — call do_thing."""
        self.do_thing()
        return "generate done"
