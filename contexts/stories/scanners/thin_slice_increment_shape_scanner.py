"""thin-slice-increment-shape — every increment carries an outcome and stories."""

from __future__ import annotations

from story_workspace_base import StoryWorkspaceScanner


class ThinSliceIncrementShapeScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_increments():
            return
        for inc in workspace.story_map.increments:
            if not (inc.outcome or "").strip():
                yield self.violation(
                    f"Increment {inc.name!r} has no **Outcome:** line",
                    location=self.loc(inc, f"increment {inc.name!r}"),
                    severity="error",
                )
                continue
            if not inc.stories:
                yield self.violation(
                    f"Increment {inc.name!r} has no stories",
                    location=self.loc(inc, f"increment {inc.name!r}"),
                    severity="error",
                )
