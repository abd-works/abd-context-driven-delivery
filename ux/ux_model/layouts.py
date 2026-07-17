"""Thin layout catalog — layout id → named region slots.

Extracted from abd-skills IA screen-templates (vocabulary + slots only).
Not a paste library of ASCII/drawio fragments.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class LayoutTemplate:
    """One conventional screen layout and the slots it names."""

    id: str
    slots: Tuple[str, ...]
    category: str = ""
    aliases: Tuple[str, ...] = ()


# Core IA layouts — CLI layouts first, then high-value navigation/structure patterns.
LAYOUTS: Tuple[LayoutTemplate, ...] = (
    LayoutTemplate("sidebar", ("panel", "body"), "Navigation"),
    LayoutTemplate("form", ("body",), "Utility"),
    LayoutTemplate("modal", ("body",), "Utility", ("modal-dialog",)),
    LayoutTemplate("holy-grail", ("header", "nav", "body", "aside", "footer"), "Structure"),
    LayoutTemplate("split-screen", ("left", "right"), "Structure"),
    LayoutTemplate("flyout", ("body", "panel"), "Utility", ("flyout-panel",)),
    LayoutTemplate("stack", ("rows",), "Content", ("list",)),
    LayoutTemplate("tabbed", ("tab-bar", "body"), "Navigation"),
    LayoutTemplate("wizard-stepper", ("step-bar", "body", "back", "continue"), "Utility"),
    LayoutTemplate("rail-navigation", ("rail", "body"), "Navigation", ("rail",)),
    LayoutTemplate("top-header", ("logo", "nav-links", "profile", "body"), "Navigation"),
    LayoutTemplate("dashboard", ("header", "nav", "main"), "Structure"),
    LayoutTemplate("search-filter", ("search-bar", "filters", "results"), "Utility"),
    LayoutTemplate("accordion", ("section-headers", "expanded-content"), "Content"),
)


def _index() -> Dict[str, LayoutTemplate]:
    by_id: Dict[str, LayoutTemplate] = {}
    for layout in LAYOUTS:
        by_id[layout.id] = layout
        for alias in layout.aliases:
            if alias:
                by_id[alias] = layout
    return by_id


_BY_ID = _index()


def resolve_layout(layout_id: str) -> LayoutTemplate | None:
    """Return the template for *layout_id* (or alias), or None if unknown."""
    key = (layout_id or "").strip().lower()
    if not key:
        return None
    return _BY_ID.get(key)


def layout_slots(layout_id: str) -> List[str]:
    """Named slots for *layout_id*; empty list if unknown."""
    template = resolve_layout(layout_id)
    return list(template.slots) if template else []


def known_layout_ids() -> List[str]:
    """Canonical layout ids (aliases omitted)."""
    return [layout.id for layout in LAYOUTS]
