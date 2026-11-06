"""Schema relationship fields recorded on the graph node.

Child lists already record their own edge. belongsTo is the back-edge for those
lists. Every other relationship the schema names is recorded here when the two
nodes are on the graph and the owning object already has the evidence.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from harness.graph.graph import edge_order
from harness.guidance.schema import Schema

_ROOT = Path(__file__).resolve().parents[2]

# Child-list edges. _link records these. The sync records the other schema fields.
_CHILD_LISTS = {
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

# The explorer leaves scopes out of the serialized graph.
_SKIPPED = _CHILD_LISTS | {"scopes"}

_SEMANTIC = {
    "class": "OoadClass",
    "subEpic": "Epic",
    "given": "Step",
    "when": "Step",
    "then": "Step",
    "spec": "Spec",
    "map": "UxMap",
    "storyNode": "StoryNode",
    "boundedContext": "BoundedContext",
    "entityRoot": "EntityRoot",
    "valueObject": "ValueObject",
    "domainEvent": "DomainEvent",
    "domainService": "DomainService",
    "node": "NodeRoot",
    "nodeRoot": "NodeRoot",
    "client": "ClientRoot",
    "clientRoot": "ClientRoot",
    "nodeRepository": "NodeRepository",
    "jsonStore": "JsonStore",
    "route": "Route",
    "contextMapping": "ContextMapping",
    # Legacy explorer labels (same tiers as nodeRoot / clientRoot)
    "domainNode": "NodeRoot",
    "domainClient": "ClientRoot",
    "share": "StoryShared",
    "server": "ServerSpec",
    "domain": "DomainSpec",
    "playwright": "PlaywrightSpec",
    "behaviorShared": "BehaviorShared",
    "behaviorDomain": "BehaviorDomain",
    "behaviorServer": "BehaviorServer",
    "behaviorPlaywright": "BehaviorPlaywright",
    "behaviorE2e": "BehaviorE2e",
    "jsonStore": "JsonStore",
    "route": "Route",
    "view": "DomainView",
    "destination": "Destination",
}

_PHASES = {"given": "given", "when": "when", "then": "then"}

_DISPLAY = {"demonstrates": "grouped"}


class SchemaField:
    def __init__(self, owner: str, kind: str, targets: tuple[str, ...], phase: str = "") -> None:
        self.owner = owner
        self.kind = kind
        self.targets = targets
        self.phase = phase


def sync_schema_edges(graph) -> None:
    """Record schema relationship edges for the nodes already on this graph."""
    nodes = _bound_nodes(graph)
    if len(nodes) < 2:
        return
    by_type: dict[str, list] = {}
    for node in nodes:
        by_type.setdefault(node.semantic_type(), []).append(node)
    fields = _fields()
    for owner in nodes:
        semantic = owner.semantic_type()
        for field in fields:
            if field.owner != semantic or field.kind in _SKIPPED:
                continue
            if field.phase and _phase(owner) != field.phase:
                continue
            targets: list = []
            for type_name in field.targets:
                targets.extend(by_type.get(type_name, ()))
            for target in targets:
                if target is owner:
                    continue
                if not _matches(field.kind, owner, target, nodes):
                    continue
                _record(field.kind, owner, target)
                for inverse in _inverses(target.semantic_type(), semantic, field.kind):
                    _record(inverse, target, owner)


def _bound_nodes(graph) -> list:
    found = []
    for practice in graph.practices.values():
        for bucket in practice.nodes.values():
            found.extend(node for node in bucket if hasattr(node, "semantic_type") and hasattr(node, "_subtree"))
    return found


def _record(kind: str, parent, child) -> None:
    display = _DISPLAY.get(kind, "relationship")
    fact = {"kind": kind, "order": edge_order(kind, display), "display": display}
    parent.practice.record(fact, parent, child)
    if parent.practice is not child.practice:
        child.practice.record(fact, child, parent)


def _inverses(owner: str, target: str, forward: str) -> list[str]:
    found = []
    for field in _fields():
        if field.owner != owner or field.kind == forward or field.kind in _CHILD_LISTS or field.kind == "scopes":
            continue
        if target in field.targets and field.kind not in found:
            found.append(field.kind)
    return found


def _matches(kind: str, owner, target, nodes: list) -> bool:
    if kind == "invokes":
        return _calls(owner, target.name) or target.name in list(getattr(owner, "callees", []) or [])
    if kind == "observes":
        return _mentions(_evidence(owner), target.name)
    if kind == "demonstrates":
        return _mentions(_evidence(owner), target.name)
    if kind == "retrievedUsing":
        return _accesses(_evidence(owner), target.name) or _calls(owner, target.name)
    if kind == "uses":
        return _epic_uses(owner, target, nodes)
    if kind == "shownOn":
        if owner.semantic_type() == "Step":
            return step_key(owner) in list(getattr(target, "step_names", []) or [])
        if owner.semantic_type() == "Scenario":
            return scenario_key(owner) in list(getattr(target, "scenario_names", []) or [])
        return owner.name in list(getattr(target, "story_names", []) or [])
    if kind == "specifiedBy":
        return owner.name.casefold() == target.name.casefold()
    if kind == "given":
        return _is_given(target) and target in list(getattr(owner, "steps", []) or [])
    if kind == "dependsOn":
        names = list(getattr(owner, "collaborators", []) or []) + list(getattr(owner, "dependencies", []) or [])
        return target.name in names
    if kind == "hasType":
        return _mentions(str(getattr(owner, "type_hint", "") or ""), target.name)
    if kind == "returnType":
        return _mentions(str(getattr(owner, "return_type", "") or ""), target.name)
    return False


def scenario_key(scenario) -> str:
    """A scenario named the way a screen lists it: ``Story › Scenario``."""
    story = scenario.parent
    while story is not None and story.semantic_type() != "Story":
        story = story.parent
    return " › ".join(part for part in (getattr(story, "name", ""), scenario.name) if part)


def step_key(step) -> str:
    """A step named the way a screen lists it: ``Story › Scenario › Step``."""
    scenario = step.parent
    while scenario is not None and scenario.semantic_type() not in {"Scenario", "Background"}:
        scenario = scenario.parent
    story = scenario.parent if scenario is not None else None
    while story is not None and story.semantic_type() != "Story":
        story = story.parent
    parts = [getattr(story, "name", ""), getattr(scenario, "name", ""), getattr(step, "text", "") or step.name]
    return " › ".join(part for part in parts if part)


def _epic_uses(epic, module, nodes: list) -> bool:
    if epic.semantic_type() != "Epic" or module.semantic_type() != "Module":
        return False
    for node in epic._subtree():
        if node.semantic_type() == "Example":
            for class_node in nodes:
                if class_node.semantic_type() == "OoadClass" and _module_of(class_node) is module and _mentions(_evidence(node), class_node.name):
                    return True
        if node.semantic_type() != "Step":
            continue
        for member in nodes:
            if _module_of(member) is not module:
                continue
            if member.semantic_type() in {"Operation", "Property"} and (_calls(node, member.name) or member.name in list(getattr(node, "callees", []) or [])):
                return True
    return False


def _module_of(node):
    current = node
    seen = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if getattr(current, "semantic_type", lambda: "")() == "Module":
            return current
        current = getattr(current, "parent", None)
    return None


def _calls(owner, name: str) -> bool:
    text = _evidence(owner)
    if not text or not name:
        return False
    for step in _steps_under(owner):
        text += "\n" + _evidence(step)
    pattern = re.compile(rf"(?<![\w]){re.escape(name)}\s*\(")
    return pattern.search(text) is not None


def _steps_under(owner) -> list:
    if not hasattr(owner, "_subtree"):
        return []
    return [node for node in owner._subtree() if node is not owner and node.semantic_type() == "Step"]


def _accesses(text: str, name: str) -> bool:
    if not text or not name:
        return False
    return re.search(rf"\.{re.escape(name)}\b(?!\s*\()", text) is not None


def _mentions(text: str, name: str) -> bool:
    if not text or not name:
        return False
    return re.search(rf"\b{re.escape(name)}\b", text) is not None


def _evidence(node) -> str:
    source = getattr(node, "source", None)
    if source is None:
        return ""
    stored = getattr(source, "__dict__", {}).get("text")
    return stored if isinstance(stored, str) else ""


def _phase(node) -> str:
    step_type = getattr(node, "step_type", None)
    if step_type is None:
        return ""
    return str(getattr(step_type, "value", step_type)).casefold()


def _is_given(node) -> bool:
    return _phase(node) == "given"


# Single-reference LERN / DDD schema fields that appear as children in the explorer tree.
_OVERLAY_TREE_DIRECT_KINDS = frozenset(
    {
        "owns",
        "root",
        "entityRoot",
        "nodeRoot",
        "clientRoot",
        "nodeRepository",
        "repository",
        "route",
        "view",
        "views",
        "mappedTo",
        "local",
        "remote",
        "jsonStore",
        "hosts",
        "interacts",
        "calls",
        "writes",
        "stores",
        "writtenBy",
        "belongsTo",
    }
)

# Fields every schema type may carry that name the type itself, not a relationship.
_OVERLAY_REL_SKIP = frozenset({"is", "fidelity", "name", "path"})


def _relationship_kinds_from_overlay_schema(schema: Schema) -> set[str]:
    """Field names from an overlay schema (``- route: route``)."""
    return {
        name
        for kind in schema.types.values()
        for name, value in kind.fields
        if value and name not in _OVERLAY_REL_SKIP
    }


def overlay_edge_display(kind: str) -> str:
    """Schema-modeled composition uses direct tree edges; the rest stay grouped under the kind."""
    return "direct" if kind in _OVERLAY_TREE_DIRECT_KINDS else "relationship"


def relationship_kinds_for_patterns(active_patterns: tuple[str, ...]) -> dict[str, frozenset[str]]:
    """Relationship field names from active overlay schemas, grouped by practice."""
    if not active_patterns:
        return {}
    patterns = _ROOT / "cdd_guidance" / "patterns"
    by_practice: dict[str, set[str]] = {}
    for pattern in active_patterns:
        root = patterns / pattern / "practices"
        if not root.is_dir():
            continue
        for schema in sorted(root.glob("*/model/schema.yaml")):
            practice = schema.parent.parent.name
            kinds = _relationship_kinds_from_overlay_schema(Schema.load(schema))
            by_practice.setdefault(practice, set()).update(kinds)
    return {name: frozenset(kinds) for name, kinds in by_practice.items()}


@lru_cache(maxsize=1)
def _fields() -> tuple[SchemaField, ...]:
    found: list[SchemaField] = []
    from harness.guidance.practice_catalogue import PracticeCatalogue

    for practice in PracticeCatalogue.keys():
        found.extend(_schema_fields(Schema.load(_ROOT / "cdd_guidance" / "practices" / practice / "model" / "schema.yaml")))
    patterns = _ROOT / "cdd_guidance" / "patterns"
    if patterns.is_dir():
        for schema in sorted(patterns.glob("*/practices/*/model/schema.yaml")):
            found.extend(_schema_fields(Schema.load(schema)))
    return tuple(found)


def _schema_fields(schema: Schema) -> list[SchemaField]:
    """Every field of a schema type whose value names other types."""
    fields: list[SchemaField] = []
    for key, kind in schema.types.items():
        for name, value in kind.fields:
            targets = _targets(value)
            if targets:
                fields.append(SchemaField(semantic_type(key), name, tuple(semantic_type(target) for target in targets), _PHASES.get(key, "")))
    return fields


def _targets(value: str) -> list[str]:
    value = value.strip()
    if not value or '"' in value or value in {"string", "number", "dotPath"}:
        return []
    return [name for name in re.findall(r"[A-Za-z]\w*", value) if name not in {"string", "number", "dotPath"}]


def semantic_type(schema_key: str) -> str:
    """The explorer node type a schema key names: ``class`` is ``OoadClass``; any other key is capitalised."""
    if schema_key in _SEMANTIC:
        return _SEMANTIC[schema_key]
    return schema_key[:1].upper() + schema_key[1:]


def schema_key_for_type(node_type: str) -> str:
    """The schema key for an explorer node type, the reverse of ``semantic_type``."""
    for key, mapped in _SEMANTIC.items():
        if mapped == node_type:
            return key
    return node_type[:1].lower() + node_type[1:]
