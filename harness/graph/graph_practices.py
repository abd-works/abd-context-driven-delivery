"""GraphPractices. The practices one graph holds, the ones a load reads, and the ones open in it now."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools.progress import report_progress
from harness.guidance.practice_catalogue import UnknownPractice

if TYPE_CHECKING:
    from harness.graph.graph import Graph, PracticeNodes
    from harness.graph.saved_graph import SavedGraph
    from harness.guidance.guidance import PracticeGuidance


class GraphPractices:
    """The practices one graph holds, which the graph makes once and keeps (``graph.practices``): every practice it was
    given (``held``), the ones a load reads, each on the source root its part of the graph keeps (``chosen``), and the
    ones open in it now, which hold its nodes (``opened``). It is always the same practice objects, the ones the graph
    was given, so code that holds a practice keeps it: a practice is looked up by its key only for a call that names it
    by the key it sent (``named``), and code that knows the practice's class asks for it by that class (``of``,
    ``loaded``). It holds a saved graph's practices and rebuilds each open practice's tree; the build takes every other
    step on the open practices itself."""

    def __init__(self, graph: Graph, held: Iterable[PracticeGuidance]) -> None:
        self._graph = graph
        # Every practice the graph holds, by key, whether a load reads it or not.
        self.held = {practice.key: practice for practice in held}
        # The practices open in the graph, by key, in the order they were opened.
        self.opened: dict[str, PracticeGuidance] = {}
        # The practices the next load reads, each from the source root its part keeps.
        self.chosen: list[PracticeGuidance] = []

    def named(self, key: str) -> PracticeGuidance:
        """The practice called key, opened in the graph on the folder it last loaded the first time it is asked for: the
        one lookup by key, for a call that names a practice by the key it sent."""
        practice = self.held.get(key)
        if practice is None:
            raise UnknownPractice(key, tuple(self.held))
        return self._opened(practice)

    def of(self, kind: type) -> PracticeGuidance:
        """The practice of class kind, such as the graph's Stories for ``Stories``, opened like ``named``."""
        practice = next((held for held in self.held.values() if type(held) is kind), None)
        if practice is None:
            raise UnknownPractice(kind.__name__, tuple(self.held))
        return self._opened(practice)

    def loaded(self, kind: type) -> PracticeGuidance | None:
        """The practice of class kind when it is open in the graph; none when it is not. A practice that links its
        nodes to another's, or checks them against another's, asks this, so it opens nothing."""
        return next((practice for practice in self.opened.values() if type(practice) is kind), None)

    def part_of(self, practice: PracticeGuidance) -> PracticeNodes:
        """practice's part of the graph, where its nodes and edges are kept; ``UnknownPractice`` for a practice another
        graph holds, so no graph records an edge in a practice it does not hold."""
        if practice.reading.graph is not self._graph:
            raise UnknownPractice(practice.key, tuple(self.held))
        return practice.reading.in_graph

    def choose(self, roots: dict[PracticeGuidance, Path]) -> None:
        """Read each practice of roots from its root; the next load reads only those."""
        for practice in self.held.values():
            practice.reading.in_graph.source_root_path = roots.get(practice)
        self.chosen = list(roots)

    @property
    def roots_by_key(self) -> dict[str, Path]:
        """Each chosen practice's root by its key, as a saved graph and a build order keep it."""
        return {practice.key: practice.reading.in_graph.source_root_path for practice in self.chosen}

    def open_chosen(self) -> None:
        """Forget every node and open each chosen practice on its root, holding its root node alone."""
        self._close_all()
        for practice in self.chosen:
            self._open(practice, practice.reading.in_graph.source_root_path)

    def reopen(self, saved: SavedGraph, folder: Path) -> None:
        """Choose and hold every practice saved keeps of those the graph holds, each on the source root it was saved
        with."""
        kept = saved.of_practices(list(self.held))
        self.choose({self.held[key]: record.root_in(folder) for key, record in kept.practices.items()})
        self.hold(kept, folder)

    def hold(self, saved: SavedGraph, folder: Path | None) -> None:
        """Hold exactly the practices saved keeps, of those the graph holds, each on the source root it was saved with:
        their nodes, then the edges between them, which may cross practices, and the violations on them, then each
        practice's tree."""
        self._close_all()
        kept = {self.held[key]: record for key, record in saved.practices.items() if key in self.held}
        for practice, record in kept.items():
            report_progress(f"Loading saved {practice.key} nodes")
            self._open(practice, record.root_in(folder))
            practice.reading.in_graph.restore.nodes(record)
        for practice, record in kept.items():
            practice.reading.in_graph.restore.links(record)
        self.rebuild_trees()

    def rebuild_trees(self) -> None:
        for practice in self.opened.values():
            practice.reading.in_graph.root.tree.rebuild()

    def _opened(self, practice: PracticeGuidance) -> PracticeGuidance:
        """practice, opened in the graph on the folder it last loaded the first time it is asked for."""
        if practice.key not in self.opened:
            self._open(practice, practice.reading.in_graph.source_root_path or self._graph.scope.folder)
        return practice

    def _open(self, practice: PracticeGuidance, root: Path | None) -> None:
        self.opened[practice.key] = practice
        practice.reading.in_graph.loading.open(root)

    def _close_all(self) -> None:
        """Forget every practice's nodes and edges, so a load reads them again from nothing."""
        self.opened = {}
        for practice in self.held.values():
            practice.reading.in_graph.loading.close()
