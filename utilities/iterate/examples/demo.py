"""Demo toolset used by iterate_spec — a minimal @iterate-wrapped @action.

Living in a real .py file (not string-eval'd) so inspect.getsource can read it.
"""
from __future__ import annotations

from primitives.actions.action import action
from iterate import iterate
from tools.tool import tool, toolset


@toolset
class Demo:
    """Demo generator for testing the @iterate → ActionExpander integration."""

    @tool
    def do_thing(self) -> str:
        """Do a thing."""
        return "done"

    @iterate
    @action
    def generate(self) -> str:
        """Base generate action body — should appear after the iterate preamble."""
        """Step 1 — call do_thing."""
        self.do_thing()
        return "generate done"
