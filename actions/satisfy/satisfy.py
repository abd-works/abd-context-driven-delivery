"""Satisfy — validate then generate fixes on each provided context tool."""

from __future__ import annotations

from guidance_actions import GuidanceArg, GuidanceAction
from agent_tools import agent_instructions, agent_toolset
from installation.harness_files.harness_files import Skill
from installation.mcp.mcp_server import Mcp
from workspace import SessionLog

@agent_toolset
class Satisfy(GuidanceAction):
    """Satisfy artifacts for provided context tools."""

    @Mcp
    @Skill
    @agent_instructions
    def satisfy(self, guidance: GuidanceArg) -> str:
        """Run validate for each provided Guidance host against the content; apply generate_fixes_from_validate, then validate again when done. Pass a string to satisfy that text once."""
        from validate.validate import Validate

        def on(item) -> None:
            if isinstance(item, str):
                Validate().validate(item)
                return
            Validate().validate(guidance=[item])
            item.generate_fixes_from_validate()
            SessionLog.instance().append(
                toolset=item.registration_name,
                name="satisfy",
                summary="satisfy",
                ok=True,
                role="run",
            )

        self.run(guidance, on, action="satisfy")
        return "When done, run validate on artifacts under {session.path}/."
