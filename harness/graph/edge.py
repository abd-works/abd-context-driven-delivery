"""Edges: one kind of edge between two nodes, where its group sits under a node in the explorer tree, and one edge.

The graph, the schema edges between model objects, and every practice's reader record edges through these, so they
sit below all of them."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness.graph.graph import Node

# How an edge's nodes are shown under its parent: as children (``direct``) or under a child named for the kind.
Display = str

# Where each edge kind's group sits under a node in the explorer tree, lowest first. A practice orders its groups
# by these numbers, and graph.json saves them on each edge, so every loader and model reads them through EdgeType.
EDGE_ORDER: dict[str, int] = {
    "decomposedInto": 1,
    "relative": 1,
    "root": 1,
    "descriptions": 1,
    "participants": 1,
    "screens": 1,
    "owns": 2,
    "background": 2,
    "contexts": 2,
    "parameters": 2,
    "aggregates": 2,
    "given": 2,
    "scenarios": 3,
    "properties": 3,
    "observations": 3,
    "steps": 4,
    "demonstrates": 4,
    "shownOn": 4,
    "specifiedBy": 4,
    "specifies": 4,
    "examples": 5,
    "belongsTo": 5,
    "hasParameter": 6,
    "increments": 6,
    "accesses": 6,
    "hasType": 7,
    "returnType": 7,
    "stories": 7,
    "associates": 7,
    "observes": 8,
    "demonstratedThrough": 8,
    "ands": 9,
    "uses": 9,
    "invokedBy": 9,
    "returns": 10,
    "retrievedUsing": 11,
    "invokes": 12,
    "dependsOn": 13,
    "usedBy": 14,
}
# A kind only a pattern overlay's schema names: a child sits with the owned children, a relationship after them.
_DIRECT_KIND_ORDER = 2
_RELATIONSHIP_KIND_ORDER = 7


class EdgeType:
    """One kind of edge: its name, where its group sits under a node in the explorer tree, and whether its nodes are
    shown as children (``direct``) or under a child named for the kind (``grouped``, ``relationship``)."""

    def __init__(self, kind: str, order: int, display: Display) -> None:
        self.kind = kind
        self.order = order
        self.display = display

    @classmethod
    def from_kind(cls, kind: str, display: Display = "direct") -> EdgeType:
        """The edge type of kind, at the place ``EDGE_ORDER`` gives it, or after its display's other kinds."""
        default = _DIRECT_KIND_ORDER if display == "direct" else _RELATIONSHIP_KIND_ORDER
        return cls(kind, EDGE_ORDER.get(kind, default), display)


class Edge:
    def __init__(self, kind: str, order: int, display: Display, parent: Node, child: Node) -> None:
        self.kind = kind
        self.order = order
        self.display = display
        self.parent = parent
        self.child = child

    @property
    def stage(self) -> str:
        """The child node's stage. An edge does not store one of its own."""
        return self.child.stage
