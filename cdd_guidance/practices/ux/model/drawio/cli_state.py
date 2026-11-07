"""Convert UxMap -> drawio-ux CLI state (Detailed IA + Site Map)."""

from __future__ import annotations

from typing import Any, Dict

from cdd_guidance.practices.ux.model.nodes import Region, Screen
from cdd_guidance.practices.ux.model.ux_map import UxMap

# Layouts the CLI templates understand (alias -> CLI id).
_CLI_LAYOUTS = {
    "stack": "stack",
    "list": "stack",
    "modal": "modal",
    "modal-dialog": "modal",
    "form": "form",
    "sidebar": "sidebar",
    "split-screen": "split-screen",
    "flyout": "flyout",
    "flyout-panel": "flyout",
    "holy-grail": "holy-grail",
}


def ux_map_to_cli_state(ux_map: UxMap, target: str = "") -> Dict[str, Any]:
    """Build the JSON state shape consumed by drawio_ux.mjs."""
    return {
        "target": target,
        "screens": [_screen_to_cli(screen, index) for index, screen in enumerate(ux_map.screens)],
        "connections": [
            {
                "from": transition.from_screen.name if transition.from_screen else "",
                "to": transition.to_screen.name if transition.to_screen else "",
                "label": transition.trigger or transition.name,
                "dashed": transition.nav_type == "tab",
            }
            for transition in ux_map.transitions
        ],
        "scope": ux_map.scope,
    }


def _screen_to_cli(screen: Screen, column: int) -> Dict[str, Any]:
    return {
        "name": screen.name,
        "layout": _cli_layout(screen.layout),
        "tabOf": screen.chrome_of.name if screen.chrome_of else None,
        "col": column,
        "row": 0,
        "regions": [_region_to_cli(region) for region in screen.regions],
        "stories": list(screen.story_names),
        "terms": list(screen.domain_terms or screen.domain_concepts),
    }


def _cli_layout(layout_id: str) -> str:
    key = (layout_id or "").strip().lower()
    return _CLI_LAYOUTS.get(key, "stack")


def _region_to_cli(region: Region) -> Dict[str, Any]:
    area = region.area or "body"
    controls = list(region.controls)
    if not controls:
        return {"name": region.name, "type": "chrome", "area": area, "dimmed": False}

    buttons = [c for c in controls if c.control_type == "button"]
    fields = [c for c in controls if c.control_type in {"text", "dropdown", "checkbox"}]
    list_controls = [c for c in controls if c.control_type in {"list", "tree"}]

    if fields and not list_controls:
        return {
            "name": region.name,
            "type": "form",
            "area": area,
            "fields": [c.label for c in fields] + [f"[{c.label}]" for c in buttons],
        }

    if list_controls or buttons:
        field_labels = [c.label for c in list_controls] or [
            c.label for c in controls if c.control_type != "button"
        ]
        return {
            "name": region.name,
            "type": "list",
            "area": area,
            "fields": field_labels or [region.name],
            "actions": [c.label for c in buttons],
        }

    return {
        "name": region.name,
        "type": "chrome",
        "area": area,
        "dimmed": False,
    }
