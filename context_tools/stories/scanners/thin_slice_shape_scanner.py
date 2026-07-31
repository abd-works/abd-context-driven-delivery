"""thin-slice-shape - validates the fundamental increments skeleton."""

from __future__ import annotations

from story_workspace_base import StoryWorkspaceScanner


class ThinSliceShapeScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_increments():
            yield self.violation(
                "No thin-slice found or thin-slice contains no increments",
                location="thin-slicing.md",
                severity="error",
            )
            return

        for increment in workspace.story_map.increments:
            if not increment.stories:
                yield self.violation(
                    f"Increment {increment.name!r} lists no stories",
                    location=self.loc(increment, f"increment {increment.name!r}"),
                    severity="error",
                )
