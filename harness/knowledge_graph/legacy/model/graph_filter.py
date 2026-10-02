"""Filter — match seeds, then expand the neighborhood."""

from __future__ import annotations

import json
from typing import Any, Iterable

_TRUE = (True, "true", "True", 1)
_ALIASES = {
    "node": "name",
    "nodeTypes": "semantic_types",
    "node_type": "semantic_type",
    "relatedTo": "related_to",
    "relationshipTypes": "relationship_types",
    "connectorKind": "relationship_type",
}


class Filter:
    def __init__(
        self,
        path: str = "",
        name: str = "",
        node_id: str = "",
        file: str = "",
        practice: str = "",
        practices: list[str] | None = None,
        semantic_type: str = "",
        semantic_types: list[str] | None = None,
        fidelity: str = "",
        stages: list[str] | None = None,
        violations: bool = False,
        rule: str = "",
        rules: list[str] | None = None,
        related_to: "Filter | None" = None,
        relationship_type: str = "",
        relationship_types: list[str] | None = None,
        kind: str = "",
    ) -> None:
        self.path = path
        self.name = name
        self.node_id = node_id
        self.file = file
        self.practice = practice
        self.practices = practices
        self.semantic_type = semantic_type
        self.semantic_types = semantic_types
        self.fidelity = fidelity
        self.stages = stages
        self.violations = violations
        self.rule = rule
        self.rules = rules
        self.related_to = related_to
        self.relationship_type = relationship_type
        self.relationship_types = relationship_types
        self.kind = kind

    @classmethod
    def from_value(cls, value: Any) -> Filter:
        if value in (None, "", {}, []):
            return cls()
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("{"):
                return cls.from_value(json.loads(stripped))
            return cls(path=stripped)
        if not isinstance(value, dict):
            raise TypeError(f"Filter expected an object, got {type(value).__name__}")
        fields = cls()._canonical_fields(value)
        related = fields.get("related_to")
        if related not in (None, "", {}):
            fields["related_to"] = cls.from_value(related)
        allowed = cls.__init__.__code__.co_varnames[1:]
        return cls(**{key: fields[key] for key in fields if key in allowed})

    @property
    def constrains(self) -> bool:
        return bool(
            self.path
            or self.name
            or self.node_id
            or self.file
            or self.practice
            or self.practices
            or self.semantic_type
            or self.semantic_types
            or self.fidelity
            or self.stages
            or self.violations
            or self.rule
            or self.rules
            or self.related_to
            or self.relationship_type
            or self.relationship_types
            or self.kind
        )

    def scope(self) -> Filter:
        return Filter(path=self.path, name=self.name, node_id=self.node_id)

    def without_scope(self) -> Filter:
        fields = dict(self.__dict__)
        fields["path"] = ""
        fields["name"] = ""
        fields["node_id"] = ""
        allowed = self.__init__.__code__.co_varnames[1:]
        return Filter(**{key: fields[key] for key in allowed if key in fields})

    def _canonical_fields(self, value: dict) -> dict:
        fields: dict[str, Any] = {}
        for key, raw in value.items():
            fields[_ALIASES.get(key, key)] = raw
        return fields

    def listed(self, keys: tuple[str, ...]) -> list[str] | None:
        values: list[str] = []
        for key in keys:
            raw = getattr(self, key, None)
            if raw in (None, "", [], ()):
                continue
            if isinstance(raw, (list, tuple)):
                values.extend(str(item) for item in raw if str(item).strip())
            else:
                values.append(str(raw))
        return values or None

    def matches(self, node: Any) -> bool:
        if not self._match_path(node):
            return False
        if not self._match_identity(node):
            return False
        if not self._match_source(node):
            return False
        if not self._match_related(node):
            return False
        return self._match_rules(node)

    def expand_ids(self, seeds: Iterable[str], graph: Any) -> set[str]:
        seed_ids = {node_id for node_id in seeds if node_id in graph.nodes}
        keep = set(seed_ids)
        for node_id in seed_ids:
            node = graph.nodes[node_id]
            for ancestor in node.ancestors():
                keep.add(ancestor.node_id)
            for child in node.descendants():
                keep.add(child.node_id)
            for other in node.incident():
                keep.add(other.node_id)
        return keep

    def subtree_ids(self, seeds: Iterable[str], graph: Any) -> set[str]:
        seed_ids = {node_id for node_id in seeds if node_id in graph.nodes}
        keep = set(seed_ids)
        for node_id in seed_ids:
            for child in graph.nodes[node_id].descendants():
                keep.add(child.node_id)
        return keep

    def _match_path(self, node: Any) -> bool:
        path = str(self.path or "").strip()
        if not path:
            return True
        keys = [part.strip().casefold() for part in path.split(".") if part.strip()]
        hits = {item.node_id for item in self._nodes_along(node.graph, keys)}
        return node.node_id in hits

    def _match_identity(self, node: Any) -> bool:
        names = self.listed(("name",))
        if names and self._name_key(node) not in {item.casefold() for item in names}:
            return False
        if self.node_id and node.node_id != str(self.node_id):
            return False
        practices = self.listed(("practices", "practice"))
        if practices and (getattr(node, "practice", "") or "") not in practices:
            return False
        types = self.listed(("semantic_types", "semantic_type"))
        if types and node.semantic_type() not in types:
            return False
        stages = self.listed(("stages", "fidelity"))
        stage = getattr(node, "fidelity", None) or getattr(node, "stage", "") or ""
        if stages and stage not in stages:
            return False
        return True

    def _match_source(self, node: Any) -> bool:
        file = str(self.file or "").replace("\\", "/").casefold()
        if not file:
            return True
        src = str(getattr(getattr(node, "source", None), "file", "") or "").replace("\\", "/")
        return file in src.casefold()

    def _match_related(self, node: Any) -> bool:
        kinds = self.listed(("relationship_types", "relationship_type"))
        if kinds and not node.has_kind(kinds):
            return False
        related = self.related_to
        if related is None:
            return True
        others = node.incident()
        kind = str(related.kind or related.relationship_type or "")
        if kind:
            others = [item for item in others if self._edge_kind(node, item) == kind]
        return any(related.matches(item) for item in others)

    def _match_rules(self, node: Any) -> bool:
        hits = list(node.graph.violations_for(node))
        rules = self.listed(("rules", "rule"))
        if self.violations in _TRUE:
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

    def _nodes_along(self, graph: Any, keys: list[str]):
        if not keys:
            return list(graph.nodes.values())
        current = [node for node in graph.nodes.values() if self._key_matches(node, keys[0])]
        for key in keys[1:]:
            current = [
                child
                for node in current
                for child in node.children()
                if self._key_matches(child, key)
            ]
        return current

    def _key_matches(self, node: Any, key: str) -> bool:
        return self._name_key(node) == key or node.node_id.casefold() == key

    def _name_key(self, node: Any) -> str:
        return str(getattr(node, "name", "") or node.semantic_type()).casefold()

    def _edge_kind(self, node: Any, other: Any) -> str:
        for edge in node.graph.edges_at(node):
            if edge.from_node is other or edge.to_node is other:
                return edge.kind
        return ""
