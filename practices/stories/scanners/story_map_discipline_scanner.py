"""story-map-discipline — the map must carry scope boundaries."""

from __future__ import annotations

from story_workspace_base import StoryWorkspaceScanner


class StoryMapDisciplineScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_story_map():
            return

        md_candidate = workspace.root / "story-map.md"
        if md_candidate.exists():
            source_path = md_candidate
        else:
            source = getattr(workspace.story_map, "source", None)
            if source is None:
                return
            source_path = workspace.root / source.file
            if not source_path.exists():
                return

        text = source_path.read_text(encoding="utf-8", errors="replace")
        location = source_path.relative_to(workspace.root).as_posix() + ":1"

        has_section = "## Scope boundary" in text
        has_in_scope = "**In scope:**" in text
        has_out_scope = "**Out of scope:**" in text

        if not has_section:
            yield self.violation(
                "Story map has no '## Scope boundary' section",
                location=location,
                severity="warning",
            )
            return

        if not (has_in_scope and has_out_scope):
            missing = []
            if not has_in_scope:
                missing.append("**In scope:**")
            if not has_out_scope:
                missing.append("**Out of scope:**")
            yield self.violation(
                f"Scope boundary is present but missing: {', '.join(missing)}",
                location=location,
                severity="warning",
            )
