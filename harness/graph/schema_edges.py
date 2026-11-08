"""SchemaEdges. The relationship edges every practice's ``schema.yaml`` names, recorded between the model objects on one
graph.

Child lists already record their own edge, and belongsTo is the back-edge for those lists. Every other relationship the
schema names is recorded here when both nodes are on the graph: a field read from evidence (``invokes``, ``hasType``) when
the owning object's source or names show it, and any other field when the owner holds the target in the list attribute
named for the field.
"""

from __future__ import annotations

import re
from functools import cached_property, lru_cache

from harness.graph.graph import EdgeType
from harness.guidance.schema import Schema
from harness.annotations.name import Name

# Child-list edges. A model object's child list records these itself.
_CHILD_LISTS = frozenset(
    {
        "decomposedInto",
        "background",
        "scenarios",
        "steps",
        "examples",
        "increments",
        "stories",
        "participants",
        "parameters",
        "screens",
        "descriptions",
        "contexts",
        "observations",
        "aggregates",
        "ands",
        "belongsTo",
    }
)

# The explorer leaves scopes out of the serialized graph.
_SKIPPED = _CHILD_LISTS | {"scopes"}

# Schema keys whose node type is not the key capitalised, in the order the reverse lookup reads them.
_NODE_TYPES = {
    "class": "OoadClass",
    "subEpic": "Epic",
    "given": "Step",
    "when": "Step",
    "then": "Step",
    "map": "UxMap",
    "node": "NodeRoot",
    "client": "ClientRoot",
    "share": "StoryShared",
    "server": "ServerSpec",
    "domain": "DomainSpec",
    "playwright": "PlaywrightSpec",
    "view": "DomainView",
}

_PHASES = {"given": "given", "when": "when", "then": "then"}

_DISPLAY = {"demonstrates": "grouped"}

# Fields a node's evidence decides (its source text, callees, names); every other field is the nodes it holds.
_EVIDENCE_KINDS = frozenset(
    {"invokes", "observes", "demonstrates", "retrievedUsing", "uses", "specifiedBy", "given", "dependsOn", "hasType", "returnType"}
)

# Field values that name a value type rather than another schema type.
_VALUE_TYPES = frozenset({"string", "number", "dotPath"})


class SchemaKey:
    """One type key in a ``schema.yaml`` and the explorer node type it names: ``class`` is ``OoadClass``; any other key
    is capitalised."""

    def __init__(self, key: str) -> None:
        self.key = key

    @classmethod
    def from_node_type(cls, node_type: str) -> SchemaKey:
        """The schema key an explorer node type is written as, the reverse of ``node_type``."""
        named = next((key for key, mapped in _NODE_TYPES.items() if mapped == node_type), None)
        return cls(named if named is not None else node_type[:1].lower() + node_type[1:])

    @property
    def node_type(self) -> str:
        return _NODE_TYPES.get(self.key) or self.key[:1].upper() + self.key[1:]


class SchemaField:
    """One field of a schema type whose value names other types: a relationship the owner type has with them."""

    def __init__(self, owner: str, kind: str, targets: tuple[str, ...], phase: str = "") -> None:
        self.owner = owner
        self.kind = kind
        self.targets = targets
        self.phase = phase

    def links_from(self, owner) -> bool:
        """True when this field is a relationship a node like owner records here."""
        if self.owner != owner.semantic_type() or self.kind in _SKIPPED:
            return False
        return not self.phase or owner.phase == self.phase


class SchemaFields:
    """Every relationship field in every practice's schema and every pattern's practice schemas."""

    def __init__(self, fields: tuple[SchemaField, ...]) -> None:
        self.fields = fields

    @classmethod
    @lru_cache(maxsize=1)
    def load(cls) -> SchemaFields:
        from harness.graph.pattern_overlays import PatternOverlays
        from harness.guidance.practice_catalogue import PracticeCatalogue

        schemas = [practice.schema_types for practice in PracticeCatalogue.practices()]
        for folder in PatternOverlays().pattern_folders:
            schemas.extend(Schema.load(path) for path in sorted(folder.glob("practices/*/model/schema.yaml")))
        return cls(tuple(field for schema in schemas for field in cls._fields_of(schema)))

    def inverses(self, owner_type: str, target_type: str, forward: str) -> list[str]:
        """The relationships owner_type names back to target_type, other than forward and the child lists."""
        found: list[str] = []
        for field in self.fields:
            if field.owner != owner_type or field.kind == forward or field.kind in _SKIPPED:
                continue
            if target_type in field.targets and field.kind not in found:
                found.append(field.kind)
        return found

    @classmethod
    def _fields_of(cls, schema: Schema) -> list[SchemaField]:
        found: list[SchemaField] = []
        for key, kind in schema.types.items():
            for name, value in kind.fields:
                targets = [target for target in re.findall(r"[A-Za-z]\w*", value.strip()) if target not in _VALUE_TYPES]
                if targets and '"' not in value:
                    found.append(SchemaField(SchemaKey(key).node_type, name, tuple(SchemaKey(target).node_type for target in targets), _PHASES.get(key, "")))
        return found


class NodeEvidence:
    """What a model object's source shows: the names it mentions, calls, and reads, and the module it sits in."""

    def __init__(self, node) -> None:
        self.node = node

    @cached_property
    def text(self) -> str:
        source = getattr(self.node, "source", None)
        stored = getattr(source, "__dict__", {}).get("text") if source is not None else None
        return stored if isinstance(stored, str) else ""

    @property
    def callees(self) -> list[str]:
        return list(getattr(self.node, "callees", []) or [])

    def mentions(self, name: str) -> bool:
        return bool(self.text and name) and re.search(rf"\b{re.escape(name)}\b", self.text) is not None

    def reads(self, name: str) -> bool:
        """True when the source reads a property called name: ``.name`` not followed by a call."""
        return bool(self.text and name) and re.search(rf"\.{re.escape(name)}\b(?!\s*\()", self.text) is not None

    def calls(self, name: str) -> bool:
        """True when the source, or the source of a step under it, calls name."""
        if not self.text or not name:
            return False
        text = "\n".join([self.text, *(NodeEvidence(step).text for step in self._steps_under())])
        return re.search(rf"(?<![\w]){re.escape(name)}\s*\(", text) is not None

    def invokes(self, name: str) -> bool:
        return self.calls(name) or name in self.callees

    @property
    def module(self):
        """The Module node this object sits under, through its parents; none when it sits under none."""
        current, seen = self.node, set()
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            if getattr(current, "semantic_type", lambda: "")() == "Module":
                return current
            current = getattr(current, "parent", None)
        return None

    def _steps_under(self) -> list:
        if not hasattr(self.node, "_subtree"):
            return []
        return [node for node in self.node._subtree() if node is not self.node and node.semantic_type() == "Step"]


class SchemaEdges:
    """The schema relationship edges between the model objects on one graph."""

    def __init__(self, graph) -> None:
        self.graph = graph

    @cached_property
    def nodes(self) -> list:
        """The model objects on the graph: nodes that build their own edges."""
        found = []
        for practice in self.graph.practices.values():
            found.extend(node for node in self.graph.nodes_of(practice) if hasattr(node, "semantic_type") and hasattr(node, "_subtree"))
        return found

    @cached_property
    def _by_type(self) -> dict[str, list]:
        found: dict[str, list] = {}
        for node in self.nodes:
            found.setdefault(node.semantic_type(), []).append(node)
        return found

    def sync(self) -> None:
        """Record every schema relationship edge between the model objects already on the graph."""
        if len(self.nodes) < 2:
            return
        schema = SchemaFields.load()
        for owner in self.nodes:
            for field in (field for field in schema.fields if field.links_from(owner)):
                for target in self._linked_targets(field, owner):
                    self._record(field.kind, owner, target)
                    for inverse in schema.inverses(target.semantic_type(), owner.semantic_type(), field.kind):
                        self._record(inverse, target, owner)

    def _linked_targets(self, field: SchemaField, owner) -> list:
        """The nodes owner links to through field: for a field read from evidence, the targets its evidence matches;
        for any other, the nodes owner holds in the list attribute named for the field (``showsSteps`` is ``shows_steps``)."""
        if field.kind not in _EVIDENCE_KINDS:
            held = getattr(owner, Name(field.kind).snake, None)
            if not isinstance(held, (list, tuple)):
                return []
            return [item for item in held if item is not owner and hasattr(item, "semantic_type") and item.semantic_type() in field.targets]
        targets = [target for type_name in field.targets for target in self._by_type.get(type_name, ())]
        return [target for target in targets if target is not owner and self._matches(field.kind, owner, target)]

    def _record(self, kind: str, parent, child) -> None:
        edge_type = EdgeType.from_kind(kind, _DISPLAY.get(kind, "relationship"))
        self.graph.record(edge_type, parent, child)
        if parent.practice is not child.practice:
            self.graph.record(edge_type, child, parent)

    def _matches(self, kind: str, owner, target) -> bool:
        evidence = NodeEvidence(owner)
        if kind == "invokes":
            return evidence.invokes(target.name)
        if kind in {"observes", "demonstrates"}:
            return evidence.mentions(target.name)
        if kind == "retrievedUsing":
            return evidence.reads(target.name) or evidence.calls(target.name)
        if kind == "uses":
            return self._epic_uses(owner, target)
        if kind == "specifiedBy":
            return owner.name.casefold() == target.name.casefold()
        if kind == "given":
            return target.semantic_type() == "Step" and target.phase == "given" and target in list(getattr(owner, "steps", []) or [])
        if kind == "dependsOn":
            return target.name in [*(getattr(owner, "collaborators", []) or []), *(getattr(owner, "dependencies", []) or [])]
        if kind in {"hasType", "returnType"}:
            hint = getattr(owner, "type_hint" if kind == "hasType" else "return_type", "") or ""
            return re.search(rf"\b{re.escape(target.name)}\b", str(hint)) is not None if target.name else False
        return False

    def _epic_uses(self, epic, module) -> bool:
        """True when an epic's examples name a class of the module, or its steps call one of the module's members."""
        if epic.semantic_type() != "Epic" or module.semantic_type() != "Module":
            return False
        members = [node for node in self.nodes if NodeEvidence(node).module is module]
        classes = [node for node in members if node.semantic_type() == "OoadClass"]
        operations = [node for node in members if node.semantic_type() in {"Operation", "Property"}]
        for node in epic._subtree():
            evidence = NodeEvidence(node)
            if node.semantic_type() == "Example" and any(evidence.mentions(found.name) for found in classes):
                return True
            if node.semantic_type() == "Step" and any(evidence.invokes(member.name) for member in operations):
                return True
        return False
