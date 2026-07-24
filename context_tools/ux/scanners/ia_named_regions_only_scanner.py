"""ia-named-regions-only — IA surfaces list named regions; control-like labels fail."""

from __future__ import annotations

import re

from ux_workspace_base import UxWorkspaceScanner

_CONTROL_HINT = re.compile(
    r"\b(button|input|checkbox|dropdown|textbox|text field|select|toggle)\b",
    re.I,
)


class IaNamedRegionsOnlyScanner(UxWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_ux_map():
            return
        # When any control exists on the map, treat as mockup+ and skip IA-only rule.
        has_controls = any(
            control
            for screen in workspace.ux_map.screens
            for region in screen.regions
            for control in region.controls
        )
        if has_controls:
            return
        for screen in workspace.ux_map.screens:
            for region in screen.regions:
                if _CONTROL_HINT.search(region.name):
                    yield self.violation(
                        f"region {region.name!r} on {screen.name!r} looks like a control — "
                        "IA lists named regions only",
                        location=f"screen:{screen.name}/region:{region.name}",
                    )
