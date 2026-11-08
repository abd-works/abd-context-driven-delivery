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


class JsonControl(Control):
    """A control as the JSON document writes it: its fields, its states, and each interaction, a link to a screen
    written as that screen's name."""

    def as_record(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "control_type": self.control_type,
            "label": self.label,
            "bound_field": self.bound_field,
            "states": list(self.states),
            "interactions": [
                {"name": interaction.name, "trigger": interaction.trigger, "effect": interaction.effect,
                 "destination": _name_of(interaction.destination)}
                for interaction in self.interactions
            ],
        }


class JsonStoryDemoControl(StoryDemoControl, JsonControl):
    """A Story Demo control as the JSON document writes it: a control's record, marked with its kind, with the steps
    it runs and the input it fills."""

    def as_record(self) -> dict[str, Any]:
        demo: dict[str, Any] = {
            "kind": "StoryDemoControl",
            "story_steps": [step.as_dict() for step in self.story_steps],
            "set_input": self.set_input,
            "item_story_steps": [step.as_dict() for step in self.item_story_steps],
            "item_value": self.item_value,
            "item_label": self.item_label,
        }
        return {**super().as_record(), **{key: value for key, value in demo.items() if value or key in ("kind", "story_steps")}}


class JsonRegion(Region):
    """A region as the JSON document writes it: its name, its area, and each control's record."""

    def as_record(self) -> dict[str, Any]:
        return {"name": self.name, "area": self.area, "controls": [control.as_record() for control in self.controls]}


class JsonScreen(Screen):
    """A screen as the JSON document writes it: its fields, what it shows, and each region's record."""

    def as_record(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "slug": self.slug,
            "layout": self.layout,
            "description": self.description,
            "chrome_of": _name_of(self.chrome_of),
            "inactive_tabs": list(self.inactive_tabs),
            "story_names": self.story_keys,
            "scenario_names": self.scenario_keys,
            "step_names": self.step_keys,
            "domain_terms": list(self.domain_terms),
            "domain_concepts": list(self.domain_concepts),
            "image": self.image,
            "prototype": self.prototype,
            "regions": [region.as_record() for region in self.regions],
        }


class JsonTransition(Transition):
    """A transition as the JSON document writes it, each screen it joins written as that screen's name."""

    def as_record(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "from_screen": _name_of(self.from_screen),
            "to_screen": _name_of(self.to_screen),
            "trigger": self.trigger,
            "nav_type": self.nav_type,
        }


class JsonUxMap(UxMap):
    workspace_files = ("ux-map.json", "**/ux-map.json", "ux.json", "**/ux.json")
    screen_type = JsonScreen
    region_type = JsonRegion
    control_type = JsonControl
    story_demo_control_type = JsonStoryDemoControl
    transition_type = JsonTransition

    def parse(self, content: str | dict) -> UxMap:
        data = json.loads(content) if isinstance(content, str) else content
        ux_map = type(self).create(name=data.get("name", "UxMap"))
        return JsonUxMapReader(ux_map, data).read()

    def render(self, canonical: UxMap) -> str:
        """canonical in this format: copied into a map of this format, which writes itself."""
        return type(self).copy_of(canonical).save()

    def save(self) -> str:
        return json.dumps(self.map_record(), indent=2) + "\n"

    def map_record(self) -> dict[str, Any]:
        """This map as the JSON document JsonUxMapReader reads: each screen and transition writes its own record."""
        return {
            "name": self.name,
            "scope": self.scope,
            "story_references": self.story_references.as_list(),
            "object_references": self.object_references.as_list(),
            "notes": list(self.context.notes),
            "invariants": list(self.context.invariants),
            "screens": [screen.as_record() for screen in self.screens],
            "transitions": [transition.as_record() for transition in self.transitions],
            "content_types": [
                {"name": content_type.name, "hierarchy": content_type.hierarchy,
                 "key_actions": list(content_type.key_actions)}
                for content_type in self.content_types
            ],
            "nav_components": [
                {"name": nav.name, "ux_type": nav.ux_type,
                 "destinations": [screen.name for screen in nav.destinations]}
                for nav in self.nav_components
            ],
        }


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
        return self.ux_map.screen_type(
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
        region = self.ux_map.region_type(region_data.get("name", f"Region {index}"), index, region_data.get("area", ""), self.ux_map.graph)
        for control_index, control_data in enumerate(region_data.get("controls", [])):
            region.append_control(self._control(control_data, control_index))
        return region

    def _control(self, control_data: dict[str, Any], index: int) -> Control:
        name = control_data.get("name", f"Control {index}")
        common = (name, index, control_data.get("control_type", ""), control_data.get("label", ""),
                  control_data.get("bound_field", ""))
        if control_data.get("kind") == "StoryDemoControl" or control_data.get("story_steps"):
            control: Control = self.ux_map.story_demo_control_type(
                *common,
                control_data.get("story_steps"),
                control_data.get("set_input", ""),
                control_data.get("item_story_steps"),
                control_data.get("item_value", ""),
                control_data.get("item_label", ""),
                graph=self.ux_map.graph,
            )
        else:
            control = self.ux_map.control_type(*common, graph=self.ux_map.graph)
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
            self.ux_map.transitions.append(self.ux_map.transition_type(
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


def _name_of(screen: Optional[Screen]) -> str:
    return screen.name if screen is not None else ""
