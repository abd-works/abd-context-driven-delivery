"""JSON channel - round-trip UxMap fields for transform and scanners."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from context_tools.ux.ux_model.nodes import (
    ContentType,
    Control,
    Interaction,
    NavComponent,
    Region,
    Screen,
    StoryDemoControl,
    Transition,
)
from context_tools.ux.ux_model.ux_map import UxMap


def _control_from_dict(control_data: dict[str, Any], index: int) -> Control:
    story_steps = control_data.get("story_steps") or []
    is_story_demo = (
        control_data.get("kind") == "StoryDemoControl"
        or bool(story_steps)
    )
    if is_story_demo:
        control: Control = StoryDemoControl(
            control_data.get("name", f"Control {index}"),
            index,
            control_data.get("control_type", ""),
            control_data.get("label", ""),
            control_data.get("bound_field", ""),
            story_steps,
            control_data.get("set_input", ""),
            control_data.get("item_story_steps") or [],
            control_data.get("item_value", ""),
            control_data.get("item_label", ""),
        )
    else:
        control = Control(
            control_data.get("name", f"Control {index}"),
            index,
            control_data.get("control_type", ""),
            control_data.get("label", ""),
            control_data.get("bound_field", ""),
        )
    control.states = list(control_data.get("states", []))
    return control


def _control_to_dict(control: Control) -> dict[str, Any]:
    data: dict[str, Any] = {
        "name": control.name,
        "control_type": control.control_type,
        "label": control.label,
        "bound_field": control.bound_field,
        "states": list(control.states),
        "interactions": [
            {
                "name": interaction.name,
                "trigger": interaction.trigger,
                "effect": interaction.effect,
                "destination_screen": interaction.destination_screen,
            }
            for interaction in control.interactions
        ],
    }
    if isinstance(control, StoryDemoControl):
        data["kind"] = "StoryDemoControl"
        data["story_steps"] = [
            {"kind": s.get("kind", ""), "label": s.get("label", "")}
            for s in control.story_steps
        ]
        if control.set_input:
            data["set_input"] = control.set_input
        if control.item_story_steps:
            data["item_story_steps"] = [
                {"kind": s.get("kind", ""), "label": s.get("label", "")}
                for s in control.item_story_steps
            ]
        if control.item_value:
            data["item_value"] = control.item_value
        if control.item_label:
            data["item_label"] = control.item_label
    return data


class JsonUxMap(UxMap):
    @classmethod
    def parse(cls, content: str) -> UxMap:
        data = json.loads(content) if isinstance(content, str) else content
        return cls._from_dict(data)

    @classmethod
    def render(cls, ux_map: UxMap) -> str:
        return json.dumps(cls._to_dict(ux_map), indent=2) + "\n"

    @classmethod
    def from_workspace(cls, root: Path) -> Optional[UxMap]:
        for name in ("ux-map.json", "ux.json"):
            candidate = root / name
            if candidate.is_file():
                return cls.parse(candidate.read_text(encoding="utf-8"))
            for found in root.rglob(name):
                return cls.parse(found.read_text(encoding="utf-8"))
        return None

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> UxMap:
        ux_map = cls(name=data.get("name", "UxMap"))
        ux_map.scope = data.get("scope", "")
        ux_map.story_references = list(
            data.get("story_references")
            or data.get("story_modules")
            or data.get("story_module_paths")
            or []
        )
        ux_map.object_references = list(
            data.get("object_references")
            or data.get("domain_modules")
            or data.get("domain_module_paths")
            or []
        )
        ux_map.context.notes = list(data.get("notes", []))
        ux_map.context.invariants = list(data.get("invariants", []))

        for index, screen_data in enumerate(data.get("screens", [])):
            screen = Screen(
                screen_data.get("name", f"Screen {index}"),
                index,
                screen_data.get("slug", ""),
                screen_data.get("layout", ""),
                screen_data.get("description", ""),
                screen_data.get("chrome_of", ""),
            )
            screen.inactive_tabs = list(screen_data.get("inactive_tabs", []))
            screen.story_names = list(screen_data.get("story_names", []))
            screen.domain_terms = list(screen_data.get("domain_terms", []))
            screen.domain_concepts = list(screen_data.get("domain_concepts", []))
            for r_index, region_data in enumerate(screen_data.get("regions", [])):
                region = Region(
                    region_data.get("name", f"Region {r_index}"),
                    r_index,
                    region_data.get("slot", ""),
                )
                for c_index, control_data in enumerate(region_data.get("controls", [])):
                    control = _control_from_dict(control_data, c_index)
                    for i_index, interaction_data in enumerate(
                        control_data.get("interactions", [])
                    ):
                        control.append_interaction(
                            Interaction(
                                interaction_data.get("name", f"Interaction {i_index}"),
                                i_index,
                                interaction_data.get("trigger", ""),
                                interaction_data.get("effect", ""),
                                interaction_data.get("destination_screen", ""),
                            )
                        )
                    region.append_control(control)
                screen.append_region(region)
            ux_map.append_screen(screen)

        for index, transition_data in enumerate(data.get("transitions", [])):
            ux_map.transitions.append(
                Transition(
                    transition_data.get("name", f"Transition {index}"),
                    index,
                    transition_data.get("from_screen", ""),
                    transition_data.get("to_screen", ""),
                    transition_data.get("trigger", ""),
                    transition_data.get("nav_type", "action"),
                )
            )

        for index, content_data in enumerate(data.get("content_types", [])):
            content_type = ContentType(
                content_data.get("name", f"ContentType {index}"),
                index,
                content_data.get("hierarchy", ""),
            )
            content_type.key_actions = list(content_data.get("key_actions", []))
            ux_map.content_types.append(content_type)

        for index, nav_data in enumerate(data.get("nav_components", [])):
            nav = NavComponent(
                nav_data.get("name", f"Nav {index}"),
                index,
                nav_data.get("ux_type", ""),
            )
            nav.destinations = list(nav_data.get("destinations", []))
            ux_map.nav_components.append(nav)

        return ux_map

    @classmethod
    def _to_dict(cls, ux_map: UxMap) -> dict[str, Any]:
        return {
            "name": ux_map.name,
            "scope": ux_map.scope,
            "story_references": ux_map.story_references.as_list(),
            "object_references": ux_map.object_references.as_list(),
            "notes": list(ux_map.context.notes),
            "invariants": list(ux_map.context.invariants),
            "screens": [
                {
                    "name": screen.name,
                    "slug": screen.slug,
                    "layout": screen.layout,
                    "description": screen.description,
                    "chrome_of": screen.chrome_of,
                    "inactive_tabs": list(screen.inactive_tabs),
                    "story_names": list(screen.story_names),
                    "domain_terms": list(screen.domain_terms),
                    "domain_concepts": list(screen.domain_concepts),
                    "regions": [
                        {
                            "name": region.name,
                            "slot": region.slot,
                            "controls": [
                                _control_to_dict(control)
                                for control in region.controls
                            ],
                        }
                        for region in screen.regions
                    ],
                }
                for screen in ux_map.screens
            ],
            "transitions": [
                {
                    "name": transition.name,
                    "from_screen": transition.from_screen,
                    "to_screen": transition.to_screen,
                    "trigger": transition.trigger,
                    "nav_type": transition.nav_type,
                }
                for transition in ux_map.transitions
            ],
            "content_types": [
                {
                    "name": content_type.name,
                    "hierarchy": content_type.hierarchy,
                    "key_actions": list(content_type.key_actions),
                }
                for content_type in ux_map.content_types
            ],
            "nav_components": [
                {
                    "name": nav.name,
                    "ux_type": nav.ux_type,
                    "destinations": list(nav.destinations),
                }
                for nav in ux_map.nav_components
            ],
        }
