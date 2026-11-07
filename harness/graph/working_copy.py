"""WorkingCopy. The folder a graph loads, read through the practices and pattern overlays registered with the graph.

Each practice reads its own nodes (see ``graph_practice.py``); the working copy reads them in the order their
dependencies need, links them once all are read, adds the applied overlays' nodes, and then runs every practice's rules.
"""

from __future__ import annotations

from harness.graph.graph import EdgeType, Graph
from harness.graph.graph_practice import GraphPractices
from harness.graph.rules import PracticeChecks
from harness.graph.schema_rules import PracticeSchema

_LOADED = ["nodes", "edges", "rules"]


class WorkingCopy:
    """The working copy one graph loads from its folder."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def fill(self) -> None:
        """Read every practice the graph holds, link them, add the overlays' nodes, and run every practice's rules."""
        if self.graph.loaded_folder is None:
            return
        practices = GraphPractices.in_reading_order(list(self.graph.practices))
        for graph_practice in practices:
            practice = self.graph.practice(graph_practice.name)
            practice.node_types.update(graph_practice.node_types)
            graph_practice.read(practice)
            practice.loaded = list(_LOADED)
        for graph_practice in practices:
            graph_practice.link(self.graph)
        for pattern in self.graph.overlay_patterns:
            GraphPractices.overlay(pattern).read(self.graph)
        self._offer_overlay_types()
        for practice in self.graph.practices.values():
            PracticeChecks(practice).run()
            practice.loaded = list(_LOADED)

    def _offer_overlay_types(self) -> None:
        """Offer the overlay schemas' node and relationship types in the filter lists before rules run."""
        patterns = self.graph.overlay_patterns
        if not patterns:
            return
        overlays = [GraphPractices.overlay(pattern) for pattern in patterns]
        for name, practice in self.graph.practices.items():
            schema = PracticeSchema.load(name, patterns)
            practice.node_types.update(schema.types)
            for kind in schema.overlay_relationship_kinds - set(practice.edge_types):
                display = "direct" if any(overlay.display_of(kind) == "direct" for overlay in overlays) else "relationship"
                # A kind no edge was recorded under is listed after the ones the tree shows.
                practice.edge_types[kind] = EdgeType(kind, EdgeType.from_kind(kind, "relationship").order, display)
