"""Satisfy — validate, apply the fixes the report names, and validate again, on each listed guidance."""

from __future__ import annotations

from pathlib import Path

from cdd_guidance.actions.generate.generate import Generate
from cdd_guidance.actions.validate.validate import Validate
from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset, instructions, tools
from harness.installation.files import skill
from harness.mcp.mcp_server import mcp

_SATISFY_MARKDOWN = Path(__file__).with_name("satisfy.md").read_text(encoding="utf-8")


@agent_toolset
class Satisfy(GuidanceAction):
    """Satisfy artifacts for provided context tools."""

    @mcp
    @skill
    @agent_instructions
    def satisfy(self, guidance: GuidanceArg) -> str:
        """Run validate for each listed guidance against the content; apply generate_fixes_from_validate, then validate again when done."""
        self._work_on(guidance)
        self.log_running("satisfy")
        steps = _SATISFY_MARKDOWN.strip()
        instructions(steps)
        rules = self.rules_to_follow()
        instructions(rules)
        tools(self._validate().validate)
        instructions(self._generate().generate_fixes_from_validate)
        return (
            "When every applicable rule passes validate for the artifacts under the session's root, "
            "reply with a short **Fixes** list: file path and rule slug per change."
        )

    def _validate(self) -> Validate:
        """Validate as a tool the agent calls, first and again after its fixes: checking is the agent's step, so
        expanding these instructions saves no report and logs no validate line."""
        return self._inside(Validate).as_tool()

    def _generate(self) -> Generate:
        """The generate whose fixes step follows each validate, working on what this satisfy lists."""
        return self._inside(Generate)
