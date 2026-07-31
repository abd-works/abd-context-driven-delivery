"""brownfield-story-mapping - no lingering UNVERIFIED evidence markers."""

from __future__ import annotations

from story_workspace_base import StoryWorkspaceScanner

_UNVERIFIED_MARKER = "**UNVERIFIED**"


class BrownfieldStoryMappingScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        for ctx in workspace.story_contexts:
            source = ctx.source
            if source is None:
                continue
            source_path = workspace.root / source.file
            if not source_path.exists():
                continue
            text = source_path.read_text(encoding="utf-8", errors="replace")
            if _UNVERIFIED_MARKER in text:
                yield self.violation(
                    f"Story context {source.file} still marks evidence as {_UNVERIFIED_MARKER}",
                    location=self.loc(ctx, source.file),
                    severity="warning",
                )
