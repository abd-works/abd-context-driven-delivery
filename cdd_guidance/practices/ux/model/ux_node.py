"""UxNode - abstract base for every node in every format."""

from __future__ import annotations

from typing import List, Optional

from harness.graph.bound_node import BoundNode
from harness.graph.graph import Graph


class UxNode(BoundNode):
    """Subclasses declare `_semantic_type_name`, the node type the graph records, and each child belongs to its owner."""

    _graph_practice = "ux"
    _semantic_type_name: str = "UxNode"
    _belongs = {
        ("Screen", "UxMap"),
        ("Transition", "UxMap"),
        ("ContentType", "UxMap"),
        ("NavComponent", "UxMap"),
        ("UxContext", "UxMap"),
        ("Region", "Screen"),
        ("Control", "Region"),
        ("StoryDemoControl", "Region"),
        ("Interaction", "Control"),
        ("Interaction", "StoryDemoControl"),
    }

    def __init__(self, name: str, sequential_order: int, graph: Optional[Graph] = None) -> None:
        super().__init__(name, sequential_order, graph)

    def _renumber(self, nodes: List["UxNode"]) -> None:
        for index, node in enumerate(nodes):
            node.sequential_order = index
