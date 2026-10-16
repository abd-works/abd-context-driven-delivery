"""A model object that is its graph node.

Callers keep appending to the same lists. Appending records the edge.
Pass a graph the same way you pass another model.
"""

from __future__ import annotations

from typing import Iterable, Optional

from harness.graph.graph import Graph, Node, Source
from harness.graph.schema_edges import sync_schema_edges


class BoundChildren(list):
    """The list callers already append to. Appending records the graph edge."""

    def __init__(self, owner: "BoundNode", kind: str) -> None:
        super().__init__()
        self.owner = owner
        self.kind = kind
        owner._child_lists.append(self)

    def append(self, child) -> None:
        list.append(self, child)
        self.owner._link(child, self.kind)

    def extend(self, children: Iterable) -> None:
        for child in children:
            self.append(child)

    def insert(self, index: int, child) -> None:
        list.insert(self, index, child)
        self.owner._link(child, self.kind)

    def pop(self, index: int = -1):
        child = list.pop(self, index)
        self.owner._unlink(child, self.kind)
        return child

    def __setitem__(self, index, child) -> None:
        if isinstance(index, slice):
            self.owner._refill(self, list(child))
            return
        list.__setitem__(self, index, child)
        self.owner._link(child, self.kind)


class BoundNode(Node):
    """Base model object for one practice. Subclasses name the practice and the belongsTo pairs."""

    _graph_practice: str = "stories"
    _semantic_type_name: str = "Node"
    _belongs: set[tuple[str, str]] = set()
    _edge_order: dict[str, int] = {
        "belongsTo": 8,
        "participants": 1,
        "parameters": 2,
        "screens": 1,
        "descriptions": 1,
        "contexts": 2,
        "observations": 3,
        "aggregates": 2,
        "invokes": 5,
        "invokedBy": 6,
        "observes": 8,
        "demonstrates": 3,
        "demonstratedThrough": 6,
        "retrievedUsing": 7,
        "uses": 9,
        "usedBy": 9,
        "shownOn": 4,
        "specifiedBy": 4,
        "ands": 9,
    }

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        init = cls.__dict__.get("__init__")
        if init is None or getattr(init, "_schema_wrapped", False):
            return

        def wrapped(self, *args, **kw):
            init(self, *args, **kw)
            self._ready = True
            self._sync_schema_edges()

        wrapped._schema_wrapped = True
        cls.__init__ = wrapped

    def __init__(self, name: str, sequential_order: int, graph: Optional[Graph] = None) -> None:
        graph = graph or Graph()
        practice_name = type(self)._graph_practice
        practice = graph.practice(practice_name)
        if practice.root_node.node_id not in practice.by_id:
            practice.by_id[practice.root_node.node_id] = practice.root_node
        semantic = type(self)._semantic_type_name
        self._child_lists: list[BoundChildren] = []
        Node.__init__(
            self,
            practice,
            semantic,
            _node_id(practice, semantic, name),
            name,
            Source(".", sequential_order or 1, sequential_order or 1),
        )
        self.sequential_order = sequential_order
        practice.node_types.add(semantic)
        practice.nodes.setdefault(semantic, []).append(self)
        practice.by_id[self.node_id] = self
        self._ready = False

    @property
    def node(self) -> "BoundNode":
        """This object is its graph node."""
        return self

    @property
    def graph(self) -> Graph:
        return self.practice.graph

    def semantic_type(self) -> str:
        return self._semantic_type_name

    def _link(self, child, kind: str) -> None:
        if not isinstance(child, BoundNode) or child is self:
            return
        self._adopt(child)
        child.parent = self
        self.practice.record(
            {"kind": kind, "order": self._order(kind), "display": "direct"},
            self,
            child,
        )
        if (child.semantic_type(), self.semantic_type()) in type(self)._belongs:
            self.practice.record(
                {"kind": "belongsTo", "order": self._order("belongsTo"), "display": "relationship"},
                child,
                self,
            )
        self._sync_schema_edges()

    def _unlink(self, child, kind: str) -> None:
        if not isinstance(child, BoundNode):
            return
        practice = self.practice
        for edge_kind, listed in list(practice.edges.items()):
            practice.edges[edge_kind] = [
                edge
                for edge in listed
                if not (
                    (edge.parent is self and edge.child is child and edge.kind == kind)
                    or (edge.parent is child and edge.child is self and edge.kind == "belongsTo")
                )
            ]

    def _refill(self, children: BoundChildren, incoming: Iterable) -> None:
        for child in list(children):
            self._unlink(child, children.kind)
        children.clear()
        for child in incoming:
            children.append(child)

    def _adopt(self, child: "BoundNode") -> None:
        if child.practice is self.practice:
            return
        subtree = child._subtree()
        members = set(subtree)
        old = child.practice
        carried = []
        for kind, listed in list(old.edges.items()):
            kept = []
            for edge in listed:
                if edge.parent in members and edge.child in members:
                    carried.append(edge)
                else:
                    kept.append(edge)
            old.edges[kind] = kept
        for node in subtree:
            node._move_to(self.practice)
        for edge in carried:
            self.practice.record(
                {"kind": edge.kind, "order": edge.order, "display": edge.display},
                edge.parent,
                edge.child,
            )

    def _move_to(self, practice) -> None:
        if self.practice is practice:
            return
        old = self.practice
        old.by_id.pop(self.node_id, None)
        bucket = old.nodes.get(self.type, [])
        if self in bucket:
            bucket.remove(self)
        if self.node_id in practice.by_id and practice.by_id[self.node_id] is not self:
            self.node_id = _node_id(practice, self.type, self.name)
        self.practice = practice
        practice.by_id[self.node_id] = self
        practice.nodes.setdefault(self.type, []).append(self)
        practice.node_types.add(self.type)

    def _subtree(self) -> list["BoundNode"]:
        found: list[BoundNode] = [self]
        for children in list(self._child_lists):
            for child in list(children):
                if isinstance(child, BoundNode):
                    found.extend(child._subtree())
        examples = getattr(self, "examples", None)
        if isinstance(examples, dict):
            for example in examples.values():
                if isinstance(example, BoundNode):
                    found.extend(example._subtree())
        return found

    def __setattr__(self, name: str, value) -> None:
        object.__setattr__(self, name, value)
        if name in {"source", "story_names", "collaborators", "dependencies", "type_hint", "return_type", "callees"} and getattr(self, "_ready", False):
            self._sync_schema_edges()

    def _sync_schema_edges(self) -> None:
        graph = getattr(self, "practice", None)
        graph = getattr(graph, "graph", None)
        if graph is None or getattr(graph, "_syncing_schema", False):
            return
        graph._syncing_schema = True
        try:
            sync_schema_edges(graph)
        finally:
            graph._syncing_schema = False

    def _order(self, kind: str) -> int:
        return type(self)._edge_order.get(kind, 1)

    def _copies_on_graph(self, semantic: str) -> list:
        return [
            node
            for node in self.practice.nodes.get(semantic, [])
            if node is not self and isinstance(node, BoundNode)
        ]


def _node_id(practice, semantic: str, name: str) -> str:
    base = f"{practice.name}:{semantic}:{name}"
    if base not in practice.by_id:
        return base
    index = 2
    while f"{base}:{index}" in practice.by_id:
        index += 1
    return f"{base}:{index}"
