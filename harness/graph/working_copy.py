"""WorkingCopy. The folder a graph loads, read through the practices the graph holds and the pattern overlays it applies.

Each practice reads its own nodes (``PracticeGuidance.read_working_copy``); the working copy reads them in the order their
dependencies need, links them once all are read, adds the applied overlays' nodes, and then runs every practice's rules.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.graph import EdgeType, Graph
from harness.graph.rules import PracticeChecks

if TYPE_CHECKING:
    from harness.guidance.guidance import PracticeGuidance


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
            self.graph.offer_node_types(practice, practice.node_types)
            practice.read_working_copy()
        for practice in practices:
            practice.link_to_other_practices()
        for overlay in self.graph.pattern_overlays:
            overlay.read(self.graph)
        self._offer_overlay_types()
        for practice in self.graph.practices.values():
            PracticeChecks(practice).run()

    def _in_reading_order(self) -> list[PracticeGuidance]:
        """The practices the graph reads, each after the practices it reads while it reads its own."""
        ordered: list[PracticeGuidance] = []
        for practice in list(self.graph.practices.values()):
            self._place(practice, ordered)
        return ordered

    def _place(self, practice: PracticeGuidance, ordered: list[PracticeGuidance]) -> None:
        if practice in ordered:
            return
        for earlier in practice.reads_after:
            if earlier in self.graph.practices:
                self._place(self.graph.practices[earlier], ordered)
        ordered.append(practice)

    def _offer_overlay_types(self) -> None:
        """Offer the overlay schemas' node and relationship types in the filter lists before rules run."""
        overlays = self.graph.pattern_overlays
        if not overlays:
            return
        for practice in self.graph.practices.values():
            schema = self.graph.schema_of(practice)
            self.graph.offer_node_types(practice, schema.types)
            for kind in schema.overlay_relationship_kinds - set(self.graph.edge_types_of(practice)):
                display = "direct" if any(overlay.display_of(kind) == "direct" for overlay in overlays) else "relationship"
                # A kind no edge was recorded under is listed after the ones the tree shows.
                self.graph.offer_edge_type(practice, EdgeType(kind, EdgeType.from_kind(kind, "relationship").order, display))
