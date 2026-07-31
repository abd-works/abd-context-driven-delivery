"""UxMap - root container for screens and UxComponent collections."""

from __future__ import annotations

from typing import Iterable, List

from .collections import ContentTypes, NavComponents, Transitions
from .nodes import ContentType, NavComponent, Screen, Transition, UxContext
from .reference_paths import ReferencePaths
from .update_report import ChildCollectionPair
from .ux_node import UxNode


class UxMap(UxNode):
    _semantic_type_name = "UxMap"

    def __init__(self, name: str = "UxMap", sequential_order: int = 0) -> None:
        super().__init__(name, sequential_order)
        self.scope: str = ""
        self._story_references = ReferencePaths()
        self._object_references = ReferencePaths()
        self.screens: List[Screen] = []
        self.transitions = Transitions()
        self.content_types = ContentTypes()
        self.nav_components = NavComponents()
        self.context: UxContext = UxContext()

    @property
    def story_references(self) -> ReferencePaths:
        """Paths to Stories JS artifacts. Bind/dedupe behind the property."""
        return self._story_references

    @story_references.setter
    def story_references(self, paths: Iterable[str] | ReferencePaths) -> None:
        if isinstance(paths, ReferencePaths):
            self._story_references.replace(paths.as_list())
        else:
            self._story_references.replace(paths)

    @property
    def object_references(self) -> ReferencePaths:
        """Paths to object-model JS artifacts (CE). Bind/dedupe behind the property."""
        return self._object_references

    @object_references.setter
    def object_references(self, paths: Iterable[str] | ReferencePaths) -> None:
        if isinstance(paths, ReferencePaths):
            self._object_references.replace(paths.as_list())
        else:
            self._object_references.replace(paths)

    def append_screen(self, screen: Screen) -> None:
        self.screens.append(screen)
        self._renumber(self.screens)

    def remove_screen(self, screen_name: str) -> Screen:
        for index, screen in enumerate(self.screens):
            if screen.name == screen_name:
                removed = self.screens.pop(index)
                self._renumber(self.screens)
                return removed
        raise KeyError(f"Screen {screen_name!r} not found")

    def find_screen(self, name: str) -> Screen:
        for screen in self.screens:
            if screen.name == name:
                return screen
        raise KeyError(f"Screen {name!r} not found")

    def append_transition(self, transition: Transition) -> None:
        """Delegate - prefer `ux_map.transitions.append(transition)`."""
        self.transitions.append(transition)

    def append_content_type(self, content_type: ContentType) -> None:
        """Delegate - prefer `ux_map.content_types.append(content_type)`."""
        self.content_types.append(content_type)

    def append_nav_component(self, nav_component: NavComponent) -> None:
        """Delegate - prefer `ux_map.nav_components.append(nav_component)`."""
        self.nav_components.append(nav_component)

    def update_self(self, source: "UxMap") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.scope = source.scope
        self.story_references = source.story_references
        self.object_references = source.object_references
        self.context.translate_from(source.context)
        self.transitions.translate_from(source.transitions)
        self.content_types.translate_from(source.content_types)
        self.nav_components.translate_from(source.nav_components)

    def child_collections(self, source: "UxMap") -> List[ChildCollectionPair]:
        return [
            ChildCollectionPair(
                self_children=self.screens,
                source_children=source.screens,
                create_child=self.create_child_screen,
            ),
        ]

    def create_child_screen(self, source: Screen) -> Screen:
        return Screen(source.name, source.sequential_order, source.slug, source.layout)

    def snapshot_fields(self) -> dict:
        return {
            "scope": self.scope,
            "story_references": self.story_references.as_list(),
            "object_references": self.object_references.as_list(),
        }

    def all_story_names(self) -> List[str]:
        names: List[str] = []
        for screen in self.screens:
            for story_name in screen.story_names:
                if story_name not in names:
                    names.append(story_name)
        return names
