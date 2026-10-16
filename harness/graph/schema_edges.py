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

# These are the back-edges. They stay on the clean-engineering node. Mirroring them
# onto the step lists the same operation a second time, under the reverse name.
_MIRROR_SKIP = {"invokedBy", "demonstratedThrough", "usedBy"}

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
                if target is owner or not _matches_target(target, field.targets):
                    continue
                if not _matches(field.kind, owner, target, nodes):
                    continue
                _record(field.kind, owner, target)
                for inverse in _inverses(target.semantic_type(), owner, field.kind):
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
    if parent.practice is not child.practice and kind not in _MIRROR_SKIP:
        child.practice.record(fact, child, parent)


def _inverses(owner: str, other, forward: str) -> list[str]:
    practice = getattr(getattr(other, "practice", None), "name", "")
    semantic = other.semantic_type() if hasattr(other, "semantic_type") else str(other)
    found = []
    for field in _fields():
        if field.owner != owner or field.kind == forward or field.kind in _CHILD_LISTS or field.kind == "scopes":
            continue
        if _name_satisfies(semantic, practice, field.targets) and field.kind not in found:
            found.append(field.kind)
    return found


def _matches(kind: str, owner, target, nodes: list) -> bool:
    if kind == "invokes":
        hit = _calls(owner, target.name) or target.name in list(getattr(owner, "callees", []) or [])
        if not hit:
            return False
        return _on_the_class_in_play(owner, target, nodes)
    if kind == "observes":
        if target.semantic_type() == "Property":
            hit = _is_step(owner) and _accesses(_evidence(owner), target.name)
            return hit and _on_the_class_in_play(owner, target, nodes)
        return _mentions(_evidence(owner), target.name)
    if kind == "demonstrates":
        return target.name in _built_types(_evidence(owner))
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
        if not _is_step(node):
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
    if not _is_step(owner):
        for step in _steps_under(owner):
            text += "\n" + _evidence(step)
    pattern = re.compile(rf"(?<![\w]){re.escape(name)}\s*\(")
    return pattern.search(text) is not None


def _steps_under(owner) -> list:
    if not hasattr(owner, "_subtree"):
        return []
    return [node for node in owner._subtree() if node is not owner and _is_step(node)]


def _accesses(text: str, name: str) -> bool:
    if not text or not name:
        return False
    return re.search(rf"\.{re.escape(name)}\b(?!\s*\()", text) is not None


def _mentions(text: str, name: str) -> bool:
    if not text or not name:
        return False
    return re.search(rf"\b{re.escape(name)}\b", text) is not None


def _evidence(node) -> str:
    """The source the model stored for this node: its own text, or its own line span."""
    source = getattr(node, "source", None)
    if source is None:
        return ""
    stored = getattr(source, "__dict__", {}).get("text")
    if isinstance(stored, str) and stored:
        return stored
    text = getattr(source, "text", None)
    return text if isinstance(text, str) else ""


def _matches_target(node, targets: tuple[str, ...]) -> bool:
    practice = getattr(getattr(node, "practice", None), "name", "")
    return _name_satisfies(node.semantic_type(), practice, targets)


def _name_satisfies(semantic: str, practice: str, targets: tuple[str, ...]) -> bool:
    names = _type_names(semantic, practice)
    return any(target in names for target in targets)


def _on_the_class_in_play(step, member, nodes: list) -> bool:
    """A step names the class its examples build. Members of another class with the same name stay off that step."""
    if not _is_step(step) and step.semantic_type() != "Scenario":
        return True
    playing = _classes_in_play(step)
    if not playing:
        return True
    owners = {
        _owning_class(node)
        for node in nodes
        if node.semantic_type() == member.semantic_type() and node.name == member.name and _owning_class(node) in playing
    }
    if not owners:
        return True
    return _owning_class(member) in owners


def _classes_in_play(step) -> set[str]:
    scenario = step
    seen: set[int] = set()
    while scenario is not None and id(scenario) not in seen:
        seen.add(id(scenario))
        if scenario.semantic_type() == "Scenario":
            break
        scenario = getattr(scenario, "parent", None)
    if scenario is None or scenario.semantic_type() != "Scenario":
        return set()
    found: set[str] = set()
    for node in scenario._subtree():
        if node.semantic_type() == "Example":
            found.update(_built_types(_evidence(node)))
    return found


def _owning_class(node) -> str:
    current = getattr(node, "parent", None)
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if current.semantic_type() == "OoadClass":
            return current.name
        current = getattr(current, "parent", None)
    return ""


def _is_step(node) -> bool:
    practice = getattr(getattr(node, "practice", None), "name", "")
    return _name_satisfies(node.semantic_type(), practice, ("Step",))


def _type_names(semantic: str, practice: str) -> set[str]:
    from harness.graph.schema_rules import _is_supertypes_for_practice, semantic_type

    names = {semantic}
    current = semantic
    seen: set[str] = set()
    is_map = _is_supertypes_for_practice(practice) if practice else {}
    while current and current not in seen:
        seen.add(current)
        ref = is_map.get(current, "")
        if not ref:
            break
        current = semantic_type(ref.split(".")[-1])
        names.add(current)
    return names


def _built_types(text: str) -> set[str]:
    """The class an example builds: its return type, or the class it constructs."""
    if not text:
        return set()
    found = set(re.findall(r"\)\s*:\s*([A-Za-z_]\w*)", text))
    found.update(re.findall(r"\bnew\s+([A-Za-z_]\w*)", text))
    return found


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
        phase = _PHASES.get(owner_key, "")
        if _semantic(owner_key).casefold() == phase:
            phase = ""
        fields.append(
            SchemaField(
                _semantic(owner_key),
                kind,
                tuple(_semantic(name) for name in targets),
                phase,
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
