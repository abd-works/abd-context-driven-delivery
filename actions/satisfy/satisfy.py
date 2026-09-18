"""Satisfy — validate then generate fixes on each provided context tool."""

from __future__ import annotations

from lifecycle import LifecycleAction
from agent_tools import agent_instructions, agent_toolset
from installation.harness_files.harness_files import skill
from installation.mcp.mcp_server import mcp
from workspace import SessionLog

@agent_toolset
class Satisfy(LifecycleAction):
    """Satisfy artifacts for provided context tools."""

    @mcp
    @skill
    @agent_instructions
    def satisfy(self, tools: list) -> str:
        """Run validate for each provided guidance tool against the content; apply generate_fixes_from_validate, then validate again when done."""
        self.begin(tools, action="satisfy")
        from validate.validate import Validate

        for tool in self.listed():
            Validate().validate(tools=[tool])
            tool.generate_fixes_from_validate()
            SessionLog.instance().append(
                toolset=tool.registration_name,
                name="satisfy",
                summary="satisfy",
                ok=True,
                role="run",
            )
        self.end()
        return "When done, run validate on artifacts under {session.path}/."
