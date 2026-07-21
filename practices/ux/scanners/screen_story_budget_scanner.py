"""screen-story-budget — ~4 user stories per screen; 5+ is a warning signal."""

from __future__ import annotations

from ux_workspace_base import UxWorkspaceScanner

_SOFT_MAX = 4


class ScreenStoryBudgetScanner(UxWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_ux_map():
            return
        for screen in workspace.ux_map.screens:
            count = len(screen.story_names)
            if count > _SOFT_MAX:
                yield self.violation(
                    f"screen {screen.name!r} has {count} stories (budget ~{_SOFT_MAX}) — "
                    "look for a missed tab, detail, or mode screen",
                    location=f"screen:{screen.name}",
                    severity="warning",
                )
