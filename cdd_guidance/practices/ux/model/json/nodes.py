"""JSON channel - the whole UxMap as one JSON document; every other format can round-trip through it.

Each JSON node writes its own record (`as_record`) and reads one back (`from_record`), so the map reads a document by
asking each of its parts to read its own record. Every screen is on the map before any link to a screen is read, so a
transition, a tab, or a destination names a screen that is already there."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from cdd_guidance.practices.ux.model.nodes import (
    ContentType,
    Control,
    Interaction,
    NavComponent,
    Region,
    Screen,
    ServesStories,
    StoryDemoControl,
    StoryStep,
    Transition,
)
from cdd_guidance.practices.ux.model.ux_map import UxMap
from harness.guidance.practice_formats import Written

# The names a UX map's JSON file goes by.
_MAP_FILE_NAMES = ("ux-map.json", "ux.json")
# The kind a Story Demo control's record names, so it reads back as one.
_STORY_DEMO = "StoryDemoControl"


class JsonServesStories(ServesStories):
    """What a screen or a control serves as the JSON document writes it: the stories, scenarios, and steps, each a
    list of names or of markdown links."""

    def read_served(self, record: dict[str, Any]) -> None:
        for story in record.get("story_names", []):
            self.show_story(story)
        for scenario in record.get("scenario_names", []):
            self.show_scenario(scenario)
        for step in record.get("step_names", []):
            self.show_step(step)

    def served_record(self) -> dict[str, Any]:
        return {"story_names": self.story_keys, "scenario_names": self.scenario_keys, "step_names": self.step_keys}


class JsonControl(Control, JsonServesStories):
    """A control as the JSON document writes it: its fields, its states, and each interaction, a link to a screen
    written as that screen's name."""

    @classmethod
    def from_record(cls, record: dict[str, Any], index: int, ux_map: "JsonUxMap") -> Control:
        """The control a record writes: a Story Demo control when the record says it is one."""
        demo = record.get("kind") == _STORY_DEMO or record.get("story_steps")
        control = (ux_map.story_demo_control_type if demo else cls)(record.get("name", f"Control {index}"), index)
        control.control_type, control.label = record.get("control_type", ""), record.get("label", "")
        control.bound_field = record.get("bound_field", "")
        control.read_served(record)
        if demo:
            control.read_story_fields(record)
        control.read_states_and_interactions(record, ux_map)
        return control

    def read_states_and_interactions(self, record: dict[str, Any], ux_map: "JsonUxMap") -> None:
        """The states the record lists, and each interaction it writes, its destination the screen it names."""
        self.states = list(record.get("states", []))
        for index, written in enumerate(record.get("interactions", [])):
            interaction = Interaction(written.get("name", f"Interaction {index}"), index)
            interaction.trigger, interaction.effect = written.get("trigger", ""), written.get("effect", "")
            interaction.destination = ux_map.screen_named(written.get("destination", ""))
            self.append_interaction(interaction)

    def as_record(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "control_type": self.control_type,
            "label": self.label,
            "bound_field": self.bound_field,
            "states": list(self.states),
            **self.served_record(),
            "interactions": [
                {"name": interaction.name, "trigger": interaction.trigger, "effect": interaction.effect,
                 "destination": interaction.destination_name}
                for interaction in self.interactions
            ],
        }


class JsonStoryDemoControl(StoryDemoControl, JsonControl):
    """A Story Demo control as the JSON document writes it: a control's record, marked with its kind, with the steps
    it runs and the input it fills."""

    def read_story_fields(self, record: dict[str, Any]) -> None:
        """The steps the record says this control runs, the input it fills, and how it shows its items."""
        self.story_steps = StoryStep.from_values(record.get("story_steps"))
        self.set_input = record.get("set_input", "") or ""
        self.item_story_steps = StoryStep.from_values(record.get("item_story_steps"))
        self.item_value = record.get("item_value", "") or ""
        self.item_label = record.get("item_label", "") or ""

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
        region = cls(record.get("name", f"Region {index}"), index)
        region.area = record.get("area", "")
        for control_index, control in enumerate(record.get("controls", [])):
            region.append_control(ux_map.control_type.from_record(control, control_index, ux_map))
        return region

    def as_record(self) -> dict[str, Any]:
        return {"name": self.name, "area": self.area, "controls": [control.as_record() for control in self.controls]}


class JsonScreen(Screen, JsonServesStories):
    """A screen as the JSON document writes it: its fields, what it shows, and each region's record."""

    @classmethod
    def from_record(cls, record: dict[str, Any], index: int, ux_map: "JsonUxMap") -> "JsonScreen":
        """The screen a record writes, before any link to another screen is read."""
        screen = cls(record.get("name", f"Screen {index}"), index)
        screen.slug, screen.layout = record.get("slug", ""), record.get("layout", "")
        screen.description = record.get("description", "")
        return screen

    def read_record(self, record: dict[str, Any], ux_map: "JsonUxMap") -> None:
        """The rest of the screen's record, once every screen is on the map: the screen it is the chrome of, what it
        shows, and its regions."""
        self.chrome_of = ux_map.screen_named(record.get("chrome_of", ""))
        self.inactive_tabs = list(record.get("inactive_tabs", []))
        self.read_served(record)
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
            "chrome_of": self.chrome_of_name,
            "inactive_tabs": list(self.inactive_tabs),
            **self.served_record(),
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
        transition = cls(record.get("name", f"Transition {index}"), index)
        transition.trigger, transition.nav_type = record.get("trigger", ""), record.get("nav_type", "action")
        return transition.joining(ux_map.screen_named(record.get("from_screen", "")), ux_map.screen_named(record.get("to_screen", "")))

    def as_record(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "from_screen": self.from_name,
            "to_screen": self.to_name,
            "trigger": self.trigger,
            "nav_type": self.nav_type,
        }


class JsonContentType(ContentType):
    """A content type as the JSON document writes it: its name, its hierarchy, and its key actions."""

    @classmethod
    def from_record(cls, record: dict[str, Any], index: int) -> "JsonContentType":
        content_type = cls(record.get("name", f"ContentType {index}"), index)
        content_type.hierarchy = record.get("hierarchy", "")
        content_type.key_actions = list(record.get("key_actions", []))
        return content_type

    def as_record(self) -> dict[str, Any]:
        return {"name": self.name, "hierarchy": self.hierarchy, "key_actions": list(self.key_actions)}


class JsonNavComponent(NavComponent):
    """A navigation component as the JSON document writes it, each destination written as that screen's name."""

    @classmethod
    def from_record(cls, record: dict[str, Any], index: int, ux_map: "JsonUxMap") -> "JsonNavComponent":
        nav = cls(record.get("name", f"Nav {index}"), index)
        nav.ux_type = record.get("ux_type", "")
        nav.destinations = [ux_map.find_screen(name) for name in record.get("destinations", [])]
        return nav

    def as_record(self) -> dict[str, Any]:
        return {"name": self.name, "ux_type": self.ux_type, "destinations": [screen.name for screen in self.destinations]}


class JsonUxMap(UxMap):
    map_file_suffixes = (".json",)
    not_a_map_failures = (json.JSONDecodeError,)

    def reads_file(self, file: Path, text: str) -> bool:
        """A JSON file named as a UX map is, ``ux-map.json`` or ``ux.json``; any other JSON file is something else."""
        return file.name in _MAP_FILE_NAMES
    screen_type = JsonScreen
    region_type = JsonRegion
    control_type = JsonControl
    story_demo_control_type = JsonStoryDemoControl
    transition_type = JsonTransition
    content_type_type = JsonContentType
    nav_component_type = JsonNavComponent

    def parse(self, text: str | dict, file: str = "") -> UxMap:
        """A new map of this format read from a JSON document: its own fields, then each screen, each transition,
        content type, and navigation component reading its own record."""
        document = self._document_of(text)
        ux_map = type(self).create(name=document.get("name", "UxMap"))
        ux_map._read_record(document)
        return ux_map

    def _document_of(self, content: str | dict[str, Any]) -> dict[str, Any]:
        """The JSON document content holds: decoded from text, or the document itself."""
        return json.loads(content) if isinstance(content, str) else content

    def _read_record(self, document: dict[str, Any]) -> None:
        with self.batch_schema_sync():
            self.scope = document.get("scope", "")
            self.story_references = document.get("story_references", [])
            self.object_references = document.get("object_references", [])
            self.context.notes = list(document.get("notes", []))
            self.context.invariants = list(document.get("invariants", []))
            screens = document.get("screens", [])
            for index, record in enumerate(screens):
                self.append_screen(self.screen_type.from_record(record, index, self))
            for screen, record in zip(self.screens, screens):
                screen.read_record(record, self)
            for index, record in enumerate(document.get("transitions", [])):
                self.transitions.append(self.transition_type.from_record(record, index, self))
            for index, record in enumerate(document.get("content_types", [])):
                self.content_types.append(self.content_type_type.from_record(record, index))
            for index, record in enumerate(document.get("nav_components", [])):
                self.nav_components.append(self.nav_component_type.from_record(record, index, self))

    def screen_named(self, name: str) -> Optional[Screen]:
        """The screen a record names, or none for a record that names none."""
        return self.find_screen(name) if name else None

    def render(self, canonical: UxMap, written: Written = Written()) -> str:

        """canonical in this format: copied into a map of this format, which writes itself."""
        return self.copy_of(canonical).save()

    def save(self) -> str:
        return json.dumps(self._map_record(), indent=2) + "\n"

    def _map_record(self) -> dict[str, Any]:
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
