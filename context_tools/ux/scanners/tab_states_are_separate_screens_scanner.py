"""tab-states-are-separate-screens - tab siblings use chrome_of / inactive_tabs."""

from __future__ import annotations

from ux_workspace_base import UxWorkspaceScanner


class TabStatesAreSeparateScreensScanner(UxWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_ux_map():
            return
        screens_by_name = {screen.name: screen for screen in workspace.ux_map.screens}
        for screen in workspace.ux_map.screens:
            if " - " not in screen.name and " - " not in screen.name:
                continue
            if not screen.chrome_of:
                yield self.violation(
                    f"tab-state screen {screen.name!r} should set chrome_of to the primary sibling",
                    location=f"screen:{screen.name}",
                )
            elif screen.chrome_of not in screens_by_name:
                yield self.violation(
                    f"screen {screen.name!r} chrome_of {screen.chrome_of!r} is not a known screen",
                    location=f"screen:{screen.name}",
                )
