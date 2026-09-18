"""Document — observe existing state on each provided context tool."""

from __future__ import annotations

from lifecycle import LifecycleAction
from agent_tools import agent_instructions, agent_toolset
from installation.harness_files.harness_files import skill
from installation.mcp.mcp_server import mcp
from workspace import SessionLog

@agent_toolset
class Document(LifecycleAction):
    """Document existing state for provided context tools."""

    @mcp
    @skill
    @agent_instructions
    def document(self, tools: list, paths: list[str]) -> str:
        """Record what already exists for the listed context tools without correcting it. Scan the given paths, read contexts and templates, and write the observed state under the session path so violations are flagged, not fixed."""
        self.begin(tools, action="document")
        for tool in self.listed():
            tool.contexts
            tool.templates
            tool.scanner.scan(paths)
            tool.generate_output()
            SessionLog.instance().append(
                toolset=tool.registration_name,
                name="document",
                summary="document",
                ok=True,
                role="run",
            )
        self.end()
        return "Document existing state under {session.path}/ - violations flagged, none corrected."
