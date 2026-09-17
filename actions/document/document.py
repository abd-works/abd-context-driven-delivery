"""Document — observe existing state on each provided context tool."""

from __future__ import annotations

from installer.installer_tool import prompt
from lifecycle import LifecycleAction
from agent_tools import agent_instructions, agent_toolset
from workspace import SessionLog
from primitives.installer.installation import toolset_ref_for_type


@agent_toolset
class Document(LifecycleAction):
    """Document existing state for provided context tools."""

    @prompt
    @agent_instructions
    def document(self, tools: list, paths: list[str]) -> str:
        """document"""
        self.begin(tools, action="document")
        for tool in self.listed():
            tool.contexts
            tool.templates
            tool.scanner.scan(paths)
            tool.generate_output()
            SessionLog.instance().append(
                toolset=toolset_ref_for_type(type(tool)),
                name="document",
                summary="document",
                ok=True,
                role="run",
            )
        self.end()
        return "Document existing state under {session.path}/ - violations flagged, none corrected."
