"""Edges: one kind of edge between two nodes, where its group sits under a node in the explorer tree, and one edge.

The graph, the schema edges between model objects, and every practice's reader record edges through these, so they
sit below all of them."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

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
# Kinds no one filters by: belongsTo is the back-edge of every child list, and scopes is left out of the explorer tree.
_NOT_OFFERED = frozenset({"belongsTo", "scopes"})


class EdgeType:
    """One kind of edge: its name, where its group sits under a node in the explorer tree, and whether its nodes are
    shown as children (``direct``) or under a child named for the kind (``grouped``, ``relationship``)."""

    def __init__(self, kind: str, order: int, display: Display) -> None:
        self.kind = kind
        self.order = order
        self.display = display

    @property
    def is_offered(self) -> bool:
        """Whether a person filters the explorer by this kind."""
        return self.kind not in _NOT_OFFERED

    @classmethod
    def from_kind(cls, kind: str, display: Display = "direct") -> EdgeType:
        """The edge type of kind, at the place ``EDGE_ORDER`` gives it, or after its display's other kinds."""
        default = _DIRECT_KIND_ORDER if display == "direct" else _RELATIONSHIP_KIND_ORDER
        return cls(kind, EDGE_ORDER.get(kind, default), display)


class Edge:
    """One edge: the EdgeType of its kind, which says where its group sits and how its nodes show, and the two nodes it
    joins."""

    def __init__(self, type: EdgeType, parent: Node, child: Node) -> None:
        self.type = type
        self.parent = parent
        self.child = child

    @property
    def kind(self) -> str:
        return self.type.kind

    @property
    def display(self) -> Display:
        return self.type.display


class EdgeIndex:
    """The edges one practice holds, by kind, with the EdgeType of each kind, and the indexes a build reads them by:
    the pairs of nodes each kind joins, which keep an edge from being recorded twice, the edges of each kind leaving each
    parent, and the parent a direct edge hangs each child under. Every change to the edges goes through here, so the
    indexes change with them. A practice's part of the graph makes one and keeps it (``in_graph.edge_index``)."""

    def __init__(self) -> None:
        self._edges: dict[str, list[Edge]] = {}
        self.types: dict[str, EdgeType] = {}
        self._pairs: dict[str, set[tuple[int, int]]] = {}
        self._from_parent: dict[str, dict[int, list[Edge]]] = {}
        self._direct_parents: dict[int, Node] | None = None

    def of(self, kind: str | None = None) -> list[Edge]:
        """Every edge held, or only those of kind, in the order they were recorded."""
        if kind is not None:
            return list(self._edges.get(kind, []))
        return [edge for group in self._edges.values() for edge in group]

    def offer(self, edge_type: EdgeType) -> None:
        """Offer a kind of edge in the explorer's filter, before any edge of it is recorded."""
        self.types[edge_type.kind] = edge_type

    def record(self, edge_type: EdgeType, parent: Node, child: Node) -> bool:
        """Record an edge of edge_type from parent to child, once; whether it was new. The first edge of a kind sets
        where its kind sits."""
        kind = edge_type.kind
        pairs = self._pairs.setdefault(kind, set())
        if (id(parent), id(child)) in pairs:
            return False
        self.types.setdefault(kind, edge_type)
        edge = Edge(edge_type, parent, child)
        self._edges.setdefault(kind, []).append(edge)
        pairs.add((id(parent), id(child)))
        self._from_parent.setdefault(kind, {}).setdefault(id(parent), []).append(edge)
        if self._direct_parents is not None and edge.display == "direct":
            self._direct_parents.setdefault(id(child), parent)
        return True

    def drop(self, dropped: Callable[[Edge], bool]) -> list[Edge]:
        """Drop each edge that dropped says to; answer the edges dropped."""
        removed: list[Edge] = []
        for kind, edges in self._edges.items():
            gone = [edge for edge in edges if dropped(edge)]
            if gone:
                removed.extend(gone)
                ids = {id(edge) for edge in gone}
                self._index(kind, [edge for edge in edges if id(edge) not in ids])
        if removed:
            self._direct_parents = None
        return removed

    def _index(self, kind: str, edges: list[Edge]) -> None:
        """Hold exactly edges of kind, with the pairs they join and the edges leaving each parent."""
        self._edges[kind] = edges
        self._pairs[kind] = {(id(edge.parent), id(edge.child)) for edge in edges}
        by_parent: dict[int, list[Edge]] = {}
        for edge in edges:
            by_parent.setdefault(id(edge.parent), []).append(edge)
        self._from_parent[kind] = by_parent

    def from_parent(self, kind: str, parent: Node) -> list[Edge]:
        """The edges of kind leaving parent, in the order they were recorded."""
        return list(self._from_parent.get(kind, {}).get(id(parent), []))

    def direct_parent(self, child: Node) -> Node | None:
        """The node the first direct edge to child hangs it under; none when no direct edge leads to it."""
        if self._direct_parents is None:
            self._direct_parents = {}
            for edge in self.of():
                if edge.display == "direct":
                    self._direct_parents.setdefault(id(edge.child), edge.parent)
        return self._direct_parents.get(id(child))

    def clear(self) -> None:
        """Forget every edge and every kind offered."""
        self.types = {}
        self._edges = {}
        self._pairs = {}
        self._from_parent = {}
        self._direct_parents = None
