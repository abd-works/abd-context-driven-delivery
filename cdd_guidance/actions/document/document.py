"""Document — observe existing state on each provided context tool."""

from __future__ import annotations

from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset, tools
from harness.installation.files import skill
from harness.mcp.mcp_annotations import mcp

@agent_toolset
class Document(GuidanceAction):
    """Document existing state for provided context tools."""

    # Document records what is there without correcting it, so an edit it makes is no work the rules should steer.
    injects_rules = False

    @mcp
    @skill
    @agent_instructions
    def document(self, guidance: GuidanceArg, paths: list[str]) -> str:
        """Record what already exists for the listed guidance without correcting it. Read contexts and templates, and write the observed state under the session's root so violations are flagged, not fixed.
        paths: the files and folders to scan."""
        self._work_on(guidance)
        def on(item) -> str:
            if isinstance(item, str):
                return ""
            return "\n\n".join(part.strip() for part in (item.templates, item.generate_output()) if part and part.strip())

        self.run(on, action="document")
        "After writing, call refresh with exactly the files you wrote, so the session's graph holds them as they are now; nothing watches the files."
        if self._session is not None:
            tools(self.graph.refresh)
        return "Document existing state under the session's root, which the session section names - violations flagged, none corrected."
