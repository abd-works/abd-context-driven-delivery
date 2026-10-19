"""Document — observe existing state on each provided context tool."""

from __future__ import annotations

from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset
from harness.installation.files import Skill
from harness.mcp.mcp_server import Mcp

@agent_toolset
class Document(GuidanceAction):
    """Document existing state for provided context tools."""

    @Mcp
    @Skill
    @agent_instructions
    def document(self, guidance: GuidanceArg, paths: list[str]) -> str:
        """Record what already exists for the listed guidance without correcting it. Read contexts and templates, and write the observed state under the session path so violations are flagged, not fixed.
        paths: the files and folders to scan."""
        self._bind_guidance(guidance)
        def on(item) -> None:
            if isinstance(item, str):
                return
            item.contexts
            item.templates
            scanner = getattr(item, "scanner", None)
            if scanner is not None:
                scanner.scan(paths)
            item.generate_output()

        self.run(guidance, on, action="document")
        return "Document existing state under {session.path}/ - violations flagged, none corrected."
