"""The Bookshop project the graph specs of Stories read: a story map, scenarios written in markdown, story tests in
Python and TypeScript with their examples, a domain model document, and the code the story tests call. It is the
project round 3 of exploratory testing loaded, copied into a folder of its own for each spec, since a working-copy scan
never enters a ``fixtures`` folder."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import cdd_guidance.practices  # noqa: F401 - registers the practices a graph holds
from harness.graph.graph import Graph

_BOOKSHOP = Path(__file__).resolve().parent / "bookshop"
# Every file and folder of the project a load of the whole project names.
WHOLE_PROJECT = (".context", "story_tests", "src", "ordering")
PRACTICES = ("stories", "ddd", "clean_engineering")


class BookshopProject:
    """A copy of the Bookshop project in a folder of its own, and a graph that loaded files of it. The copy goes when
    the project does."""

    def __init__(self, files: tuple[str, ...] = WHOLE_PROJECT, practices: tuple[str, ...] = PRACTICES) -> None:
        self._folder = tempfile.TemporaryDirectory()
        self.root = Path(self._folder.name).resolve() / "bookshop"
        shutil.copytree(_BOOKSHOP, self.root)
        self.graph = Graph()
        self._load(files, practices)

    def _load(self, files: tuple[str, ...], practices: tuple[str, ...]) -> None:
        self.graph.load_files(str(self.root), list(practices), list(files))

    @property
    def stories(self):
        """Stories' part of the graph: its nodes and edges."""
        return self.graph.practices.named("stories").reading.in_graph

    def held(self) -> tuple[set[str], set[tuple[str, str, str]]]:
        """What the graph holds now: the id of every node of every practice, and every edge as its parent, kind and
        child."""
        parts = [practice.reading.in_graph for practice in self.graph.practices.opened.values()]
        nodes = {node.node_id for part in parts for node in part.nodes()}
        edges = {(edge.parent.node_id, edge.kind, edge.child.node_id) for part in parts for edge in part.edge_index.of()}
        return nodes, edges

    def edges(self, kind: str) -> list[tuple[str, str]]:
        """Every edge of kind Stories holds, as the ids of its parent and child."""
        return sorted((edge.parent.node_id, edge.child.node_id) for edge in self.stories.edge_index.of(kind))

    def node_named(self, type: str, name: str, file: str = ""):
        """Stories' nodes of type called name, read from file when one is given."""
        return [node for node in self.stories.nodes(type) if node.name == name and (not file or node.source.file == file)]


class BookshopWorkingCopy(BookshopProject):
    """A copy of the Bookshop project whose graph loaded the whole working copy, as a session's graph does, so every
    rule validate runs is checked on it, the rule that content conforms to its schema among them. ``rewritten`` changes the copy before the load: each
    file named from the project's root, with the text to take out and the text to put in its place; ``removed`` names
    the files the copy is to be without; ``written`` names each file to write, from the root, with its whole text."""

    def __init__(
        self,
        practices: tuple[str, ...] = PRACTICES,
        rewritten: dict[str, tuple[str, str]] | None = None,
        removed: tuple[str, ...] = (),
        written: dict[str, str] | None = None,
    ) -> None:
        self._rewritten = rewritten or {}
        self._removed = removed
        self._written = written or {}
        super().__init__(practices=practices)

    def _load(self, files: tuple[str, ...], practices: tuple[str, ...]) -> None:
        for file, (old, new) in self._rewritten.items():
            path = self.root / file
            path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
        for file in self._removed:
            (self.root / file).unlink()
        for file, text in self._written.items():
            (self.root / file).write_text(text, encoding="utf-8")
        self.graph.load_working_copy(str(self.root), {key: str(self.root) for key in practices}, force=True)

    def findings(self, rule: str) -> list[str]:
        """Each message the rule called rule recorded on Stories' nodes, after the graph has checked the practice as
        validate does."""
        self.stories.rule_run.check()
        entries = (node.rules.entries.get(rule) for node in self.stories.nodes())
        return [violation.message for entry in entries for violation in getattr(entry, "violations", [])]

    def observed_by(self, step_name: str, file: str) -> list[str]:
        """The names of the examples the step called step_name in file observes."""
        steps = [node for node in self.stories.nodes() if node.name == step_name and node.source.file == file]
        return sorted(edge.child.name for step in steps for edge in self.graph.edges.from_parent("observes", step))
