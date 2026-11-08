"""UxMap - root container for screens and UxComponent collections."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

from harness.graph.model_node import ModelChildren
from harness.graph.graph import Graph

from .collections import ContentTypes, NavComponents, Transitions
from .nodes import ContentType, Control, Interaction, NavComponent, Region, Screen, StoryDemoControl, Transition, UxContext
from .reference_paths import ReferencePaths
from .ux_node import UxNode


def _top_epic(story):
    epic = None
    current = story.parent
    while current is not None and current.semantic_type() == "Epic":
        epic, current = current, current.parent
    return epic


def _epic_outline(epic, shown: List) -> dict:
    """An epic's outline entry: a group for each sub-epic, at any depth, that holds a shown story."""
    groups: List[dict] = []
    pending = list(epic.epics)
    while pending:
        sub_epic = pending.pop(0)
        stories = [story.name for story in sub_epic.stories if story in shown]
        if stories:
            groups.append({"name": sub_epic.name, "stories": stories})
        pending[:0] = sub_epic.epics
    return {"name": epic.name, "groups": groups, "stories": [story.name for story in epic.stories if story in shown]}


class ScreenNotOnMap(KeyError):
    """A link names a screen the map does not have; transitions, tabs, and destinations join screens on one map."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Screen {name!r} not found")
        self.name = name


class UxMap(UxNode):
    _semantic_type_name = "UxMap"

    screen_type: type[Screen] = Screen
    region_type: type[Region] = Region
    control_type: type[Control] = Control
    story_demo_control_type: type[StoryDemoControl] = StoryDemoControl
    transition_type: type[Transition] = Transition
    content_type_type: type[ContentType] = ContentType
    nav_component_type: type[NavComponent] = NavComponent
    """The node types this format's map is made of; a format that writes a node its own way names its subclass here,
    and every reader and copy of the map makes its nodes through them."""

    workspace_files: tuple[str, ...] = ()
    """Where this format's map sits in a workspace folder, as glob patterns tried in order; ``{folder}`` is the
    folder's own name. The first pattern that matches a file wins."""

    def __init__(self, name: str = "UxMap", sequential_order: int = 0, graph: Graph | None = None) -> None:
        # A map is the root of its screens, their parts and the stories they show; one made on no graph keeps its own,
        # since its story links resolve on the graph its screens are on.
        super().__init__(name, sequential_order, graph if graph is not None else Graph())
        self.scope: str = ""
        self._story_references = ReferencePaths()
        self._object_references = ReferencePaths()
        self.screens = ModelChildren(self, "screens")
        self.transitions = Transitions(self)
        self.content_types = ContentTypes(self)
        self.nav_components = NavComponents(self)
        self.context = UxContext(graph=self.graph)
        self._link(self.context, "context")

    @classmethod
    def create(cls, name: str | Graph = "UxMap", sequential_order: int = 0, graph: Graph | None = None) -> "UxMap":
        """A new map; given a graph in place of a name, a map named `UxMap` whose nodes live on that graph."""
        if not isinstance(name, Graph):
            return cls(name, sequential_order, graph)
        return cls("UxMap", sequential_order, name)

    @classmethod
    def copy_of(cls, source: "UxMap") -> "UxMap":
        """source as a map of this format, on a graph of its own, made of this format's node types: its screens with
        their regions, controls, and the stories they show, its transitions, content types and nav components, and its
        context."""
        copy = cls.create(source.name)
        with copy.batch_schema_sync():
            copy._take_fields(source)
            screens = {id(screen): copy._screen_copy(screen) for screen in source.screens}
            for screen in source.screens:
                copy.append_screen(screens[id(screen)])
            for screen in source.screens:
                copy._take_screen_parts(screen, screens)
            copy._take_components(source, screens)
        return copy

    def _take_fields(self, source: "UxMap") -> None:
        self.scope = source.scope
        self.story_references = source.story_references.as_list()
        self.object_references = source.object_references.as_list()
        self.context.notes = list(source.context.notes)
        self.context.invariants = list(source.context.invariants)

    def _screen_copy(self, screen: Screen) -> Screen:
        copy = self.screen_type(screen.name, screen.sequential_order, screen.slug, screen.layout, screen.description, graph=self.graph)
        copy.inactive_tabs = list(screen.inactive_tabs)
        copy.domain_terms = list(screen.domain_terms)
        copy.domain_concepts = list(screen.domain_concepts)
        copy.image = screen.image
        copy.prototype = screen.prototype
        copy.show_what(screen)
        return copy

    def _take_screen_parts(self, screen: Screen, screens: dict) -> None:
        copy = screens[id(screen)]
        copy.chrome_of = screens.get(id(screen.chrome_of)) if screen.chrome_of is not None else None
        for region in screen.regions:
            region_copy = self.region_type(region.name, region.sequential_order, region.area, self.graph)
            for control in region.controls:
                region_copy.append_control(self._control_copy(control, screens))
            copy.append_region(region_copy)

    def _control_copy(self, control: Control, screens: dict) -> Control:
        common = (control.name, control.sequential_order, control.control_type, control.label, control.bound_field)
        if isinstance(control, StoryDemoControl):
            copy: Control = self.story_demo_control_type(
                *common, control.story_steps, control.set_input, control.item_story_steps, control.item_value,
                control.item_label, graph=self.graph,
            )
        else:
            copy = self.control_type(*common, graph=self.graph)
        copy.states = list(control.states)
        for interaction in control.interactions:
            destination = screens.get(id(interaction.destination)) if interaction.destination is not None else None
            copy.append_interaction(Interaction(interaction.name, interaction.sequential_order, interaction.trigger,
                                                interaction.effect, destination, self.graph))
        return copy

    def _take_components(self, source: "UxMap", screens: dict) -> None:
        for transition in source.transitions:
            self.transitions.append(self.transition_type(
                transition.name, transition.sequential_order, screens.get(id(transition.from_screen)),
                screens.get(id(transition.to_screen)), transition.trigger, transition.nav_type, self.graph,
            ))
        for content_type in source.content_types:
            copy = self.content_type_type(content_type.name, content_type.sequential_order, content_type.hierarchy, self.graph)
            copy.key_actions = list(content_type.key_actions)
            self.content_types.append(copy)
        for nav in source.nav_components:
            copy = self.nav_component_type(nav.name, nav.sequential_order, nav.ux_type, self.graph)
            copy.destinations = [screens[id(screen)] for screen in nav.destinations if id(screen) in screens]
            self.nav_components.append(copy)

    @classmethod
    def from_workspace(cls, root: Path) -> Optional["UxMap"]:
        """The map this format reads from its file in the workspace folder root; none when the folder has no such file."""
        loader = cls.create()
        found = loader.workspace_file(Path(root))
        return None if found is None else loader.parse(found.read_text(encoding="utf-8"))

    def workspace_file(self, root: Path) -> Optional[Path]:
        for pattern in self.workspace_files:
            matches = sorted(path for path in root.glob(pattern.format(folder=root.name)) if path.is_file())
            if matches:
                return matches[0]
        return None

    @property
    def story_references(self) -> ReferencePaths:
        """Paths to Stories JS artifacts, each stored once."""
        return self._story_references

    @story_references.setter
    def story_references(self, paths: Iterable[str]) -> None:
        self._story_references.replace(list(paths))

    @property
    def object_references(self) -> ReferencePaths:
        """Paths to object-model JS artifacts (Clean Engineering), each stored once."""
        return self._object_references

    @object_references.setter
    def object_references(self, paths: Iterable[str]) -> None:
        self._object_references.replace(list(paths))

    def append_screen(self, screen: Screen) -> None:
        self.screens.append(screen)
        self._renumber(self.screens)

    def find_screen(self, name: str) -> Screen:
        for screen in self.screens:
            if screen.name == name:
                return screen
        raise ScreenNotOnMap(name)

    def story_outline(self) -> List[dict]:
        """The story map above the stories this map's screens show, for the story explorer to place screens under:
        each epic in the order its screens first show it, with ``groups`` for its sub-epics and ``stories`` for the
        stories on the epic itself, each in story-map order. Only stories on the map's graph have an epic to place
        them under, so with no story map on the graph the outline is empty and the explorer lists the screens flat."""
        shown = [story for screen in self.screens for story in screen.shows]
        epics: List = []
        for story in shown:
            epic = _top_epic(story)
            if epic is not None and epic not in epics:
                epics.append(epic)
        return [_epic_outline(epic, shown) for epic in epics]
