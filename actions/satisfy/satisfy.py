"""Satisfy — validate then generate fixes on each provided context tool."""

from __future__ import annotations

from installer.installer_tool import prompt
from lifecycle import LifecycleAction
from agent_tools import agent_instructions, agent_toolset
from workspace import SessionLog
from primitives.installer.installation import toolset_ref_for_type


@agent_toolset
class Satisfy(LifecycleAction):
    """Satisfy artifacts for provided context tools."""

    @prompt
    @agent_instructions
    def satisfy(self, tools: list) -> str:
        """satisfy"""
        self.begin(tools, action="satisfy")
        from validate.validate import Validate

        for tool in self.listed():
            Validate().validate(tools=[tool])
            tool.generate_fixes_from_validate()
            SessionLog.instance().append(
                toolset=toolset_ref_for_type(type(tool)),
                name="satisfy",
                summary="satisfy",
                ok=True,
                role="run",
            )
        self.end()
        return "When done, run validate on artifacts under {session.path}/."
