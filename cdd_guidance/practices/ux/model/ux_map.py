"""UxMap - root container for screens and UxComponent collections."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

from harness.graph.model_node import ModelChildren
from harness.graph.graph import Graph

from .collections import ContentTypes, NavComponents, Transitions
from .nodes import Screen, UxContext
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

    workspace_files: tuple[str, ...] = ()
    """Where this format's map sits in a workspace folder, as glob patterns tried in order; ``{folder}`` is the
    folder's own name. The first pattern that matches a file wins."""

    def __init__(self, name: str = "UxMap", sequential_order: int = 0, graph: Graph | None = None) -> None:
        super().__init__(name, sequential_order, graph)
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

    def remove_screen(self, screen_name: str) -> Screen:
        removed = self.find_screen(screen_name)
        self.screens.pop(self.screens.index(removed))
        self._renumber(self.screens)
        return removed

    def find_screen(self, name: str) -> Screen:
        for screen in self.screens:
            if screen.name == name:
                return screen
        raise ScreenNotOnMap(name)

    def all_story_names(self) -> List[str]:
        names: List[str] = []
        for screen in self.screens:
            for story_name in screen.story_keys:
                if story_name not in names:
                    names.append(story_name)
        return names

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
