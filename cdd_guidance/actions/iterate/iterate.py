"""Iterate on formal generate output through a grill loop with validate + one fix pass.

Iterate is a standalone action: for each listed guidance it grills, then generates the slice the answers unlocked.
"""
from __future__ import annotations

from cdd_guidance.actions.grill_context.grill_context import GrillContext
from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset, instructions, tools
from harness.agent_tools.agent_tools import agent_tool
from harness.installation.files import skill
from harness.mcp.mcp_annotations import mcp

@agent_toolset
class Iterate(GuidanceAction):
    """Iterate formal generate output with scanners - tiny grilled slices only; never dump a whole artifact in one cycle."""

    @mcp
    @agent_tool
    def mark_iterate_round(self) -> str:
        """Record that an iterate round's show/validate/fix step is due (no I/O).
        Call only after 2-3 grill answers that unlock ONE small slice - never as a prelude to dumping the whole artifact."""
        return "iterate-round"

    @mcp
    @skill
    @agent_instructions
    def iterate(self, guidance: GuidanceArg) -> str:
        """Grill the plan with grill: ask short framed questions and wait for answers. After each small batch of answers, generate or revise only the final deliverable slice those answers unlocked, validate it, apply one fix pass, and get user feedback before asking more. Work in short cycles until the deliverables are agreed. Do not dump the whole product in one cycle, and do not sketch — iterate the formal artifacts."""
        self._work_on(guidance)
        self.log_running("iterate")
        instructions(self._grill().grill)
        "After each slice is generated, validated and fixed once, call mark_iterate_round, show the slice, and get feedback before the next grill question."
        tools(self.mark_iterate_round)
        return "Iterate complete; generate instructions applied."

    def _grill(self) -> GrillContext:
        """The grill each cycle runs, which ends in the generate of the slice its answers unlocked: started inside this
        iterate, so it works on what the iterate lists."""
        return self._inside(GrillContext)
