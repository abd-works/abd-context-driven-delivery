"""A model object that is its graph node.

Callers keep appending to the same lists. Appending records the edge.
Pass a graph the same way you pass another model.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Callable, Iterable, Iterator, Optional

from harness.graph.edge import EdgeType
from harness.graph.graph import Graph, Node, Source

# The file a new model object names until a loader tells it which file it came from.
NO_SOURCE_FILE = "."


class _RecordedList(list):
    """A list on a model object whose every change records or drops the owner's edge of one kind to the item."""

    def __init__(self, owner: "ModelNode", kind: str) -> None:
        super().__init__()
        self.owner = owner
        self.kind = kind

    def append(self, item) -> None:
        list.append(self, item)
        self._record(item)

    def extend(self, items: Iterable) -> None:
        for item in items:
            self.append(item)

    def insert(self, index: int, item) -> None:
        list.insert(self, index, item)
        self._record(item)

    def pop(self, index: int = -1):
        item = list.pop(self, index)
        self._drop(item)
        return item

    def __setitem__(self, index, item) -> None:
        if isinstance(index, slice):
            self.refill(list(item))
            return
        list.__setitem__(self, index, item)
        self._record(item)

    def refill(self, incoming: Iterable) -> None:
        """Hold exactly incoming from now on, dropping the edge to each item held before."""
        for item in list(self):
            self._drop(item)
        self.clear()
        for item in incoming:
            self.append(item)

    def _record(self, item) -> None:
        raise NotImplementedError

    def _drop(self, item) -> None:
        raise NotImplementedError


class ModelChildren(_RecordedList):
    """The list of the parts an owner is made of. Appending a part makes the owner its parent and records the edge."""

    def __init__(self, owner: "ModelNode", kind: str) -> None:
        super().__init__(owner, kind)
        owner._child_lists.append(self)

    def _record(self, child) -> None:
        self.owner._link(child, self.kind)

    def reconcile(self, sources: Iterable, load: Callable) -> None:
        """Become sources, in their order, keeping the children already held: each source is translated into the child
        of the same name, else the one at the same place, and a source no child matches is loaded as a new child. A
        child no source matches is dropped. Keeping the matched child keeps what only this format knows about it, such
        as a card's position on a diagram."""
        consumed: set[int] = set()
        reconciled = []
        for source in sources:
            match = self._match(source, consumed)
            if match is None:
                match = load(source)
            else:
                consumed.add(id(match))
            match.translate_from(source)
            reconciled.append(match)
        self.refill(reconciled)

    def _match(self, source, consumed: set[int]):
        free = [child for child in self if id(child) not in consumed]
        return next((child for child in free if child.name == source.name), None) or next(
            (child for child in free if child.sequential_order == source.sequential_order), None
        )

    def _drop(self, child) -> None:
        self.owner._unlink(child, self.kind)


class ModelReferences(_RecordedList):
    """The list of model objects an owner refers to without owning them, such as the stories an increment delivers,
    which stay under their own epic. Appending records a relationship edge; the object keeps its parent."""

    def __init__(self, owner: "ModelNode", kind: str) -> None:
        super().__init__(owner, kind)
        owner._reference_lists.append(self)

    def _record(self, target) -> None:
        self.owner._refer(target, self.kind)

    def _drop(self, target) -> None:
        self.owner._unlink(target, self.kind)

    def record_all(self) -> None:
        """Record the edge to every object held, as on a graph the owner has just moved to."""
        for target in self:
            self._record(target)


class ModelWithoutPractice(TypeError):
    """A model object class no practice registered, so the graph cannot tell which practice graph it belongs to."""

    def __init__(self, model_class: type) -> None:
        super().__init__(f"{model_class.__name__} names no practice: its practice's module registers itself with register_practice on it or a base class.")
        self.model_class = model_class


class ModelDetached(LookupError):
    """A model object no practice holds was asked for its graph. A parser's objects belong to no graph until the
    practice it reads for adopts them, so nothing builds a graph of its own for them."""

    def __init__(self, model: "ModelNode") -> None:
        super().__init__(f"{type(model).__name__} {model.name!r} belongs to no graph: no practice has adopted it")
        self.model = model


class ModelNode(Node):
    """Base model object for one practice. Its practice registers it (``register_practice``), and subclasses name the
    belongsTo pairs.

    An object made without a graph is detached: it belongs to no practice yet and records no edge. It joins a graph,
    with its whole tree, when a practice adopts it (``join``) or an owner on a graph takes it as a part; only then are
    the edges its lists hold recorded, so parsing a file into objects builds no graph. Asking a detached object for its
    graph raises ``ModelDetached``."""

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

    _practice_class: type | None = None
    """The practice class registered for this model class and its subclasses; see ``register_practice``."""

    @classmethod
    def register_practice(cls, practice_class: type) -> None:
        """Make practice_class the practice of this model class and of every subclass that registers none of its own.
        A practice's module calls it on its model's base class when it is imported, so the model never imports its
        practice and the dependency runs one way, from the practice to its model."""
        cls._practice_class = practice_class

    @classmethod
    def practice_kind(cls) -> type:
        """The class of the practice this object's graph node belongs to, such as ``Stories``: the one registered for
        this class or the nearest base class that has one."""
        if cls._practice_class is None:
            raise ModelWithoutPractice(cls)
        return cls._practice_class

    def __init__(self, name: str, sequential_order: int, graph: Optional[Graph] = None) -> None:
        self._child_lists: list[ModelChildren] = []
        self._reference_lists: list[ModelReferences] = []
        Node.__init__(
            self,
            None,
            type(self)._semantic_type_name,
            "",
            name,
            Source(NO_SOURCE_FILE, sequential_order or 1, sequential_order or 1),
        )
        self.sequential_order = sequential_order
        self._ready = False
        if graph is not None:
            self.join(graph.practice_of(type(self).practice_kind()))


    @property
    def graph(self) -> Graph:
        """The graph that holds this object: its practice's. ``ModelDetached`` for an object no practice holds yet,
        since a detached object belongs to no graph until a practice adopts it (``join``)."""
        if self.practice is None:
            raise ModelDetached(self)
        return self.practice.reading.graph

    @property
    def has_source_file(self) -> bool:
        """True once a loader has given this object the file it came from; until then its source only holds a placeholder."""
        return str(getattr(self.source, "file", "") or "") not in ("", NO_SOURCE_FILE)

    @property
    def node(self) -> "ModelNode":
        """This object is its graph node."""
        return self

    def semantic_type(self) -> str:
        return self._semantic_type_name

    def _link(self, child, kind: str) -> None:
        if not isinstance(child, ModelNode) or child is self:
            return
        child.parent = self
        if self.practice is None:
            # A detached owner records its edges when its tree joins a graph.
            return
        if child.practice is not self.practice:
            child.join(self.practice)
        self._record_child_edge(child, kind)
        self._sync_schema_edges()

    def _record_child_edge(self, child: "ModelNode", kind: str) -> None:
        self.graph.record(EdgeType.from_kind(kind), self, child)
        if (child.semantic_type(), self.semantic_type()) in type(self)._belongs:
            self.graph.record(EdgeType.from_kind("belongsTo", "relationship"), child, self)

    def _unlink(self, child, kind: str) -> None:
        if not isinstance(child, ModelNode) or self.practice is None:
            return
        self.practice.reading.in_graph.drop_edges(lambda edge: (edge.parent is self and edge.child is child and edge.kind == kind)
            or (edge.parent is child and edge.child is self and edge.kind == "belongsTo"),)

    def _refer(self, target, kind: str) -> None:
        """Record a relationship edge of kind to target when both are on one graph; an owner that joins another graph
        records it there (``_join``)."""
        if not isinstance(target, ModelNode) or target is self or self.practice is None or target.practice is None:
            return
        if target.graph is self.graph:
            self.graph.record(EdgeType.from_kind(kind, "relationship"), self, target)

    def join(self, practice) -> None:
        """Make this object and its whole tree practice's nodes, as a practice does with the objects its parser made:
        each leaves the graph it was in, carrying the edges between them, and the edges its own lists hold are recorded
        in practice's graph."""
        subtree = self.subtree()
        members = {id(node) for node in subtree}
        carried = []
        for held in {id(node.practice): node.practice for node in subtree if node.practice is not None}.values():
            carried.extend(held.reading.in_graph.drop_edges(lambda edge: id(edge.parent) in members and id(edge.child) in members))
        with schema_sync_paused():
            for node in subtree:
                node._move_to(practice)
        graph = practice.reading.graph
        for edge in carried:
            graph.record(EdgeType(edge.kind, edge.order, edge.display), edge.parent, edge.child)
        for node in subtree:
            node._record_held_edges()

    def _record_held_edges(self) -> None:
        """Record the edge to each part and each reference this object's lists hold."""
        for children in self._child_lists:
            for child in children:
                if isinstance(child, ModelNode) and child is not self:
                    self._record_child_edge(child, children.kind)
        for references in self._reference_lists:
            references.record_all()

    def _move_to(self, practice) -> None:
        if self.practice is practice:
            return
        unnamed = not self.node_id or practice.reading.in_graph.holds(self.node_id)
        node_id = practice.reading.in_graph.unused_node_id(self.type, self.name) if unnamed else self.node_id
        # add places a parsed node at its lines; a bound object keeps the source it already has, whatever its kind.
        source = self.source
        practice.reading.in_graph.add(self, node_id, NO_SOURCE_FILE, 1, 1)
        self.source = source

    def subtree(self) -> list["ModelNode"]:
        found: list[ModelNode] = [self]
        for children in list(self._child_lists):
            for child in list(children):
                if isinstance(child, ModelNode):
                    found.extend(child.subtree())
        examples = getattr(self, "examples", None)
        if isinstance(examples, dict):
            for example in examples.values():
                if isinstance(example, ModelNode):
                    found.extend(example.subtree())
        return found

    def __setattr__(self, name: str, value) -> None:
        object.__setattr__(self, name, value)
        if name in type(self)._schema_edge_fields and getattr(self, "_ready", False):
            self._sync_schema_edges()

    @contextmanager
    def batch_schema_sync(self) -> Iterator[None]:
        """Hold schema-edge rebuilds on this object's graph until a batch of child links is finished. A detached object
        records no edge, so there is nothing to hold."""
        if self.practice is None:
            yield
            return
        with self.graph.schema_sync_held():
            yield

    def _sync_schema_edges(self) -> None:
        if _SCHEMA_SYNC_PAUSED[0] > 0:
            return
        practice = getattr(self, "practice", None)
        graph = practice.reading.graph if practice is not None else None
        if graph is not None:
            graph.sync_schema_edges()


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
