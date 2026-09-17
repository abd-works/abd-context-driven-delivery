"""Generate — run generate on each provided context tool."""

from __future__ import annotations

from lifecycle import LifecycleAction
from agent_tools import agent_instructions, agent_toolset
from installer.installer_tool import prompt
from workspace import SessionLog
from primitives.installer.installation import toolset_ref_for_type


@agent_toolset
class Generate(LifecycleAction):
    """Generate artifacts for provided context tools."""

    @prompt
    @agent_instructions
    def generate(self, tools: list) -> str:
        """generate"""
        self.begin(tools, action="generate")
        for tool in self.listed():
            tool.guidance
            tool.generate_output()
            self.generate_fixes_from_validate()
            self.add_generate_header_to_generated()
            SessionLog.instance().append(
                toolset=toolset_ref_for_type(type(tool)),
                name="generate",
                summary="generate",
                ok=True,
                role="run",
            )
        self.end()
        return "When done, run validate."

    @agent_instructions
    def add_generate_header_to_generated(self) -> str:
        """Prepend the following block verbatim as the very first lines of the file you are writing - before any imports, before any code."""
        return (
            '"""\n'
            '"""\n'
        )

    @agent_instructions
    def generate_output(self) -> str:
        """"""
        return ""

    @agent_instructions
    def generate_fixes_from_validate(self) -> str:
        """generate_fixes_from_validate"""
        return ""
