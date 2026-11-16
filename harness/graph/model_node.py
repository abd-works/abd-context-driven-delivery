"""A model object that is its graph node.

Callers keep appending to the same lists. Appending records the edge.
Pass a graph the same way you pass another model.
"""

from __future__ import annotations

from abc import ABCMeta
from contextlib import contextmanager
from typing import TYPE_CHECKING, Callable, ClassVar, Iterable, Iterator, Optional

from harness.graph.edge import EdgeType
from harness.graph.graph import Graph, Node, Source
from harness.graph.saved_graph import NodeIdentity
from harness.graph.location import Location

if TYPE_CHECKING:
    from harness.guidance.guidance import PracticeGuidance

# The file a new model object names until a loader tells it which file it came from.
NO_SOURCE_FILE = "."


class _RecordedList(list):
    """A list on a model object whose every change records or drops the owner's edge of one kind to the item."""

    def __init__(self, owner: "ModelNode", kind: str) -> None:
        super().__init__()
        self.owner = owner
        self.kind = kind
        owner.keeps_list(self)

    def append(self, held: ModelNode) -> None:
        list.append(self, held)
        self._record(held)

    def extend(self, incoming: Iterable[ModelNode]) -> None:
        for held in incoming:
            self.append(held)

    def insert(self, index: int, held: ModelNode) -> None:
        list.insert(self, index, held)
        self._record(held)

    def pop(self, index: int = -1) -> ModelNode:
        held = list.pop(self, index)
        self._drop(held)
        return held

    def __setitem__(self, index: int | slice, held: ModelNode | Iterable[ModelNode]) -> None:
        if isinstance(index, slice):
            self.refill(list(held))
            return
        list.__setitem__(self, index, held)
        self._record(held)

    def refill(self, incoming: Iterable[ModelNode]) -> None:
        """Hold exactly incoming from now on, dropping the edge to each object held before."""
        for held in list(self):
            self._drop(held)
        self.clear()
        for held in incoming:
            self.append(held)

    def _record(self, held: ModelNode) -> None:
        raise NotImplementedError

    def _drop(self, held: ModelNode) -> None:
        """Drop the owner's edge of this list's kind to held, and the belongsTo edge back from held."""
        owner = self.owner
        if not isinstance(held, ModelNode) or owner.practice is None:
            return
        kind = self.kind
        owner.practice.reading.in_graph.edge_index.drop(lambda edge: (edge.parent is owner and edge.child is held and edge.kind == kind)
            or (edge.parent is held and edge.child is owner and edge.kind == "belongsTo"))


class ModelChildren(_RecordedList):
    """The list of the parts an owner is made of. Appending a part makes the owner its parent and records the edge."""

    def _record(self, child: ModelNode) -> None:
        self.owner.attach(child, self.kind)

    def reconcile(self, sources: Iterable[ModelNode], load: Callable[[ModelNode], ModelNode]) -> None:
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

    def _match(self, source: ModelNode, consumed: set[int]) -> ModelNode | None:
        free = [child for child in self if id(child) not in consumed]
        return next((child for child in free if child.name == source.name), None) or next(
            (child for child in free if child.sequential_order == source.sequential_order), None
        )


class ModelReferences(_RecordedList):
    """The list of model objects an owner refers to without owning them, such as the stories an increment delivers,
    which stay under their own epic. Appending records a relationship edge; the object keeps its parent."""

    def _record(self, target: ModelNode) -> None:
        """Record a relationship edge of this list's kind to target when the owner and target are on one graph; an
        owner that joins another graph records it there."""
        owner = self.owner
        if not isinstance(target, ModelNode) or target is owner or owner.practice is None or target.practice is None:
            return
        if target.graph is owner.graph:
            owner.graph.edges.record(EdgeType.from_kind(self.kind, "relationship"), owner, target)

    def record_all(self) -> None:
        """Record the edge to every object held, as on a graph the owner has just moved to."""
        for target in self:
            self._record(target)


class ModelWithoutPractice(TypeError):
    """A model object class no practice registered, so the graph cannot tell which practice graph it belongs to."""

    def __init__(self, model_class: type) -> None:
        super().__init__(f"{model_class.__name__} names no practice: its practice's module sets itself as the practice_class of it or a base class.")
        self.model_class = model_class


class ModelDetached(LookupError):
    """A model object no practice holds was asked for its graph. A parser's objects belong to no graph until the
    practice it reads for adopts them, so nothing builds a graph of its own for them."""

    def __init__(self, model: "ModelNode") -> None:
        super().__init__(f"{type(model).__name__} {model.name!r} belongs to no graph: no practice has adopted it")
        self.model = model


class _SyncedOnceBuilt(ABCMeta):
    """Makes a model object ready once its whole constructor has run, the subclass's included, and then records the
    schema edges its fields name: an assignment made while it is still being built rebuilds none of them. It derives
    from *ABCMeta* so a model class may also be abstract."""

    def __call__(cls, *args: object, **kwargs: object) -> ModelNode:
        model = super().__call__(*args, **kwargs)
        model.finish_building()
        return model


class ModelNode(Node, metaclass=_SyncedOnceBuilt):
    """Base model object for one practice. Its practice names itself on it (``practice_class``), and subclasses name the
    belongsTo pairs.

    An object made without a graph is detached: it belongs to no practice yet and records no edge. It joins a graph,
    with its whole tree, when a practice adopts it (``join``) or an owner on a graph takes it as a part; only then are
    the edges its lists hold recorded, so parsing a file into objects builds no graph. Asking a detached object for its
    graph raises ``ModelDetached``."""

    _semantic_type_name: str = "Node"
    _belongs: set[tuple[str, str]] = set()
    _schema_edge_fields: frozenset[str] = frozenset({"source", "collaborators", "dependencies", "type_hint", "return_type", "callees"})
    """Attributes whose new value can add or remove a schema edge; assigning one rebuilds the graph's schema edges."""

    practice_class: ClassVar[type | None] = None
    """The practice of this model class and of every subclass that names none of its own, such as ``Stories``. A
    practice's module sets it on its model's base class when it is imported (``StoryNode.practice_class = Stories``),
    so the model never imports its practice and the dependency runs one way, from the practice to its model."""

    @property
    def practice_kind(self) -> type:
        """The class of the practice this object's graph node belongs to: its class's ``practice_class``, or the nearest
        base class's. ``ModelWithoutPractice`` when none names one."""
        if self.practice_class is None:
            raise ModelWithoutPractice(type(self))
        return self.practice_class

    def __init__(self, name: str, sequential_order: int, graph: Optional[Graph] = None) -> None:
        self._child_lists: list[ModelChildren] = []
        self._reference_lists: list[ModelReferences] = []
        Node.__init__(
            self,
            None,
            NodeIdentity(type=type(self)._semantic_type_name, node_id="", name=name),
            Source(NO_SOURCE_FILE, sequential_order or 1, sequential_order or 1),
        )
        self.sequential_order = sequential_order
        self._ready = False
        if graph is not None:
            self.join(graph.practices.of(self.practice_kind))


    def finish_building(self) -> None:
        """Mark this object built, so an assignment to a field that names a schema edge rebuilds the schema edges, and
        record the ones its constructor gave it."""
        self._ready = True
        self._sync_schema_edges()

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

    def keeps_list(self, listed: ModelChildren | ModelReferences) -> None:
        """Keep listed, one of this object's lists of the parts it is made of or of the objects it refers to, so the
        object records the edge to each when it joins a graph."""
        (self._child_lists if isinstance(listed, ModelChildren) else self._reference_lists).append(listed)

    def attach(self, child: ModelNode, kind: str) -> None:
        """Make child one of this object's parts, under an edge of kind: this object becomes its parent, and on a graph
        the edge is recorded, with child joining this object's practice."""
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
        self.graph.edges.record(EdgeType.from_kind(kind), self, child)
        if (child.semantic_type(), self.semantic_type()) in type(self)._belongs:
            self.graph.edges.record(EdgeType.from_kind("belongsTo", "relationship"), child, self)

    def join(self, practice: PracticeGuidance) -> None:
        """Make this object and its whole tree practice's nodes, as a practice does with the objects its parser made:
        each leaves the graph it was in, carrying the edges between them, and the edges its own lists hold are recorded
        in practice's graph."""
        subtree = self.subtree()
        members = {id(node) for node in subtree}
        carried = []
        for held in {id(node.practice): node.practice for node in subtree if node.practice is not None}.values():
            carried.extend(held.reading.in_graph.edge_index.drop(lambda edge: id(edge.parent) in members and id(edge.child) in members))
        with schema_sync_paused():
            for node in subtree:
                node._move_to(practice)
        graph = practice.reading.graph
        for edge in carried:
            graph.edges.record(edge.type, edge.parent, edge.child)
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

    def _move_to(self, practice: PracticeGuidance) -> None:
        if self.practice is practice:
            return
        unnamed = not self.node_id or practice.reading.in_graph.holds(self.node_id)
        node_id = practice.reading.in_graph.unused_node_id(self.type, self.name) if unnamed else self.node_id
        # add places a parsed node at its lines; a bound object keeps the source it already has, whatever its kind.
        source = self.source
        practice.reading.in_graph.add(self, node_id, Location(NO_SOURCE_FILE, 1, 1))
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

    def __setattr__(self, name: str, assigned: object) -> None:
        object.__setattr__(self, name, assigned)
        if name in type(self)._schema_edge_fields and getattr(self, "_ready", False):
            self._sync_schema_edges()

    @contextmanager
    def batch_schema_sync(self) -> Iterator[None]:
        """Hold schema-edge rebuilds on this object's graph until a batch of child links is finished. A detached object
        records no edge, so there is nothing to hold."""
        if self.practice is None:
            yield
            return
        with self.graph.schema_edges.held():
            yield

    def _sync_schema_edges(self) -> None:
        if _SCHEMA_SYNC_PAUSED[0] > 0:
            return
        practice = getattr(self, "practice", None)
        graph = practice.reading.graph if practice is not None else None
        if graph is not None:
            graph.schema_edges.sync()


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
