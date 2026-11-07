"""A model object that is its graph node.

Callers keep appending to the same lists. Appending records the edge.
Pass a graph the same way you pass another model.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterable, Iterator, Optional

from harness.graph.graph import EdgeType, Graph, Node, Source

# The file a new model object names until a loader tells it which file it came from.
NO_SOURCE_FILE = "."


class ModelChildren(list):
    """The list callers already append to. Appending records the graph edge."""

    def __init__(self, owner: "ModelNode", kind: str) -> None:
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


class ModelWithoutPractice(TypeError):
    """A model object class that names no practice, so the graph cannot tell which practice graph it belongs to."""

    def __init__(self, model_class: type) -> None:
        super().__init__(f"{model_class.__name__} names no practice: set _graph_practice on it or a base class.")
        self.model_class = model_class


class ModelNode(Node):
    """Base model object for one practice. Subclasses name the practice and the belongsTo pairs."""

    _graph_practice: str = ""
    _semantic_type_name: str = "Node"
    _belongs: set[tuple[str, str]] = set()
    _schema_edge_fields: frozenset[str] = frozenset({"source", "collaborators", "dependencies", "type_hint", "return_type", "callees"})
    """Attributes whose new value can add or remove a schema edge; assigning one rebuilds the graph's schema edges."""

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
        if not type(self)._graph_practice:
            raise ModelWithoutPractice(type(self))
        graph = graph or Graph()
        practice = graph.practice(type(self)._graph_practice)
        if practice.root_node.node_id not in practice.by_id:
            practice.by_id[practice.root_node.node_id] = practice.root_node
        semantic = type(self)._semantic_type_name
        self._child_lists: list[ModelChildren] = []
        Node.__init__(
            self,
            practice,
            semantic,
            practice.unused_node_id(semantic, name),
            name,
            Source(NO_SOURCE_FILE, sequential_order or 1, sequential_order or 1),
        )
        self.sequential_order = sequential_order
        practice.node_types.add(semantic)
        practice.nodes.setdefault(semantic, []).append(self)
        practice.by_id[self.node_id] = self
        self._ready = False

    @property
    def has_source_file(self) -> bool:
        """True once a loader has given this object the file it came from; until then its source only holds a placeholder."""
        return str(getattr(self.source, "file", "") or "") not in ("", NO_SOURCE_FILE)

    @property
    def node(self) -> "ModelNode":
        """This object is its graph node."""
        return self

    @property
    def graph(self) -> Graph:
        return self.practice.graph

    def semantic_type(self) -> str:
        return self._semantic_type_name

    def _link(self, child, kind: str) -> None:
        if not isinstance(child, ModelNode) or child is self:
            return
        self._adopt(child)
        child.parent = self
        self.practice.record(EdgeType.from_kind(kind), self, child)
        if (child.semantic_type(), self.semantic_type()) in type(self)._belongs:
            self.practice.record(EdgeType.from_kind("belongsTo", "relationship"), child, self)
        self._sync_schema_edges()

    def _unlink(self, child, kind: str) -> None:
        if not isinstance(child, ModelNode):
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

    def _refill(self, children: ModelChildren, incoming: Iterable) -> None:
        for child in list(children):
            self._unlink(child, children.kind)
        children.clear()
        for child in incoming:
            children.append(child)

    def _adopt(self, child: "ModelNode") -> None:
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
        with schema_sync_paused():
            for node in subtree:
                node._move_to(self.practice)
        for edge in carried:
            self.practice.record(EdgeType(edge.kind, edge.order, edge.display), edge.parent, edge.child)

    def _move_to(self, practice) -> None:
        if self.practice is practice:
            return
        node_id = practice.unused_node_id(self.type, self.name) if self.node_id in practice.by_id else self.node_id
        # add places a parsed node at its lines; a bound object keeps the source it already has, whatever its kind.
        source = self.source
        practice.add(self, node_id, NO_SOURCE_FILE, 1, 1)
        self.source = source

    def _subtree(self) -> list["ModelNode"]:
        found: list[ModelNode] = [self]
        for children in list(self._child_lists):
            for child in list(children):
                if isinstance(child, ModelNode):
                    found.extend(child._subtree())
        examples = getattr(self, "examples", None)
        if isinstance(examples, dict):
            for example in examples.values():
                if isinstance(example, ModelNode):
                    found.extend(example._subtree())
        return found

    def __setattr__(self, name: str, value) -> None:
        object.__setattr__(self, name, value)
        if name in type(self)._schema_edge_fields and getattr(self, "_ready", False):
            self._sync_schema_edges()

    @contextmanager
    def batch_schema_sync(self) -> Iterator[None]:
        """Hold schema-edge rebuilds on this object's graph until a batch of child links is finished."""
        with self.graph.schema_sync_held():
            yield

    def _sync_schema_edges(self) -> None:
        if _SCHEMA_SYNC_PAUSED[0] > 0:
            return
        graph = getattr(getattr(self, "practice", None), "graph", None)
        if graph is not None:
            graph.sync_schema_edges()

    def _copies_on_graph(self, semantic: str) -> list:
        return [
            node
            for node in self.practice.nodes.get(semantic, [])
            if node is not self and isinstance(node, ModelNode)
        ]


# How many schema_sync_paused blocks are open; rebuilds resume when the outermost one closes.
_SCHEMA_SYNC_PAUSED = [0]


@contextmanager
def schema_sync_paused() -> Iterator[None]:
    """Skip schema-edge rebuilds on every graph while transient models are parsed.

    A working-copy load parses each file into model nodes only to read their facts;
    rebuilding schema edges on each append is quadratic per file and the edges are discarded.
    Blocks nest: an inner block closing leaves the outer block's pause in place.
    """
    _SCHEMA_SYNC_PAUSED[0] += 1
    try:
        yield
    finally:
        _SCHEMA_SYNC_PAUSED[0] -= 1
