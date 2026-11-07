"""JSON channel - the whole UxMap as one JSON document; every other format can round-trip through it."""

from __future__ import annotations

import json
from typing import Any, Optional

from cdd_guidance.practices.ux.model.nodes import (
    ContentType,
    Control,
    Interaction,
    NavComponent,
    Region,
    Screen,
    StoryDemoControl,
    Transition,
)
from cdd_guidance.practices.ux.model.ux_map import UxMap


class JsonUxMap(UxMap):
    workspace_files = ("ux-map.json", "**/ux-map.json", "ux.json", "**/ux.json")

    def parse(self, content: str | dict) -> UxMap:
        data = json.loads(content) if isinstance(content, str) else content
        ux_map = type(self).create(name=data.get("name", "UxMap"))
        return JsonUxMapReader(ux_map, data).read()

    def render(self, ux_map: UxMap) -> str:
        return json.dumps(JsonUxMapWriter().map_record(ux_map), indent=2) + "\n"


class JsonUxMapReader:
    """Reads one JSON document into a new map. Every screen is on the map before any link to a screen is read, so a
    transition, a tab, or a destination names a screen that is already there."""

    def __init__(self, ux_map: UxMap, data: dict[str, Any]) -> None:
        self.ux_map = ux_map
        self.data = data

    def read(self) -> UxMap:
        with self.ux_map.batch_schema_sync():
            self._read_map_fields()
            screens = self.data.get("screens", [])
            for index, screen_data in enumerate(screens):
                self.ux_map.append_screen(self._screen_shell(screen_data, index))
            for screen, screen_data in zip(self.ux_map.screens, screens):
                self._read_screen(screen, screen_data)
            self._read_components()
        return self.ux_map

    def _read_map_fields(self) -> None:
        self.ux_map.scope = self.data.get("scope", "")
        self.ux_map.story_references = self.data.get("story_references", [])
        self.ux_map.object_references = self.data.get("object_references", [])
        self.ux_map.context.notes = list(self.data.get("notes", []))
        self.ux_map.context.invariants = list(self.data.get("invariants", []))

    def _screen_shell(self, screen_data: dict[str, Any], index: int) -> Screen:
        return Screen(
            screen_data.get("name", f"Screen {index}"),
            index,
            screen_data.get("slug", ""),
            screen_data.get("layout", ""),
            screen_data.get("description", ""),
            graph=self.ux_map.graph,
        )

    def _read_screen(self, screen: Screen, screen_data: dict[str, Any]) -> None:
        screen.chrome_of = self._screen_named(screen_data.get("chrome_of", ""))
        screen.inactive_tabs = list(screen_data.get("inactive_tabs", []))
        for story in screen_data.get("story_names", []):
            screen.show_story(story)
        for scenario in screen_data.get("scenario_names", []):
            screen.show_scenario(scenario)
        for step in screen_data.get("step_names", []):
            screen.show_step(step)
        screen.domain_terms = list(screen_data.get("domain_terms", []))
        screen.domain_concepts = list(screen_data.get("domain_concepts", []))
        screen.image = screen_data.get("image", "")
        screen.prototype = screen_data.get("prototype", "")
        for index, region_data in enumerate(screen_data.get("regions", [])):
            screen.append_region(self._region(region_data, index))

    def _region(self, region_data: dict[str, Any], index: int) -> Region:
        region = Region(region_data.get("name", f"Region {index}"), index, region_data.get("area", ""), self.ux_map.graph)
        for control_index, control_data in enumerate(region_data.get("controls", [])):
            region.append_control(self._control(control_data, control_index))
        return region

    def _control(self, control_data: dict[str, Any], index: int) -> Control:
        name = control_data.get("name", f"Control {index}")
        common = (name, index, control_data.get("control_type", ""), control_data.get("label", ""),
                  control_data.get("bound_field", ""))
        if control_data.get("kind") == "StoryDemoControl" or control_data.get("story_steps"):
            control: Control = StoryDemoControl(
                *common,
                control_data.get("story_steps"),
                control_data.get("set_input", ""),
                control_data.get("item_story_steps"),
                control_data.get("item_value", ""),
                control_data.get("item_label", ""),
                graph=self.ux_map.graph,
            )
        else:
            control = Control(*common, graph=self.ux_map.graph)
        control.states = list(control_data.get("states", []))
        for interaction_index, interaction_data in enumerate(control_data.get("interactions", [])):
            control.append_interaction(self._interaction(interaction_data, interaction_index))
        return control

    def _interaction(self, interaction_data: dict[str, Any], index: int) -> Interaction:
        return Interaction(
            interaction_data.get("name", f"Interaction {index}"),
            index,
            interaction_data.get("trigger", ""),
            interaction_data.get("effect", ""),
            self._screen_named(interaction_data.get("destination", "")),
            self.ux_map.graph,
        )

    def _read_components(self) -> None:
        graph = self.ux_map.graph
        for index, transition_data in enumerate(self.data.get("transitions", [])):
            self.ux_map.transitions.append(Transition(
                transition_data.get("name", f"Transition {index}"),
                index,
                self._screen_named(transition_data.get("from_screen", "")),
                self._screen_named(transition_data.get("to_screen", "")),
                transition_data.get("trigger", ""),
                transition_data.get("nav_type", "action"),
                graph,
            ))
        for index, content_data in enumerate(self.data.get("content_types", [])):
            content_type = ContentType(content_data.get("name", f"ContentType {index}"), index,
                                       content_data.get("hierarchy", ""), graph)
            content_type.key_actions = list(content_data.get("key_actions", []))
            self.ux_map.content_types.append(content_type)
        for index, nav_data in enumerate(self.data.get("nav_components", [])):
            nav = NavComponent(nav_data.get("name", f"Nav {index}"), index, nav_data.get("ux_type", ""), graph)
            nav.destinations = [self.ux_map.find_screen(name) for name in nav_data.get("destinations", [])]
            self.ux_map.nav_components.append(nav)

    def _screen_named(self, name: str) -> Optional[Screen]:
        return self.ux_map.find_screen(name) if name else None


class JsonUxMapWriter:
    """Writes a map as the JSON document JsonUxMapReader reads. A link to a screen is written as that screen's name."""

    def map_record(self, ux_map: UxMap) -> dict[str, Any]:
        return {
            "name": ux_map.name,
            "scope": ux_map.scope,
            "story_references": ux_map.story_references.as_list(),
            "object_references": ux_map.object_references.as_list(),
            "notes": list(ux_map.context.notes),
            "invariants": list(ux_map.context.invariants),
            "screens": [self._screen_record(screen) for screen in ux_map.screens],
            "transitions": [self._transition_record(transition) for transition in ux_map.transitions],
            "content_types": [
                {"name": content_type.name, "hierarchy": content_type.hierarchy,
                 "key_actions": list(content_type.key_actions)}
                for content_type in ux_map.content_types
            ],
            "nav_components": [
                {"name": nav.name, "ux_type": nav.ux_type,
                 "destinations": [screen.name for screen in nav.destinations]}
                for nav in ux_map.nav_components
            ],
        }

    def _screen_record(self, screen: Screen) -> dict[str, Any]:
        return {
            "name": screen.name,
            "slug": screen.slug,
            "layout": screen.layout,
            "description": screen.description,
            "chrome_of": _name_of(screen.chrome_of),
            "inactive_tabs": list(screen.inactive_tabs),
            "story_names": screen.story_keys,
            "scenario_names": screen.scenario_keys,
            "step_names": screen.step_keys,
            "domain_terms": list(screen.domain_terms),
            "domain_concepts": list(screen.domain_concepts),
            "image": screen.image,
            "prototype": screen.prototype,
            "regions": [
                {"name": region.name, "area": region.area,
                 "controls": [self._control_record(control) for control in region.controls]}
                for region in screen.regions
            ],
        }

    def _control_record(self, control: Control) -> dict[str, Any]:
        record: dict[str, Any] = {
            "name": control.name,
            "control_type": control.control_type,
            "label": control.label,
            "bound_field": control.bound_field,
            "states": list(control.states),
            "interactions": [
                {"name": interaction.name, "trigger": interaction.trigger, "effect": interaction.effect,
                 "destination": _name_of(interaction.destination)}
                for interaction in control.interactions
            ],
        }
        if isinstance(control, StoryDemoControl):
            record.update(self._story_demo_record(control))
        return record

    def _story_demo_record(self, control: StoryDemoControl) -> dict[str, Any]:
        record: dict[str, Any] = {
            "kind": "StoryDemoControl",
            "story_steps": [step.as_dict() for step in control.story_steps],
            "set_input": control.set_input,
            "item_story_steps": [step.as_dict() for step in control.item_story_steps],
            "item_value": control.item_value,
            "item_label": control.item_label,
        }
        return {key: value for key, value in record.items() if value or key in ("kind", "story_steps")}

    def _transition_record(self, transition: Transition) -> dict[str, Any]:
        return {
            "name": transition.name,
            "from_screen": _name_of(transition.from_screen),
            "to_screen": _name_of(transition.to_screen),
            "trigger": transition.trigger,
            "nav_type": transition.nav_type,
        }


def _name_of(screen: Optional[Screen]) -> str:
    return screen.name if screen is not None else ""
