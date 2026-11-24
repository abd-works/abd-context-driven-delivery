"""The node types of one practice as the graph's shared tables ask them: the part of a practice's reading that answers
which relationships a node's evidence decides and whether one holds, and which of its types a session's stories scope;
and the tables every graph reads, joined from what each practice and pattern registered with the process says of its
own types."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness.annotations.class_registry import ClassRegistry
    from harness.graph.model_node import ModelNode
    from harness.guidance.guidance import PracticeGuidance
    from harness.guidance.practice_catalogue import PracticeCatalogue


class PracticeNodeTypes:
    """What one practice says of its node types to the graph: the schema keys whose node type is not the key
    capitalised (``schema_node_types``), the relationships its model objects record as child lists (``child_lists``),
    where each of its edge kinds' groups sits under a node in the explorer tree (``edge_order``), the relationships whose
    edges a node's evidence decides, such as a step that ``invokes`` the operation its source calls
    (``evidence_kinds``), whether one holds between two nodes (``links``), and the types whose nodes a session's stories
    scope (``scope_types``), which a validate of a session working on some stories leaves out when they lie outside
    those stories. A practice's reading holds one (``PracticeReading.types``), and so does a pattern's overlay
    (``GraphOverlay.types``); one that names none takes this, which adds nothing to the tables, decides no relationship
    by evidence and scopes nothing by stories. Every other relationship a schema names is the nodes the owner holds in
    the list named for it."""

    schema_node_types: dict[str, str] = {}
    """Schema keys whose node type is not the key capitalised, such as ``class`` for ``OoadClass``, in the order the
    reverse lookup reads them: the first key naming a node type is the one it is written as."""

    child_lists: frozenset[str] = frozenset()
    """The relationships a model object of the practice records itself as one of its child lists."""

    edge_order: dict[str, int] = {}
    """Where each edge kind of the practice has its group under a node in the explorer tree, lowest first. ``graph.json``
    saves the number on each edge, so a kind keeps its number, and two practices that name one kind give it the same."""

    evidence_kinds: frozenset[str] = frozenset()
    """The relationships a node of the practice is linked by from its evidence: its source text, the names it calls,
    and its type hints."""

    scope_types: frozenset[str] = frozenset()
    """The node types a session that names its stories scopes: a node of one of these that lies outside every story the
    session names is another increment's work."""

    def links(self, owner: ModelNode, kind: str, target: ModelNode) -> bool:
        """Whether owner, one of the practice's nodes, is linked to target by kind, one of ``evidence_kinds``, as its
        evidence shows; never, unless the practice says."""
        return False


class GraphNodeTypes(PracticeNodeTypes):
    """The edge kinds the graph records itself, whichever practices it holds: a practice's root (``root``), what a node
    owns (``owns``), a folder's relative (``relative``), and the back-edge of every child list (``belongsTo``)."""

    child_lists = frozenset({"belongsTo"})
    edge_order = {"relative": 1, "root": 1, "owns": 2, "belongsTo": 5}


class NodeTypeTablesDisagree(ValueError):
    """Two practices or patterns give one edge kind two places in the explorer tree, or one schema key two node types.
    A saved graph keeps each edge's place, so the tables refuse rather than choose one."""

    def __init__(self, table: str, name: str, held: object, given: object) -> None:
        super().__init__(f"{table} gives {name!r} both {held!r} and {given!r}; give it one, in every practice and pattern that names it")
        self.name = name


class NodeTypeTables:
    """The node type tables every graph reads: the edge kinds the graph records itself (*GraphNodeTypes*), joined with
    what each practice registered with the process (``PRACTICE_CATALOGUE``) says through its reading, and each pattern
    registered (``REGISTERED_PATTERNS``) through its overlay. The framework names no practice and no pattern: each says
    its own, and the tables are joined again whenever the registered practices or patterns change. The process holds one
    (``NODE_TYPE_TABLES``), as it holds one catalogue of practices; a caller that joins others hands their catalogue and
    registry of patterns in, as a spec does."""

    def __init__(self, practices: PracticeCatalogue | None = None, patterns: ClassRegistry[PracticeGuidance] | None = None) -> None:
        self._practices = practices
        self._patterns = patterns
        self._joined_for: tuple[tuple[type, ...], tuple[type, ...]] | None = None
        self._schema_node_types: dict[str, str] = {}
        self._child_lists: frozenset[str] = frozenset()
        self._edge_order: dict[str, int] = {}

    def node_type_of(self, key: str) -> str | None:
        """The node type a schema key names when it is not the key capitalised; none when it is."""
        self._join()
        return self._schema_node_types.get(key)

    def key_of(self, node_type: str) -> str | None:
        """The first schema key that names node_type; none when node_type is a key capitalised."""
        self._join()
        return next((key for key, named in self._schema_node_types.items() if named == node_type), None)

    def is_child_list(self, kind: str) -> bool:
        """Whether kind is a relationship a model object records itself as one of its child lists."""
        self._join()
        return kind in self._child_lists

    def order_of(self, kind: str) -> int | None:
        """Where kind's group sits under a node in the explorer tree; none for a kind no practice or pattern places."""
        self._join()
        return self._edge_order.get(kind)

    def _join(self) -> None:
        """Join the tables of every registered practice and pattern, when those registered differ from the last join."""
        from harness.graph.pattern_overlays import REGISTERED_PATTERNS, PatternOverlays

        patterns = self._patterns if self._patterns is not None else REGISTERED_PATTERNS
        registered = (self._registered_practices(), patterns.classes)
        if registered == self._joined_for:
            return
        parts = [GraphNodeTypes(), *(practice.reading_type.types for practice in registered[0] if practice.reading_type is not None)]
        parts += [overlay.types for overlay in PatternOverlays(registered=patterns).every_graph_overlay]
        self._schema_node_types, child_lists, self._edge_order = {}, set(), {}
        for part in parts:
            self._take(part, child_lists)
        self._child_lists = frozenset(child_lists)
        self._joined_for = registered

    def _registered_practices(self) -> tuple[type, ...]:
        """The practices registered with the process; none before a package registers them, as in a spec of the
        framework alone, whose graph then reads only the tables the graph and the patterns give."""
        from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE, PracticesNotRegistered

        try:
            return (self._practices or PRACTICE_CATALOGUE).practice_classes
        except PracticesNotRegistered:
            return ()

    def _take(self, part: PracticeNodeTypes, child_lists: set[str]) -> None:
        """Add what part says to the tables being joined; *NodeTypeTablesDisagree* when it places a kind or names a key
        otherwise than a part before it."""
        for key, node_type in part.schema_node_types.items():
            if self._schema_node_types.setdefault(key, node_type) != node_type:
                raise NodeTypeTablesDisagree("the schema keys", key, self._schema_node_types[key], node_type)
        for kind, order in part.edge_order.items():
            if self._edge_order.setdefault(kind, order) != order:
                raise NodeTypeTablesDisagree("the edge order", kind, self._edge_order[kind], order)
        child_lists.update(part.child_lists)


NODE_TYPE_TABLES = NodeTypeTables()
"""The process's one set of node type tables, joined from the practices and patterns registered with it."""
