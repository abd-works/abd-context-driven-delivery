"""GraphPractices. The practices one graph holds, the ones a load reads, and the ones open in it now."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools.progress import report_progress
from harness.guidance.practice_catalogue import UnknownPractice

if TYPE_CHECKING:
    from harness.graph.graph import Graph, PracticeNodes
    from harness.graph.saved_graph import GraphChanges, SavedGraph
    from harness.guidance.guidance import PracticeGuidance


class GraphPractices:
    """The practices one graph holds, which the graph makes once and keeps (``graph.practices``): every practice it was
    given (``held``), the ones a load reads, each on the source root its part of the graph keeps (``chosen``), and the
    ones open in it now, which hold its nodes (``opened``). It is always the same practice objects, the ones the graph
    was given, so code that holds a practice keeps it: a practice is looked up by its key only for a call that names it
    by the key it sent (``named``), and code that knows the practice's class asks for it by that class (``of``,
    ``loaded``). The build asks it to take each step on every open practice: a saved graph's practices held, a worker's
    changes taken, a refresh's files forgotten, the rules run, and each practice's tree rebuilt."""

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

    def take(self, changes: GraphChanges) -> None:
        """Change what the open practices hold as a worker's changes say: every practice's nodes first, then the edges,
        which may cross practices, and the violations; then each changed practice's tree. The graph then holds what the
        worker's whole answer says, without reading it back."""
        changed = {self.held[key]: record for key, record in changes.practices.items() if key in self.held and not record.is_empty}
        for practice, record in changed.items():
            practice.reading.in_graph.restore.changes(record)
        for practice, record in changed.items():
            practice.reading.in_graph.restore.links(record)
        for practice in changed:
            practice.reading.in_graph.put_in_source_order()
            practice.reading.in_graph.rebuild_tree()

    def forget(self, files: list[Path]) -> None:
        """Drop the nodes read from files in every open practice, every edge that joins one of them, and every rule's
        findings, so a refresh reads those files again from nothing."""
        dropped: set[int] = set()
        for practice in self.opened.values():
            dropped |= practice.reading.in_graph.forget_files(files)
        for practice in self.opened.values():
            practice.reading.in_graph.drop_edges(lambda edge: id(edge.parent) in dropped or id(edge.child) in dropped)
            practice.reading.in_graph.renew_rules()

    def in_reading_order(self) -> list[PracticeGuidance]:
        """The open practices, each after the practices it reads while it reads its own."""
        ordered: list[PracticeGuidance] = []

        def place(practice: PracticeGuidance) -> None:
            if practice in ordered:
                return
            for earlier in practice.reading.reads_after:
                if earlier in self.opened:
                    place(self.opened[earlier])
            ordered.append(practice)

        for practice in list(self.opened.values()):
            place(practice)
        return ordered

    def check(self) -> None:
        """Put every open practice's nodes in source order, as a fresh build reads them, and run its graph rules: a rule
        that reports the first of two nodes then reports the same node whichever build read them."""
        for practice in self.opened.values():
            practice.reading.in_graph.put_in_source_order()
        for practice in self.opened.values():
            practice.reading.in_graph.rule_run.check()

    def rebuild_trees(self) -> None:
        for practice in self.opened.values():
            practice.reading.in_graph.rebuild_tree()

    def _opened(self, practice: PracticeGuidance) -> PracticeGuidance:
        """practice, opened in the graph on the folder it last loaded the first time it is asked for."""
        if practice.key not in self.opened:
            self._open(practice, practice.reading.in_graph.source_root_path or self._graph.scope.folder)
        return practice

    def _open(self, practice: PracticeGuidance, root: Path | None) -> None:
        self.opened[practice.key] = practice
        practice.reading.in_graph.open(root)

    def _close_all(self) -> None:
        """Forget every practice's nodes and edges, so a load reads them again from nothing."""
        self.opened = {}
        for practice in self.held.values():
            practice.reading.in_graph.close()
