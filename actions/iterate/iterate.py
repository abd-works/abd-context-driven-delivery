"""Iterate on formal generate output through a grill loop with validate + one fix pass.

Iterate is a standalone toolset. The complementary @iterate decorator (see
_decorator.py) marks an @agent_instructions so framework composition prepends
iterate_session (which calls grill_with_context in-method).
"""
from __future__ import annotations

from grill_context.grill_context import GrillContext
from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset
from harness.agent_tools.agent_tools import agent_tool
from installation.files import Skill
from harness.mcp.mcp_server import Mcp

@agent_toolset
class Iterate(GuidanceAction):
    """Iterate formal generate output with scanners - tiny grilled slices only; never dump a whole artifact in one tick."""

    def _grill_context(self) -> GrillContext:
        """GrillContext toolset for in-method composition (not a tool)."""
        return GrillContext()

    def _generate(self):
        from generate.generate import Generate

        return Generate()

    @Mcp
    @agent_tool
    def mark_iterate_tick(self) -> str:
        """Record that an iterate show/validate/fix tick is due (no I/O).
        Call only after 2-3 grill answers that unlock ONE small slice - never as a prelude to dumping the whole artifact."""
        return "iterate-tick"

    @Mcp
    @Skill
    @agent_instructions
    def iterate(self, guidance: GuidanceArg, tools: list[str] = None) -> str:
        """Grill the plan with grill: ask short framed questions and wait for answers. After each small batch of answers, generate or revise only the final deliverable slice those answers unlocked, validate it, apply one fix pass, and get user feedback before asking more. Work in short cycles until the deliverables are agreed. Do not dump the whole product in one tick, and do not sketch — iterate the formal artifacts. Pass a string to iterate that text once."""
        self.run(guidance, self._iterate_item, action="iterate")
        return "Iterate complete; generate instructions applied."

    def _iterate_item(self, item) -> None:
        self._grill_context().grill_with_context()
        self.mark_iterate_tick()
        self._generate().generate(item if isinstance(item, str) else [item])
