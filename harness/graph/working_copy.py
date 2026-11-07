"""WorkingCopy. The folder a graph loads, read through the practices the graph holds and the pattern overlays it applies.

Each practice reads its own nodes (``PracticeGuidance.read_working_copy``); the working copy reads them in the order their
dependencies need, links them once all are read, adds the applied overlays' nodes, and then runs every practice's rules.
"""

from __future__ import annotations

from harness.graph.graph import EdgeType, Graph, PracticeGraph
from harness.graph.pattern_overlays import GraphOverlay
from harness.graph.rules import PracticeChecks

_LOADED = ["nodes", "edges", "rules"]


class WorkingCopy:
    """The working copy one graph loads from its folder."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def fill(self) -> None:
        """Read every practice the graph holds, link them, add the overlays' nodes, and run every practice's rules."""
        if self.graph.loaded_folder is None:
            return
        practices = self._in_reading_order()
        for practice in practices:
            practice.node_types.update(practice.guidance.node_types)
            practice.guidance.read_working_copy(practice)
            practice.loaded = list(_LOADED)
        for practice in practices:
            practice.guidance.link_to_other_practices(self.graph)
        for pattern in self.graph.overlay_patterns:
            GraphOverlay.of(pattern).read(self.graph)
        self._offer_overlay_types()
        for practice in self.graph.practices.values():
            PracticeChecks(practice).run()
            practice.loaded = list(_LOADED)

    def _in_reading_order(self) -> list[PracticeGraph]:
        """The practices the graph holds, each after the practices it reads while it reads its own."""
        ordered: list[PracticeGraph] = []
        for practice in list(self.graph.practices.values()):
            self._place(practice, ordered)
        return ordered

    def _place(self, practice: PracticeGraph, ordered: list[PracticeGraph]) -> None:
        if practice in ordered:
            return
        for earlier in practice.guidance.reads_after:
            if earlier in self.graph.practices:
                self._place(self.graph.practices[earlier], ordered)
        ordered.append(practice)

    def _offer_overlay_types(self) -> None:
        """Offer the overlay schemas' node and relationship types in the filter lists before rules run."""
        patterns = self.graph.overlay_patterns
        if not patterns:
            return
        overlays = [GraphOverlay.of(pattern) for pattern in patterns]
        for name, practice in self.graph.practices.items():
            schema = practice.schema
            practice.node_types.update(schema.types)
            for kind in schema.overlay_relationship_kinds - set(practice.edge_types):
                display = "direct" if any(overlay.display_of(kind) == "direct" for overlay in overlays) else "relationship"
                # A kind no edge was recorded under is listed after the ones the tree shows.
                practice.edge_types[kind] = EdgeType(kind, EdgeType.from_kind(kind, "relationship").order, display)
