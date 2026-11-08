"""JSON channel - the whole UxMap as one JSON document; every other format can round-trip through it.

Each JSON node writes its own record (`as_record`) and reads one back (`from_record`), so the map reads a document by
asking each of its parts to read its own record. Every screen is on the map before any link to a screen is read, so a
transition, a tab, or a destination names a screen that is already there."""

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

# The kind a Story Demo control's record names, so it reads back as one.
_STORY_DEMO = "StoryDemoControl"


class JsonControl(Control):
    """A control as the JSON document writes it: its fields, its states, and each interaction, a link to a screen
    written as that screen's name."""

    @classmethod
    def from_record(cls, record: dict[str, Any], index: int, ux_map: "JsonUxMap") -> Control:
        """The control a record writes, on ux_map's graph: a Story Demo control when the record says it is one."""
        common = (record.get("name", f"Control {index}"), index, record.get("control_type", ""),
                  record.get("label", ""), record.get("bound_field", ""))
        if record.get("kind") == _STORY_DEMO or record.get("story_steps"):
            control = ux_map.story_demo_control_type.demo_from_record(common, record, ux_map)
        else:
            control = cls(*common, graph=ux_map.graph)
        control.read_states_and_interactions(record, ux_map)
        return control

    def read_states_and_interactions(self, record: dict[str, Any], ux_map: "JsonUxMap") -> None:
        """The states the record lists, and each interaction it writes, its destination the screen it names."""
        self.states = list(record.get("states", []))
        for index, interaction in enumerate(record.get("interactions", [])):
            self.append_interaction(Interaction(
                interaction.get("name", f"Interaction {index}"),
                index,
                interaction.get("trigger", ""),
                interaction.get("effect", ""),
                ux_map.screen_named(interaction.get("destination", "")),
                ux_map.graph,
            ))

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

    @classmethod
    def demo_from_record(cls, common: tuple, record: dict[str, Any], ux_map: "JsonUxMap") -> "JsonStoryDemoControl":
        """The Story Demo control a record writes, with a control's common fields."""
        return cls(
            *common,
            record.get("story_steps"),
            record.get("set_input", ""),
            record.get("item_story_steps"),
            record.get("item_value", ""),
            record.get("item_label", ""),
            graph=ux_map.graph,
        )

    def as_record(self) -> dict[str, Any]:
        demo: dict[str, Any] = {
            "kind": _STORY_DEMO,
            "story_steps": [step.as_dict() for step in self.story_steps],
            "set_input": self.set_input,
            "item_story_steps": [step.as_dict() for step in self.item_story_steps],
            "item_value": self.item_value,
            "item_label": self.item_label,
        }
        return {**super().as_record(), **{key: value for key, value in demo.items() if value or key in ("kind", "story_steps")}}


class JsonRegion(Region):
    """A region as the JSON document writes it: its name, its area, and each control's record."""

    @classmethod
    def from_record(cls, record: dict[str, Any], index: int, ux_map: "JsonUxMap") -> "JsonRegion":
        region = cls(record.get("name", f"Region {index}"), index, record.get("area", ""), ux_map.graph)
        for control_index, control in enumerate(record.get("controls", [])):
            region.append_control(ux_map.control_type.from_record(control, control_index, ux_map))
        return region

    def as_record(self) -> dict[str, Any]:
        return {"name": self.name, "area": self.area, "controls": [control.as_record() for control in self.controls]}


class JsonScreen(Screen):
    """A screen as the JSON document writes it: its fields, what it shows, and each region's record."""

    @classmethod
    def from_record(cls, record: dict[str, Any], index: int, ux_map: "JsonUxMap") -> "JsonScreen":
        """The screen a record writes, before any link to another screen is read."""
        return cls(
            record.get("name", f"Screen {index}"),
            index,
            record.get("slug", ""),
            record.get("layout", ""),
            record.get("description", ""),
            graph=ux_map.graph,
        )

    def read_record(self, record: dict[str, Any], ux_map: "JsonUxMap") -> None:
        """The rest of the screen's record, once every screen is on the map: the screen it is the chrome of, what it
        shows, and its regions."""
        self.chrome_of = ux_map.screen_named(record.get("chrome_of", ""))
        self.inactive_tabs = list(record.get("inactive_tabs", []))
        for story in record.get("story_names", []):
            self.show_story(story)
        for scenario in record.get("scenario_names", []):
            self.show_scenario(scenario)
        for step in record.get("step_names", []):
            self.show_step(step)
        self.domain_terms = list(record.get("domain_terms", []))
        self.domain_concepts = list(record.get("domain_concepts", []))
        self.image = record.get("image", "")
        self.prototype = record.get("prototype", "")
        for index, region in enumerate(record.get("regions", [])):
            self.append_region(ux_map.region_type.from_record(region, index, ux_map))

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

    @classmethod
    def from_record(cls, record: dict[str, Any], index: int, ux_map: "JsonUxMap") -> "JsonTransition":
        return cls(
            record.get("name", f"Transition {index}"),
            index,
            ux_map.screen_named(record.get("from_screen", "")),
            ux_map.screen_named(record.get("to_screen", "")),
            record.get("trigger", ""),
            record.get("nav_type", "action"),
            ux_map.graph,
        )

    def as_record(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "from_screen": _name_of(self.from_screen),
            "to_screen": _name_of(self.to_screen),
            "trigger": self.trigger,
            "nav_type": self.nav_type,
        }


class JsonContentType(ContentType):
    """A content type as the JSON document writes it: its name, its hierarchy, and its key actions."""

    @classmethod
    def from_record(cls, record: dict[str, Any], index: int, ux_map: "JsonUxMap") -> "JsonContentType":
        content_type = cls(record.get("name", f"ContentType {index}"), index, record.get("hierarchy", ""), ux_map.graph)
        content_type.key_actions = list(record.get("key_actions", []))
        return content_type

    def as_record(self) -> dict[str, Any]:
        return {"name": self.name, "hierarchy": self.hierarchy, "key_actions": list(self.key_actions)}


class JsonNavComponent(NavComponent):
    """A navigation component as the JSON document writes it, each destination written as that screen's name."""

    @classmethod
    def from_record(cls, record: dict[str, Any], index: int, ux_map: "JsonUxMap") -> "JsonNavComponent":
        nav = cls(record.get("name", f"Nav {index}"), index, record.get("ux_type", ""), ux_map.graph)
        nav.destinations = [ux_map.find_screen(name) for name in record.get("destinations", [])]
        return nav

    def as_record(self) -> dict[str, Any]:
        return {"name": self.name, "ux_type": self.ux_type, "destinations": [screen.name for screen in self.destinations]}


class JsonUxMap(UxMap):
    workspace_files = ("ux-map.json", "**/ux-map.json", "ux.json", "**/ux.json")
    screen_type = JsonScreen
    region_type = JsonRegion
    control_type = JsonControl
    story_demo_control_type = JsonStoryDemoControl
    transition_type = JsonTransition
    content_type_type = JsonContentType
    nav_component_type = JsonNavComponent

    def parse(self, content: str | dict) -> UxMap:
        """A new map of this format read from a JSON document: its own fields, then each screen, each transition,
        content type, and navigation component reading its own record."""
        data = json.loads(content) if isinstance(content, str) else content
        ux_map = type(self).create(name=data.get("name", "UxMap"))
        ux_map.read_record(data)
        return ux_map

    def read_record(self, data: dict[str, Any]) -> None:
        with self.batch_schema_sync():
            self.scope = data.get("scope", "")
            self.story_references = data.get("story_references", [])
            self.object_references = data.get("object_references", [])
            self.context.notes = list(data.get("notes", []))
            self.context.invariants = list(data.get("invariants", []))
            screens = data.get("screens", [])
            for index, record in enumerate(screens):
                self.append_screen(self.screen_type.from_record(record, index, self))
            for screen, record in zip(self.screens, screens):
                screen.read_record(record, self)
            for index, record in enumerate(data.get("transitions", [])):
                self.transitions.append(self.transition_type.from_record(record, index, self))
            for index, record in enumerate(data.get("content_types", [])):
                self.content_types.append(self.content_type_type.from_record(record, index, self))
            for index, record in enumerate(data.get("nav_components", [])):
                self.nav_components.append(self.nav_component_type.from_record(record, index, self))

    def screen_named(self, name: str) -> Optional[Screen]:
        """The screen a record names, or none for a record that names none."""
        return self.find_screen(name) if name else None

    def render(self, canonical: UxMap) -> str:
        """canonical in this format: copied into a map of this format, which writes itself."""
        return type(self).copy_of(canonical).save()

    def save(self) -> str:
        return json.dumps(self.map_record(), indent=2) + "\n"

    def map_record(self) -> dict[str, Any]:
        """This map as the JSON document it reads back: each screen, transition, content type, and navigation
        component writes its own record."""
        return {
            "name": self.name,
            "scope": self.scope,
            "story_references": self.story_references.as_list(),
            "object_references": self.object_references.as_list(),
            "notes": list(self.context.notes),
            "invariants": list(self.context.invariants),
            "screens": [screen.as_record() for screen in self.screens],
            "transitions": [transition.as_record() for transition in self.transitions],
            "content_types": [content_type.as_record() for content_type in self.content_types],
            "nav_components": [nav.as_record() for nav in self.nav_components],
        }


def _name_of(screen: Optional[Screen]) -> str:
    return screen.name if screen is not None else ""
