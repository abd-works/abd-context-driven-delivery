"""Demo toolsets used by grill_context_decorator_spec - real .py so inspect.getsource works.

All demo classes are self-contained within the grill_context package.
No imports from sketch, ooad, or any other domain decorator package.
DemoStack uses a local stub decorator (stub_outer) to verify stacking without
taking a dependency on @sketch.
"""
from __future__ import annotations

from primitives.actions.action import action, add_action_wrapper, require_action
from grill_context import grill_with_context
from tools.tool import tool, toolset


def _stub_outer_session(self) -> str:  # type: ignore[misc]
    """Stub outer wrapper instructions - stands in for any real outermost decorator."""
    return "stub outer done"


def stub_outer(func):  # type: ignore[misc]
    """Toy decorator that acts as a second wrapper above @grill_with_context."""
    require_action(func, "stub_outer")
    add_action_wrapper(func, name="stub_outer", chained_action=_stub_outer_session)
    return func


@toolset
class DemoGrill:
    """@grill_with_context-only demo - one decorated action, one unwrapped action."""

    @tool
    def do_thing(self) -> str:
        """Do a thing."""
        return "done"

    @grill_with_context
    @action
    def generate(self) -> str:
        """Demo grill base body - appears after the grill preamble."""
        """Step 1 - call do_thing."""
        self.do_thing()
        return "generate done"

    @action
    def ping(self) -> str:
        """Unwrapped action for chain-omission assertion."""
        return "pong"


@toolset
class DemoStack:
    """stub_outer stacked with @grill_with_context - declaration order top-down."""

    @tool
    def do_thing(self) -> str:
        """Do a thing."""
        return "done"

    @stub_outer
    @grill_with_context
    @action
    def generate(self) -> str:
        """Stacked-decorator base body."""
        """Step 1 - call do_thing."""
        self.do_thing()
        return "generate done"
