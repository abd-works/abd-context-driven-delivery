"""Satisfy — validate then generate fixes on each provided context tool."""

from __future__ import annotations

from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset
from installation.files import Skill
from harness.mcp.mcp_server import Mcp

@agent_toolset
class Satisfy(GuidanceAction):
    """Satisfy artifacts for provided context tools."""

    @Mcp
    @Skill
    @agent_instructions
    def satisfy(self, guidance: GuidanceArg) -> str:
        """Run validate for each provided Guidance against the content; apply generate_fixes_from_validate, then validate again when done. Pass a string to satisfy that text once."""
        from validate.validate import Validate

        def on(item) -> None:
            if isinstance(item, str):
                Validate().validate(item)
                return
            Validate().validate(guidance=[item])
            item.generate_fixes_from_validate()

        self.run(guidance, on, action="satisfy")
        return "When done, run validate on artifacts under {session.path}/."
