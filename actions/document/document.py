"""Document — observe existing state on each provided context tool."""

from __future__ import annotations

from guidance_actions import GuidanceArg, GuidanceAction
from agent_tools import agent_instructions, agent_toolset
from installation.harness_files.harness_files import Skill
from installation.mcp.mcp_server import Mcp
from workspace import SessionLog

@agent_toolset
class Document(GuidanceAction):
    """Document existing state for provided context tools."""

    @Mcp
    @Skill
    @agent_instructions
    def document(self, guidance: GuidanceArg, paths: list[str]) -> str:
        """Record what already exists for the listed Guidance hosts without correcting it. Scan the given paths, read contexts and templates, and write the observed state under the session path so violations are flagged, not fixed. Pass a string to document that text once."""
        def on(item) -> None:
            if isinstance(item, str):
                return
            item.contexts
            item.templates
            item.scanner.scan(paths)
            item.generate_output()
            SessionLog.instance().append(
                toolset=item.registration_name,
                name="document",
                summary="document",
                ok=True,
                role="run",
            )

        self.run(guidance, on, action="document")
        return "Document existing state under {session.path}/ - violations flagged, none corrected."
