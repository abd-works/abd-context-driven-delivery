"""Convert UxMap → drawio-ux CLI state (Detailed IA + Site Map)."""

from __future__ import annotations

from typing import Any, Dict, List

from context_tools.ux.ux_model.layouts import resolve_layout
from context_tools.ux.ux_model.nodes import Control, Region, Screen
from context_tools.ux.ux_model.ux_map import UxMap

# Layouts the CLI templates understand (alias → CLI id).
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
    screens: List[Dict[str, Any]] = []
    for index, screen in enumerate(ux_map.screens):
        entry = {
            "name": screen.name,
            "layout": _cli_layout(screen.layout),
            "tabOf": screen.chrome_of or None,
            "col": index,
            "row": 0,
            "regions": [_region_to_cli(region) for region in screen.regions],
            "stories": list(screen.story_names),
            "terms": list(screen.domain_terms or screen.domain_concepts),
        }
        if screen.inactive_tabs:
            # Sibling chrome hint — kept as callout note via terms if needed.
            pass
        screens.append(entry)

    connections = [
        {
            "from": transition.from_screen,
            "to": transition.to_screen,
            "label": transition.trigger or transition.name,
            "dashed": transition.nav_type == "tab",
        }
        for transition in ux_map.transitions
    ]
    return {
        "target": target,
        "screens": screens,
        "connections": connections,
        "scope": ux_map.scope,
    }


def _cli_layout(layout_id: str) -> str:
    key = (layout_id or "").strip().lower()
    if key in _CLI_LAYOUTS:
        return _CLI_LAYOUTS[key]
    template = resolve_layout(key)
    if template and template.id in _CLI_LAYOUTS:
        return _CLI_LAYOUTS[template.id]
    return "stack"


def _region_to_cli(region: Region) -> Dict[str, Any]:
    slot = region.slot or "body"
    controls = list(region.controls)
    if not controls:
        return {"name": region.name, "type": "chrome", "slot": slot, "dimmed": False}

    buttons = [c for c in controls if c.control_type == "button"]
    fields = [c for c in controls if c.control_type in {"text", "dropdown", "checkbox"}]
    rows = [c for c in controls if c.control_type in {"list", "tree"}]

    if fields and not rows:
        return {
            "name": region.name,
            "type": "form",
            "slot": slot,
            "fields": [_field_label(c) for c in fields]
            + ([f"[{c.label}]" for c in buttons] if buttons else []),
        }

    if rows or buttons:
        field_labels = [_field_label(c) for c in rows] or [
            c.label for c in controls if c.control_type not in {"button"}
        ]
        return {
            "name": region.name,
            "type": "list",
            "slot": slot,
            "fields": field_labels or [region.name],
            "actions": [c.label for c in buttons],
        }

    return {
        "name": region.name,
        "type": "chrome",
        "slot": slot,
        "dimmed": False,
    }


def _field_label(control: Control) -> str:
    return control.label or control.name
