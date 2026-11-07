"""Load a working copy into the graph through the practices and pattern overlays registered with it.

Each practice reads its own nodes (see ``graph_practice.py``); the graph reads them in the order their dependencies
need, links them once all are read, adds the applied overlays' nodes, and then runs every practice's rules.
"""

from __future__ import annotations

from harness.graph.graph import EdgeType, Graph, edge_order
from harness.graph.graph_practice import GraphPractices
from harness.graph.rules import attach_rules
from harness.graph.schema_rules import active_overlay_patterns

_LOADED = ["nodes", "edges", "rules"]


def fill_working_copy(graph: Graph) -> None:
    if graph._folder is None:
        return
    practices = GraphPractices.in_reading_order(list(graph.practices))
    for graph_practice in practices:
        practice = graph.practice(graph_practice.name)
        practice.node_types.update(graph_practice.node_types)
        graph_practice.read(practice)
        practice.loaded = list(_LOADED)
    for graph_practice in practices:
        graph_practice.link(graph)
    patterns = active_overlay_patterns(tuple(graph.overlays))
    for pattern in patterns:
        GraphPractices.overlay(pattern).read(graph)
    _offer_overlay_types(graph, patterns)
    for practice in graph.practices.values():
        attach_rules(practice)
        practice.loaded = list(_LOADED)


def _offer_overlay_types(graph: Graph, patterns: tuple[str, ...]) -> None:
    """Offer the overlay schema's node and connector types in the filter lists before rules run."""
    from harness.graph.schema_edges import overlay_edge_display, relationship_kinds_for_patterns
    from harness.graph.schema_rules import schema_semantic_types_for_practice

    if not patterns:
        return
    edge_kinds = relationship_kinds_for_patterns(patterns)
    for name, practice in graph.practices.items():
        practice.node_types.update(schema_semantic_types_for_practice(name, patterns))
        for kind in edge_kinds.get(name, ()):
            if kind not in practice.edge_types:
                # A kind no edge was recorded under is listed after the ones the tree shows.
                practice.edge_types[kind] = EdgeType(kind, edge_order(kind, "relationship"), overlay_edge_display(kind))
