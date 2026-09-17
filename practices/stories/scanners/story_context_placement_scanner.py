"""story-context-placement - story-context.md sits at the right level."""

from __future__ import annotations

from story_workspace_base import StoryWorkspaceScanner


class StoryContextPlacementScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        for ctx in workspace.story_contexts:
            if ctx.is_leaf_folder:
                yield self.violation(
                    f"story-context.md at {ctx.folder!r} is placed at a leaf folder; "
                    "move it to the parent epic or sub-epic root",
                    location=self.loc(ctx, ctx.folder),
                    severity="error",
                )
                continue

            missing: list[str] = []
            if not ctx.title:
                missing.append("H1 title")
            if not ctx.has_status:
                missing.append("**Status:**")
            if not ctx.has_stories_in_scope or not ctx.stories_in_scope:
                missing.append("**Stories in scope:** with at least one bullet")
            if missing:
                yield self.violation(
                    f"story-context.md at {ctx.folder!r} is missing: "
                    f"{', '.join(missing)}",
                    location=self.loc(ctx, ctx.folder),
                    severity="error",
                )
