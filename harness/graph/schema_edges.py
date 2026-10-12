"""Schema relationship fields recorded on the graph node.

Child lists already record their own edge. belongsTo is the back-edge for those
lists. Every other relationship the schema names is recorded here when the two
nodes are on the graph and the owning object already has the evidence.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_PRACTICES = ("stories", "clean_engineering", "ddd", "bdd", "ux")

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
    "node": "DomainNode",
    "client": "DomainClient",
    "share": "StoryShared",
    "server": "ServerSpec",
    "domain": "DomainSpec",
    "playwright": "PlaywrightSpec",
    "jsonStore": "JsonStore",
    "route": "Route",
    "view": "DomainView",
    "destination": "Destination",
}

_PHASES = {"given": "given", "when": "when", "then": "then"}

_DISPLAY = {"demonstrates": "grouped"}

_ORDER = {
    "demonstrates": 3,
    "shownOn": 4,
    "specifiedBy": 4,
    "invokes": 5,
    "invokedBy": 6,
    "demonstratedThrough": 6,
    "hasType": 6,
    "retrievedUsing": 7,
    "observes": 8,
    "uses": 9,
    "usedBy": 9,
    "dependsOn": 10,
    "given": 2,
    "returnType": 7,
    "specifies": 4,
}


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
    fields = _fields()
    for owner in nodes:
        semantic = owner.semantic_type()
        for field in fields:
            if field.owner != semantic or field.kind in _SKIPPED:
                continue
            if field.phase and _phase(owner) != field.phase:
                continue
            for target in nodes:
                if target is owner or target.semantic_type() not in field.targets:
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
    fact = {"kind": kind, "order": _ORDER.get(kind, 1), "display": _DISPLAY.get(kind, "relationship")}
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


@lru_cache(maxsize=1)
def _fields() -> tuple[SchemaField, ...]:
    found: list[SchemaField] = []
    for practice in _PRACTICES:
        path = _ROOT / "practices" / practice / "model" / "schema.yaml"
        if path.is_file():
            found.extend(_parse(path.read_text(encoding="utf-8")))
    patterns = _ROOT / "patterns"
    if patterns.is_dir():
        for schema in sorted(patterns.glob("*/practices/*/model/schema.yaml")):
            found.extend(_parse(schema.read_text(encoding="utf-8")))
    return tuple(found)


def _parse(text: str) -> list[SchemaField]:
    fields: list[SchemaField] = []
    owner_key = ""
    for line in text.splitlines():
        header = re.match(r"^([A-Za-z]\w*):\s*$", line)
        if header:
            owner_key = header.group(1)
            continue
        field = re.match(r"^  ([A-Za-z]\w*)\??:\s*(.*)$", line)
        if field is None or not owner_key:
            continue
        targets = _targets(field.group(2))
        if not targets:
            continue
        kind = field.group(1)
        fields.append(
            SchemaField(
                _semantic(owner_key),
                kind,
                tuple(_semantic(name) for name in targets),
                _PHASES.get(owner_key, ""),
            )
        )
    return fields


def _targets(value: str) -> list[str]:
    value = value.strip()
    if not value or '"' in value or value in {"string", "number", "dotPath"}:
        return []
    return [name for name in re.findall(r"[A-Za-z]\w*", value) if name not in {"string", "number", "dotPath"}]


def _semantic(name: str) -> str:
    if name in _SEMANTIC:
        return _SEMANTIC[name]
    return name[:1].upper() + name[1:]
