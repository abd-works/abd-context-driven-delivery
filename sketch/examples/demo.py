"""Demo toolset used by sketch_spec — a minimal @sketch-wrapped @action.

Living in a real .py file (not string-eval'd) so inspect.getsource can read it.
"""
from __future__ import annotations

from action.action import action
from sketch import sketch
from tools.tool import tool, toolset


@toolset
class Demo:
    """Demo generator for testing the @sketch → ActionExpander integration."""

    @tool
    def do_thing(self) -> str:
        """Do a thing."""
        return "done"

    @sketch
    @action
    def generate(self) -> str:
        """Base generate action body — should appear after the sketch preamble."""
        """Step 1 — call do_thing."""
        self.do_thing()
        return "generate done"
