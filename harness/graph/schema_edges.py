"""SchemaEdges. The relationship edges every practice's ``schema.yaml`` names, recorded between the model objects on one
graph.

Child lists already record their own edge, and belongsTo is the back-edge for those lists; each practice names its own
(``PracticeNodeTypes.child_lists``). Every other relationship the schema names is recorded here when both nodes are on the graph: a field the owning object's practice reads from evidence
(``invokes``, ``hasType``) when that practice says its source or names show it (``PracticeNodeTypes.links``), and any
other field when the owner holds the target in the list attribute named for the field.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from functools import cached_property
from typing import TYPE_CHECKING

from harness.graph.edge import EdgeType
from harness.graph.practice_node_types import NODE_TYPE_TABLES
from harness.guidance.schema import Schema
from harness.annotations.name import Name

if TYPE_CHECKING:
    from harness.graph.graph import Graph
    from harness.graph.model_node import ModelNode
    from harness.graph.pattern_overlays import GraphOverlay
    from harness.guidance.guidance import PracticeGuidance


# Kinds left out of the schema edges besides the child lists: the explorer leaves scopes out of the serialized graph.
_NOT_RECORDED = frozenset({"scopes"})

_PHASES = {"given": "given", "when": "when", "then": "then"}

_DISPLAY = {"demonstrates": "grouped"}


def records(kind: str) -> bool:
    """Whether the schema edges record kind: not a child list, which its model object records itself and whose
    back-edge is belongsTo, nor a kind the explorer leaves out."""
    return not NODE_TYPE_TABLES.is_child_list(kind) and kind not in _NOT_RECORDED


class SchemaKey:
    """One type key in a ``schema.yaml`` and the explorer node type it names: the node type the practice or pattern
    whose schema names it gives (``NODE_TYPE_TABLES``), such as ``OoadClass`` for ``class``; any other key capitalised."""

    def __init__(self, key: str) -> None:
        self.key = key

    @classmethod
    def from_node_type(cls, node_type: str) -> SchemaKey:
        """The schema key an explorer node type is written as, the reverse of ``node_type``."""
        named = NODE_TYPE_TABLES.key_of(node_type)
        return cls(named if named is not None else node_type[:1].lower() + node_type[1:])

    @property
    def node_type(self) -> str:
        return NODE_TYPE_TABLES.node_type_of(self.key) or self._capitalised

    @property
    def node_types(self) -> tuple[str, ...]:
        """Every node type a node of this key may be read as: ``node_type``, and the key capitalised, which a practice's
        reading may name it instead (a story map's sub-epic is a ``SubEpic``, a given step a ``Given``)."""
        return tuple(dict.fromkeys((self.node_type, self._capitalised)))

    @property
    def _capitalised(self) -> str:
        return self.key[:1].upper() + self.key[1:]

    @property
    def phase(self) -> str:
        """The step phase the key names (``given``, ``when``, ``then``), whose nodes are steps of that phase; empty for
        any other key."""
        return _PHASES.get(self.key, "")


class SchemaField:
    """One field of a schema type whose value names other types: a relationship the owner type has with them."""

    def __init__(self, owner: SchemaKey, kind: str, targets: tuple[str, ...]) -> None:
        self.owner = owner.node_type
        self.kind = kind
        self.targets = targets
        # The step phase an owner of this field is in, for a field of one phase's steps; empty for any other owner.
        self.phase = owner.phase

    def links_from(self, owner: ModelNode) -> bool:
        """True when this field is a relationship a node like owner records here."""
        if self.owner != owner.semantic_type() or not records(self.kind):
            return False
        return not self.phase or owner.phase == self.phase


class SchemaFields:
    """Every relationship field in the schema of each practice one graph holds, and in the schema every pattern keeps
    for each of those practices, applied or not."""

    def __init__(self, schemas: list[Schema]) -> None:
        self.fields = tuple(field for schema in schemas for field in self._fields_of(schema))

    @classmethod
    def of(cls, practices: list[PracticeGuidance], overlays: list[GraphOverlay]) -> SchemaFields:
        """The fields of practices' schemas and of the schema each overlay keeps for one of them (``practice_file``)."""
        schemas = [practice.schema for practice in practices]
        pattern_files = (overlay.practice_file(practice.key, "schema.yaml") for overlay in overlays for practice in practices)
        schemas.extend(Schema.load(path) for path in sorted(path for path in pattern_files if path.is_file()))
        return cls(schemas)

    def inverses(self, owner_type: str, target_type: str, forward: str) -> list[str]:
        """The relationships owner_type names back to target_type, other than forward and the child lists."""
        found: list[str] = []
        for field in self.fields:
            if field.owner != owner_type or field.kind == forward or not records(field.kind):
                continue
            if target_type in field.targets and field.kind not in found:
                found.append(field.kind)
        return found

    def _fields_of(self, schema: Schema) -> list[SchemaField]:
        """Each relationship of each type of schema that names a type, with the node types it names."""
        return [
            SchemaField(SchemaKey(key), relationship.name, tuple(SchemaKey(target).node_type for target in relationship.targets))
            for key, kind in schema.types.items()
            for relationship in kind.relationships
            if relationship.targets
        ]


class SchemaEdges:
    """The schema relationship edges between the model objects on one graph, which the graph makes once and keeps
    (``graph.schema_edges``). It reads the schemas' relationship fields the first time it records an edge, and the model
    objects again on each sync, since the graph holds other objects by then. It syncs only while the graph is not loaded
    from a working copy, whose practices record their own edges (``syncs``), and never while a batch of links is still
    being made (``held``) or a sync is under way."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.nodes: list[ModelNode] = []
        self._by_type: dict[str, list[ModelNode]] = {}
        # Whether model objects joining the graph record their schema edges; a working copy's load turns it off.
        self.syncs = True
        self._holds = 0
        self._syncing = False

    @cached_property
    def fields(self) -> SchemaFields:
        """The relationship fields of the graph's practices and of every pattern's schemas for them."""
        return SchemaFields.of(list(self.graph.practices.held.values()), self.graph.applied_patterns.every_graph_overlay)

    @contextmanager
    def held(self) -> Iterator[None]:
        """Hold syncs until a batch of links is finished, then sync once. Each link would otherwise record every schema
        edge again, which on a story map is quadratic in the nodes already attached."""
        self._holds += 1
        try:
            yield
        finally:
            self._holds -= 1
            self.sync()

    def sync(self) -> None:
        """Record every schema relationship edge between the model objects on the graph now."""
        if not self.syncs or self._holds or self._syncing:
            return
        self._syncing = True
        try:
            self._read_nodes()
            if len(self.nodes) >= 2:
                for owner in self.nodes:
                    self._record_from(owner)
        finally:
            self._syncing = False

    def _read_nodes(self) -> None:
        """The model objects on the graph now, and by type."""
        self.nodes = [
            node for practice in self.graph.practices.opened.values() for node in practice.reading.in_graph.nodes() if hasattr(node, "semantic_type") and hasattr(node, "subtree")
        ]
        self._by_type = {}
        for node in self.nodes:
            self._by_type.setdefault(node.semantic_type(), []).append(node)

    def _record_from(self, owner: ModelNode) -> None:
        """Record each schema edge from owner, and each relationship its targets name back to it."""
        schema = self.fields
        for field in (field for field in schema.fields if field.links_from(owner)):
            for target in self._linked_targets(field, owner):
                self._record(field.kind, owner, target)
                for inverse in schema.inverses(target.semantic_type(), owner.semantic_type(), field.kind):
                    self._record(inverse, target, owner)

    def _linked_targets(self, field: SchemaField, owner: ModelNode) -> list[ModelNode]:
        """The nodes owner links to through field: for a field owner's practice reads from evidence, the targets its
        evidence links (``PracticeNodeTypes.links``); for any other, the nodes owner holds in the list attribute named
        for the field (``showsSteps`` is ``shows_steps``)."""
        types = owner.practice.reading.types
        if field.kind not in types.evidence_kinds:
            held = getattr(owner, Name(field.kind).snake, None)
            if not isinstance(held, (list, tuple)):
                return []
            return [item for item in held if item is not owner and hasattr(item, "semantic_type") and item.semantic_type() in field.targets]
        targets = [target for type_name in field.targets for target in self._by_type.get(type_name, ())]
        return [target for target in targets if target is not owner and types.links(owner, field.kind, target)]

    def _record(self, kind: str, parent: ModelNode, child: ModelNode) -> None:
        edge_type = EdgeType.from_kind(kind, _DISPLAY.get(kind, "relationship"))
        self.graph.edges.record(edge_type, parent, child)
        if parent.practice is not child.practice:
            self.graph.edges.record(edge_type, child, parent)
