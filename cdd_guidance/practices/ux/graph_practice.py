"""How UX takes part in the graph: it checks its screen rules on the UX maps put on a graph, and offers the explorer the
node types a UX map is made of. A working-copy load reads no UX files yet."""

from __future__ import annotations

from harness.graph.graph_practice import GraphPractice, GraphPractices

_PACKAGE = "cdd_guidance.practices.ux"


class UxGraph(GraphPractice):
    """The UX practice's node types and its rules."""

    node_types = (
        "UxMap",
        "Screen",
        "Region",
        "Control",
        "StoryDemoControl",
        "Interaction",
        "Transition",
        "ContentType",
        "NavComponent",
        "UxContext",
    )


GraphPractices.register(UxGraph("ux", _PACKAGE))
