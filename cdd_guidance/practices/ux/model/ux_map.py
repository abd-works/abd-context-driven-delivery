"""UxMap - root container for screens and UxComponent collections."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

from harness.graph.bound_node import BoundChildren
from harness.graph.graph import Graph

from .collections import ContentTypes, NavComponents, Transitions
from .nodes import Screen, UxContext
from .reference_paths import ReferencePaths
from .ux_node import UxNode


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
        self.screens = BoundChildren(self, "screens")
        self.transitions = Transitions(self)
        self.content_types = ContentTypes(self)
        self.nav_components = NavComponents(self)
        self.context = UxContext(graph=self.graph)
        self._link(self.context, "context")

    @classmethod
    def create(cls, name: str | Graph = "UxMap", sequential_order: int = 0, graph: Graph | None = None) -> "UxMap":
        """A new map, or, given a graph, the map already on that graph."""
        if not isinstance(name, Graph):
            return cls(name, sequential_order, graph)
        opened = cls("UxMap", sequential_order, name)
        opened._copy_screens_on_graph()
        return opened

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

    def _copy_screens_on_graph(self) -> None:
        others = [node for node in self._copies_on_graph("UxMap") if node.screens]
        if not others:
            return
        for screen in others[0].screens:
            self.append_screen(Screen(screen.name, screen.sequential_order))

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
            for story_name in screen.story_names:
                if story_name not in names:
                    names.append(story_name)
        return names
