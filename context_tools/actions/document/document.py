"""Document — observe existing state on each provided context tool."""

from __future__ import annotations

from harness.harness_tool import prompt
from lifecycle import LifecycleAction
from primitives.actions.action import agent_instructions, agentic_toolset
from workspace import SessionLog


@agentic_toolset
class Document(LifecycleAction):
    """Document existing state for provided context tools."""

    @prompt
    @agent_instructions
    def document(self, tools: list, paths: list[str]) -> str:
        """document"""
        self.begin(tools, action="document")
        for tool in self.context_tools(tools):
            tool.contexts
            tool.templates
            tool.scanner.scan(paths)
            tool.generate_output()
            SessionLog.instance().append(
                toolset=type(tool).manifest_path,
                name="document",
                summary="document",
                ok=True,
                role="run",
            )
        self.end()
        return "Document existing state under {session.path}/ - violations flagged, none corrected."
