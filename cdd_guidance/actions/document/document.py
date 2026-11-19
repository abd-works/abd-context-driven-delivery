"""Document — observe existing state on each provided context tool."""

from __future__ import annotations

from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.guidance.stages import on_stage
from harness.agent_tools import agent_instructions, agent_toolset, instructions, tools
from harness.installation.files import skill
from harness.mcp.mcp_annotations import mcp

# Document's place among a stage's actions: last, after render, since it records what is there rather than making it.
DOCUMENT_RANK_ON_STAGE = 6


@agent_toolset
class Document(GuidanceAction):
    """Document existing state for provided context tools."""

    # Document records what is there without correcting it, so an edit it makes is no work the rules should steer.
    injects_rules = False

    @on_stage(DOCUMENT_RANK_ON_STAGE)
    @mcp
    @skill
    @agent_instructions
    def document(self, guidance: GuidanceArg, paths: list[str]) -> str:
        """Record what already exists for the listed guidance without correcting it. Read contexts and templates, and write the observed state under the session's root so violations are flagged, not fixed.
        paths: the files and folders to scan, named from the project's root or absolute. A path that is not there, or not under the session's root, is refused."""
        self._work_on(guidance)
        scanned = self._paths_to_scan(paths)
        instructions(scanned)
        def on(item) -> str:
            if isinstance(item, str):
                return ""
            return "\n\n".join(part.strip() for part in (item.templates, item.generate_output()) if part and part.strip())

        self.run(on, action="document")
        "After writing, call refresh with exactly the files you wrote, so the session's graph holds them as they are now; nothing watches the files."
        if self._session is not None:
            tools(self.graph.refresh)
        return "Document existing state under the session's root, which the session section names - violations flagged, none corrected."

    def _paths_to_scan(self, paths: list[str]) -> str:
        """The paths the call names to scan, each checked to be there under the session's root and named from it; none
        when the call names none."""
        found = self.files.paths_to_read(paths)
        if not found:
            return ""
        root = self._session.work_root if self._session is not None else None
        named = [path.relative_to(root).as_posix() if root is not None and path.is_relative_to(root) else path.as_posix() for path in found]
        return f"Scan these paths: {', '.join(named)}"
