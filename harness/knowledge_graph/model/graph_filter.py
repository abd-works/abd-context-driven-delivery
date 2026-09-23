"""Filter bag for KnowledgeGraph — match seeds, then expand the neighborhood."""

from __future__ import annotations

import json
from typing import Any, Iterable

from .graph_node import Kind

_TRUE = (True, "true", "True", 1)


def parse_filter(filter: Any) -> dict:
    if filter in (None, "", {}, []):
        return {}
    if isinstance(filter, str):
        stripped = filter.strip()
        if stripped.startswith("{"):
            return json.loads(stripped)
        return {"path": stripped}
    return dict(filter)


def listed(parsed: dict, *keys: str) -> list[str] | None:
    values: list[str] = []
    for key in keys:
        raw = parsed.get(key)
        if raw in (None, "", [], ()):
            continue
        if isinstance(raw, (list, tuple)):
            values.extend(str(item) for item in raw if str(item).strip())
        else:
            values.append(str(raw))
    return values or None


def is_true(value: Any) -> bool:
    return value in _TRUE


def match_node(node: Any, graph: Any, parsed: dict) -> bool:
    if not _match_path(node, graph, parsed):
        return False
    if not _match_identity(node, parsed):
        return False
    if not _match_source(node, parsed):
        return False
    if not _match_related(node, graph, parsed):
        return False
    return _match_rules(node, graph, parsed)


def expand_ids(seeds: Iterable[str], graph: Any) -> set[str]:
    seed_ids = {node_id for node_id in seeds if node_id in graph.nodes}
    keep = set(seed_ids)
    for node_id in seed_ids:
        node = graph.nodes[node_id]
        for ancestor in _ancestors(node):
            keep.add(ancestor.node_id)
        for child in _descendants(node):
            keep.add(child.node_id)
        for other in _incident(node):
            keep.add(other.node_id)
    return keep


def _match_path(node: Any, graph: Any, parsed: dict) -> bool:
    path = str(parsed.get("path") or "").strip()
    if not path:
        return True
    keys = [part.strip().casefold() for part in path.split(".") if part.strip()]
    hits = {item.node_id for item in _nodes_along(graph, keys)}
    return node.node_id in hits


def _match_identity(node: Any, parsed: dict) -> bool:
    names = listed(parsed, "name", "node")
    if names and _name_key(node) not in {item.casefold() for item in names}:
        return False
    node_id = parsed.get("node_id")
    if node_id and node.node_id != str(node_id):
        return False
    practices = listed(parsed, "practices", "practice")
    if practices and (getattr(node, "practice", "") or "") not in practices:
        return False
    types = listed(parsed, "semantic_types", "semantic_type", "nodeTypes", "node_type")
    if types and node.semantic_type() not in types:
        return False
    stages = listed(parsed, "stages", "fidelity")
    stage = getattr(node, "fidelity", None) or getattr(node, "stage", "") or ""
    if stages and stage not in stages:
        return False
    return True


def _match_source(node: Any, parsed: dict) -> bool:
    file = str(parsed.get("file") or "").replace("\\", "/").casefold()
    if not file:
        return True
    src = str(getattr(getattr(node, "source", None), "file", "") or "").replace("\\", "/")
    return file in src.casefold()


def _match_related(node: Any, graph: Any, parsed: dict) -> bool:
    kinds = listed(
        parsed,
        "relationship_types",
        "relationshipTypes",
        "relationship_type",
        "connectorKind",
    )
    if kinds and not _has_kind(node, kinds):
        return False
    related = parsed.get("related_to") or parsed.get("relatedTo")
    if not related:
        return True
    target = dict(related) if isinstance(related, dict) else {"path": related}
    kind = str(target.get("kind") or "")
    others = _incident(node)
    if kind:
        others = [item for item in others if _edge_kind(node, item) == kind]
    return any(match_node(item, graph, target) for item in others)


def _match_rules(node: Any, graph: Any, parsed: dict) -> bool:
    hits = list(graph._violations_by_node.get(node.node_id, []))
    rules = listed(parsed, "rules", "rule")
    if is_true(parsed.get("violations")):
        if not hits:
            return False
        if rules:
            return any(hit.rule_slug in rules for hit in hits)
        return True
    if not rules:
        return True
    if any(hit.rule_slug in rules for hit in hits):
        return True
    names = list(getattr(node, "applicable_rules", None) or [])
    return any(slug in names for slug in rules)


def _nodes_along(graph: Any, keys: list[str]):
    if not keys:
        return list(graph.nodes.values())
    current = [node for node in graph.nodes.values() if _key_matches(node, keys[0])]
    for key in keys[1:]:
        current = [
            child
            for node in current
            for child in _children(node)
            if _key_matches(child, key)
        ]
    return current


def _key_matches(node: Any, key: str) -> bool:
    return _name_key(node) == key or node.node_id.casefold() == key


def _name_key(node: Any) -> str:
    return str(getattr(node, "name", "") or node.semantic_type()).casefold()


def _children(node: Any):
    owned = node.related(Kind.OWNS)
    return owned if owned else node.related()


def _ancestors(node: Any):
    found = []
    current = node
    for _ in range(16):
        parents = current.related(Kind.BELONGS_TO) or current.related(
            Kind.OWNS, direction="in"
        )
        if not parents:
            break
        current = parents[0]
        found.append(current)
    return found


def _descendants(node: Any):
    found = []
    stack = list(_children(node))
    seen = {node.node_id}
    while stack:
        child = stack.pop()
        if child.node_id in seen:
            continue
        seen.add(child.node_id)
        found.append(child)
        stack.extend(_children(child))
    return found


def _incident(node: Any):
    return node.related() + node.related(direction="in")


def _has_kind(node: Any, kinds: list[str]) -> bool:
    names = set(kinds)
    return any(edge.kind in names for edge in _edges(node))


def _edge_kind(node: Any, other: Any) -> str:
    for edge in _edges(node):
        if edge.from_node is other or edge.to_node is other:
            return edge.kind
    return ""


def _edges(node: Any):
    graph = node.graph
    outgoing = graph._outgoing.get(node.node_id, ())
    incoming = graph._incoming.get(node.node_id, ())
    return list(outgoing) + list(incoming)
