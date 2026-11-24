"""UxMap - root container for screens and UxComponent collections."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Iterable

from harness.graph.model_node import ModelChildren
from harness.graph.graph import Graph
from harness.guidance.practice_formats import FormatAdapter, TextOrData

from .collections import ContentTypes, NavComponents, Transitions
from .nodes import ContentType, Control, Interaction, NavComponent, Region, Screen, StoryDemoControl, Transition, UxContext
from .reference_paths import ReferencePaths
from .ux_node import UxNode


if TYPE_CHECKING:
    from harness.guidance.guidance import PracticeGuidance

ScreenCopies = dict[int, Screen]
"""Each source screen's copy, by the identity of the source screen, while a map is copied."""


class ScreenNotOnMap(KeyError):
    """A link names a screen the map does not have; transitions, tabs, and destinations join screens on one map."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Screen {name!r} not found")
        self.name = name


class UxMap(UxNode, FormatAdapter):
    _semantic_type_name = "UxMap"
    graph_facts = ("scope",)

    screen_type: type[Screen] = Screen
    region_type: type[Region] = Region
    control_type: type[Control] = Control
    story_demo_control_type: type[StoryDemoControl] = StoryDemoControl
    transition_type: type[Transition] = Transition
    content_type_type: type[ContentType] = ContentType
    nav_component_type: type[NavComponent] = NavComponent
    """The node types this format's map is made of; a format that writes a node its own way names its subclass here,
    and every reader and copy of the map makes its nodes through them."""

    holds_screens: bool = True
    """Whether this format's file holds the map's screens; the UX context file holds only the scope and the notes, so
    a map read from it has none and is not held to having any."""

    map_file_suffixes: tuple[str, ...] = ()
    """The file endings this format's map is written with, such as ``.drawio``; none for a format no file is read
    back from. The graph reading opens only the files that end with one."""

    not_a_map_failures: tuple[type[Exception], ...] = ()
    """What reading a file fails with when the file is not this format's map after all, such as text that is not its
    format. The graph reading keeps such a file, with the reason, among the files it could not read."""

    def content_beside(self, file: Path) -> TextOrData:
        """What a render reads of this format's map from file when the map is written as several files beside it; none
        for a format whose file alone holds its map, which a render reads as the file's text."""
        return None

    def __init__(self, name: str = "UxMap", sequential_order: int = 0, graph: Graph | None = None) -> None:
        # A map is the root of its screens, their parts and the stories they show. One made on no graph is detached, as
        # every model object is until a practice adopts it: its screens keep the stories they show by key, and resolve
        # them once the map is on the graph that holds the stories.
        super().__init__(name, sequential_order, graph)
        self.scope: str = ""
        self._story_references = ReferencePaths()
        self._object_references = ReferencePaths()
        self.screens = ModelChildren(self, "screens")
        self.transitions = Transitions(self)
        self.content_types = ContentTypes(self)
        self.nav_components = NavComponents(self)
        self.context = UxContext()
        self.attach(self.context, "context")

    def join(self, practice: PracticeGuidance) -> None:
        """Make this map and its whole tree practice's nodes, its context with them: the context is the map's one part
        that sits in no list, so the map brings it along itself."""
        super().join(practice)
        # A map made on a graph joins it while it is still being built, before it has its context to bring.
        if "context" in vars(self):
            self.attach(self.context, "context")

    @classmethod
    def create(cls, name: str | Graph = "UxMap", sequential_order: int = 0, graph: Graph | None = None) -> "UxMap":
        """A new map; given a graph in place of a name, a map named `UxMap` whose nodes live on that graph."""
        if not isinstance(name, Graph):
            return cls(name, sequential_order, graph)
        return cls("UxMap", sequential_order, name)

    def copy_of(self, source: "UxMap") -> "UxMap":
        """source as a map of this format, made of this format's node types: its screens with their regions, controls,
        and the stories they show, its transitions, content types and nav components, and its context. The copy is
        detached, as a render writes it to text: it keeps the stories each screen shows by key, and joins a graph only
        when a practice adopts it. It is asked of a map, not its class, as a story map's copy is."""
        copy = type(self).create(source.name)
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
        copy = self.screen_type(screen.name, screen.sequential_order)
        copy.slug, copy.layout, copy.description = screen.slug, screen.layout, screen.description
        copy.inactive_tabs = list(screen.inactive_tabs)
        copy.domain_terms = list(screen.domain_terms)
        copy.domain_concepts = list(screen.domain_concepts)
        copy.image = screen.image
        copy.prototype = screen.prototype
        copy.show_what(screen)
        return copy

    def _take_screen_parts(self, screen: Screen, screens: ScreenCopies) -> None:
        copy = screens[id(screen)]
        copy.chrome_of = screens.get(id(screen.chrome_of)) if screen.chrome_of is not None else None
        for region in screen.regions:
            copy.append_region(self._region_copy(region, screens))

    def _region_copy(self, region: Region, screens: ScreenCopies) -> Region:
        copy = self.region_type(region.name, region.sequential_order)
        copy.area = region.area
        for control in region.controls:
            copy.append_control(self._control_copy(control, screens))
        return copy

    def _control_copy(self, control: Control, screens: ScreenCopies) -> Control:
        demo = isinstance(control, StoryDemoControl)
        copy = (self.story_demo_control_type if demo else self.control_type)(control.name, control.sequential_order)
        copy.control_type, copy.label, copy.bound_field = control.control_type, control.label, control.bound_field
        if demo:
            copy.take_story_fields(control)
        copy.states = list(control.states)
        copy.show_what(control)
        for interaction in control.interactions:
            copy.append_interaction(self._interaction_copy(interaction, screens))
        return copy

    def _interaction_copy(self, interaction: Interaction, screens: ScreenCopies) -> Interaction:
        copy = Interaction(interaction.name, interaction.sequential_order)
        copy.trigger, copy.effect = interaction.trigger, interaction.effect
        copy.destination = screens.get(id(interaction.destination)) if interaction.destination is not None else None
        return copy

    def _take_components(self, source: "UxMap", screens: ScreenCopies) -> None:
        for transition in source.transitions:
            self.transitions.append(self._transition_copy(transition, screens, transition.sequential_order))
        for content_type in source.content_types:
            self.content_types.append(self._content_type_copy(content_type, content_type.sequential_order))
        for nav in source.nav_components:
            self.nav_components.append(self._nav_component_copy(nav, screens, nav.sequential_order))

    def _content_type_copy(self, content_type: ContentType, order: int) -> ContentType:
        """content_type as one of this map's own, at order."""
        copy = self.content_type_type(content_type.name, order)
        copy.hierarchy = content_type.hierarchy
        copy.key_actions = list(content_type.key_actions)
        return copy

    def _nav_component_copy(self, nav: NavComponent, screens: ScreenCopies, order: int) -> NavComponent:
        """nav as one of this map's own, at order, reaching the copies of the screens it reaches."""
        copy = self.nav_component_type(nav.name, order)
        copy.ux_type = nav.ux_type
        copy.destinations = [screens[id(screen)] for screen in nav.destinations if id(screen) in screens]
        return copy

    def _transition_copy(self, transition: Transition, screens: ScreenCopies, order: int) -> Transition:
        """transition as one of this map's own, at order, joining the copies of the screens it joins."""
        copy = self.transition_type(transition.name, order)
        copy.trigger, copy.nav_type = transition.trigger, transition.nav_type
        return copy.joining(screens.get(id(transition.from_screen)), screens.get(id(transition.to_screen)))

    def keep_served_by(self, held: "UxMap") -> None:
        """Take from held, the map a file already holds, what its screens and controls serve and the domain terms its
        screens name, for each screen and control this map holds too: a control is the one of the same name on the
        same screen, in whichever region. What this map holds comes first; nothing it holds is replaced."""
        for mine, theirs in self._screens_also_in(held):
            mine.show_what(theirs)
            for term in theirs.domain_terms:
                mine.attach_domain_term(term)
            mine.layout = mine.layout or theirs.layout
            own = {control.name: control for region in mine.regions for control in region.controls}
            for control in (control for region in theirs.regions for control in region.controls if control.name in own):
                own[control.name].show_what(control)
                own[control.name].control_type = own[control.name].control_type or control.control_type

    def keep_what_only(self, held: "UxMap") -> None:
        """Take from held, the map a file already holds, everything only it holds, so drawing this map over that file
        loses nothing: what its screens and controls serve (``keep_served_by``), and each screen, region, control,
        transition, content type, and nav component this map lacks, after this map's own."""
        with self.batch_schema_sync():
            self.keep_served_by(held)
            screens: ScreenCopies = {id(theirs): mine for mine, theirs in self._screens_also_in(held)}
            for mine, theirs in self._screens_also_in(held):
                self._keep_parts_only(mine, theirs, screens)
            for theirs in [screen for screen in held.screens if id(screen) not in screens]:
                screens[id(theirs)] = self._screen_copy(theirs)
                self.append_screen(screens[id(theirs)])
                self._take_screen_parts(theirs, screens)
            self._keep_transitions_only(held, screens)
            self._keep_components_only(held, screens)

    def _screens_also_in(self, held: "UxMap") -> list[tuple[Screen, Screen]]:
        """Each screen of this map with the screen of the same name held holds."""
        own = {screen.name: screen for screen in self.screens}
        return [(own[theirs.name], theirs) for theirs in held.screens if theirs.name in own]

    def _keep_parts_only(self, mine: Screen, theirs: Screen, screens: ScreenCopies) -> None:
        """Give mine each region only theirs holds, and each of mine's regions the controls only theirs holds in the
        region of the same name."""
        own = {region.name: region for region in mine.regions}
        for region in theirs.regions:
            if region.name not in own:
                mine.append_region(self._region_copy(region, screens))
                continue
            own[region.name].area = own[region.name].area or region.area
            named = {control.name for held_region in mine.regions for control in held_region.controls}
            for control in (control for control in region.controls if control.name not in named):
                own[region.name].append_control(self._control_copy(control, screens))

    def _keep_transitions_only(self, held: "UxMap", screens: ScreenCopies) -> None:
        """Give this map each transition only held holds, joining this map's own screens."""
        own = {(transition.trigger, transition.from_name, transition.to_name) for transition in self.transitions}
        for transition in held.transitions:
            if (transition.trigger, transition.from_name, transition.to_name) not in own:
                self.transitions.append(self._transition_copy(transition, screens, len(self.transitions)))

    def _keep_components_only(self, held: "UxMap", screens: ScreenCopies) -> None:
        """Give this map each content type and each nav component only held holds, by name, a nav component reaching
        this map's own screens."""
        own_types = {content_type.name for content_type in self.content_types}
        for content_type in (content_type for content_type in held.content_types if content_type.name not in own_types):
            self.content_types.append(self._content_type_copy(content_type, len(self.content_types)))
        own_navs = {nav.name for nav in self.nav_components}
        for nav in (nav for nav in held.nav_components if nav.name not in own_navs):
            self.nav_components.append(self._nav_component_copy(nav, screens, len(self.nav_components)))

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
