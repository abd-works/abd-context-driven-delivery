"""Guidance rule registry and fidelity scope for graph nodes."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set

from harness.guidance.rule import Rule, RulesCollection

_REPO = Path(__file__).resolve().parents[3]
_PRACTICES = _REPO / "practices"
_CLASS_TYPES = {
    "OoadClass",
    "Entity",
    "EntityRoot",
    "ValueObject",
    "Repository",
    "DomainEvent",
    "DomainService",
}
_KIND_SEMANTICS = {
    "Function": {"Operation", "Property"},
    "Class": set(_CLASS_TYPES),
    "Module": {"Module", "Package"},
}
_MEMBER_TYPES = {"Operation", "Property", "Parameter"}

# Fidelity order: first match wins as "closest" (most specific first).
FIDELITY_ORDER: Dict[str, List[str]] = {
    "stories": ["acceptance_tests", "scenarios", "story_map"],
    "clean_engineering": ["code", "model", "modules", "language"],
    "ddd": ["tactics", "building_blocks", "bounded_context"],
    "bdd": ["behavior"],
    "ux": ["front_end_code", "mockup", "ia"],
}

FIDELITY_NODE_SCOPE: Dict[str, Dict[str, Set[str]]] = {
    "stories": {
        "story_map": {"Epic", "SubEpic", "Story", "StoryMap"},
        "scenarios": {"Scenario", "Background", "Step", "Example"},
        "acceptance_tests": {"Step", "Example"},
    },
    "clean_engineering": {
        "modules": {"Module", "CleanEngineeringModel"},
        "model": {
            "Module",
            "File",
            "OoadClass",
            "Property",
            "Operation",
            "Parameter",
            "CleanEngineeringModel",
        },
        "code": {
            "OoadClass",
            "Property",
            "Operation",
            "Parameter",
            "Module",
            "File",
        },
        "language": {"Module", "CleanEngineeringModel"},
    },
    "ddd": {
        "bounded_context": {"BoundedContext", "Aggregate", "Module"},
        "building_blocks": {
            "Entity",
            "EntityRoot",
            "ValueObject",
            "Repository",
            "DomainEvent",
            "DomainService",
            "Aggregate",
            "BoundedContext",
        },
        "tactics": {
            "Entity",
            "EntityRoot",
            "ValueObject",
            "Repository",
            "DomainEvent",
            "DomainService",
        },
    },
    "bdd": {
        "behavior": {"Description", "Context", "Observation"},
    },
    "ux": {
        "ia": {"Screen", "UxMap"},
        "mockup": {"Screen", "Control", "UxMap"},
        "front_end_code": {"Screen", "Control", "UxMap"},
    },
}

@dataclass
class RuleViolation:
    rule_slug: str
    message: str
    practice: str
    fidelity: Optional[str] = None
    node_id: str = ""
    location: str = ""
    line: int = 0
    direct: bool = False
    source: str = "graph"  # graph | codeql
    contributors: List[str] = field(default_factory=list)

    @classmethod
    def from_entry(cls, graph, entry: dict):
        node_id = entry.get("node_id") or ""
        if node_id and node_id in graph.nodes:
            return graph.nodes[node_id]
        semantic = entry.get("semantic_type") or ""
        name = entry.get("node_name") or ""
        for node in graph.nodes.values():
            if node.semantic_type() != semantic:
                continue
            if node.name != name:
                continue
            return node
        return None

    def belongs_on(self, node) -> bool:
        message = self.message
        labeled = re.search(r"Operation '([^']+)'", message)
        if labeled and "." in labeled.group(1):
            cls, _, op = labeled.group(1).rpartition(".")
            owner = node.owner_class()
            return node.name == op and owner is not None and owner.name == cls
        size = re.search(r" is (\d+) (lines|statements)", message)
        if size:
            if size.group(2) == "statements":
                return True
            src = getattr(node, "source", None)
            start = int(getattr(src, "line", 0) or 0)
            end = int(getattr(src, "end_line", 0) or start)
            return start > 0 and (end - start + 1) == int(size.group(1))
        attr = re.search(r"private attribute '([^']+)'", message) or re.search(
            r"via '([^']+)'", message
        )
        if attr:
            text = str(getattr(getattr(node, "source", None), "text", "") or "")
            return bool(text) and attr.group(1) in text
        return False


class GraphRule(Rule):
    def __init__(self, rule: Rule, *, practice: str, shared: bool = False) -> None:
        super().__init__(rule.slug, rule.body, rule.fidelity)
        self.scanner = rule.scanner
        parent = getattr(rule, "parent", None)
        if parent is not None:
            self.parent = parent
        self.practice = practice
        self.shared = shared

    def validate(self) -> str:
        if self.graphQuery is None:
            return super().validate()
        return super().validate()

    @property
    def inherits_to_children(self) -> bool:
        return self.shared

    @property
    def applies_to(self) -> Set[str]:
        if self.slug == "keep-classes-single-responsibility":
            return set(_CLASS_TYPES)
        if self.shared:
            return self.types_for_practice()
        return set(FIDELITY_NODE_SCOPE.get(self.practice, {}).get(self.fidelity or "", set()))

    @property
    def query_pack(self) -> Path:
        return _PRACTICES / self.practice / "model" / "codeql"

    @property
    def pack_rules_query(self) -> Optional[Path]:
        path = self.query_pack / "rules.ql"
        return path if path.is_file() else None

    @property
    def graph_evaluated(self) -> bool:
        return self.graphQuery is not None

    @property
    def graphQuery(self) -> Optional[Path]:
        path = self.query_pack / f"{self.slug}.ql"
        return path if path.is_file() else None

    def load_graph_query(self) -> str:
        path = self.graphQuery
        if path is None:
            return ""
        return path.read_text(encoding="utf-8")

    def evaluate(self, graph, hits=None, by_name=None) -> List[RuleViolation]:
        if hits is None:
            from .codeql import CodeQL, Rows

            combined = self.pack_rules_query
            if combined is not None:
                grouped = CodeQL(graph.root).run_rules(combined, [self.slug])
                hits = Rows.from_tuples(grouped.get(self.slug) or [])
            elif self.graphQuery is not None:
                hits = CodeQL(graph.root).run(self.graphQuery)
            else:
                raise FileNotFoundError(f"no graphQuery file for {self.slug}")
        from .graph_query_spec import refine_rows

        hits = refine_rows(self.slug, hits)
        return self.hits_from_query(graph, hits)

    def hits_from_query(self, graph, hits) -> List[RuleViolation]:
        names = graph.named_nodes()
        violations: List[RuleViolation] = []
        for (name, file, line), payload in self._group_query_hits(hits).items():
            kind = str(payload.get("kind") or "")
            self._hit_file = file
            self._hit_line = line
            subjects = self._subjects_for_hit(
                [
                    candidate
                    for candidate in names.get(name, ())
                    if self._is_subject(candidate, kind)
                ]
            )
            contributor_ids = [
                child.node_id
                for contributor in payload["contributors"]
                for child in names.get(contributor, ())
            ]
            for subject in subjects:
                violations.append(
                    self._violation(
                        subject,
                        payload["message"],
                        contributors=contributor_ids,
                        source="codeql",
                    )
                )
        return violations

    def _group_query_hits(self, hits) -> Dict[tuple, dict]:
        grouped: Dict[tuple, dict] = {}
        for hit in hits:
            name = hit.get("name", "")
            file = str(hit.get("file") or "").replace("\\", "/")
            line = int(hit.get("line") or 0)
            bucket = grouped.setdefault(
                (name, file, line),
                {
                    "message": hit.get("message", ""),
                    "contributors": [],
                    "kind": hit.get("kind") or "",
                },
            )
            if hit.get("kind") and not bucket.get("kind"):
                bucket["kind"] = hit.get("kind")
            contributor = hit.get("contributor")
            if contributor:
                bucket["contributors"].append(contributor)
        return grouped

    def _subjects_for_hit(self, candidates: list) -> list:
        file, line = self._hit_file, self._hit_line
        if file and line > 0:
            return [
                candidate
                for candidate in candidates
                if candidate.matches_source(file, line)
            ]
        if len(candidates) == 1:
            return candidates
        return []

    def types_for_practice(self) -> Set[str]:
        out: Set[str] = set()
        for types in FIDELITY_NODE_SCOPE.get(self.practice, {}).values():
            out.update(types)
        return out

    def _is_subject(self, node, kind: str = "") -> bool:
        semantic = node.semantic_type()
        if kind:
            allowed = _KIND_SEMANTICS.get(kind)
            if allowed is not None:
                return semantic in allowed and semantic in self.applies_to
        if semantic == "Parameter" and self.slug not in (
            "avoid-vague-parameter-names",
            "limit-operation-parameters",
            "use-typed-signatures",
        ):
            return False
        return semantic in self.applies_to

    def _violation(
        self,
        node,
        message: str,
        *,
        location: str = "",
        line: int = 0,
        contributors: Optional[List[str]] = None,
        source: str = "graph",
    ) -> RuleViolation:
        src = getattr(node, "source", None)
        return RuleViolation(
            rule_slug=self.slug,
            message=message,
            practice=self.practice,
            fidelity=self.fidelity,
            node_id=node.node_id,
            location=location or str(getattr(src, "file", "") or ""),
            line=line or int(getattr(src, "line", 0) or 0),
            source=source,
            contributors=list(contributors or ()),
        )


def drop_cloned_operation_hits(graph, by_node: Dict[str, list]) -> None:
    from collections import Counter

    counts: Counter = Counter()
    member_ids: List[str] = []
    for node_id, hits in by_node.items():
        node = graph.nodes.get(node_id)
        if node is None or node.semantic_type() not in _MEMBER_TYPES:
            continue
        member_ids.append(node_id)
        for hit in hits:
            counts[(hit.rule_slug, hit.message)] += 1
    for node_id in member_ids:
        node = graph.nodes[node_id]
        by_node[node_id] = [
            hit
            for hit in by_node[node_id]
            if counts[(hit.rule_slug, hit.message)] <= 1
            or hit.belongs_on(node)
        ]


def _practice_slug(parent: Any) -> str:
    if parent is None:
        return ""
    practice = getattr(parent, "practice_guidance", None)
    if practice is None and getattr(parent, "fidelities", None) is not None:
        practice = parent
    if practice is None:
        return ""
    from harness.markdown import class_file_directory

    return class_file_directory(practice).name


class GraphRulesCollection(RulesCollection):
    @classmethod
    def from_markdown(
        cls,
        text: str,
        fidelity: str | None = None,
        parent: Any = None,
    ) -> RulesCollection:
        collection = super().from_markdown(text, fidelity=fidelity, parent=parent)
        practice = _practice_slug(parent)
        if not practice:
            return collection
        shared = getattr(parent, "fidelities", None) is not None
        for slug, rule in list(collection.entries.items()):
            if not isinstance(rule, Rule) or isinstance(rule, GraphRule):
                continue
            query = _PRACTICES / practice / "model" / "codeql" / f"{slug}.ql"
            if not query.is_file():
                continue
            collection.entries[slug] = GraphRule(rule, practice=practice, shared=shared)
        return collection


class RuleRegistry:
    def __init__(self) -> None:
        self.rules: List[GraphRule] = []

    @classmethod
    def load(cls) -> "RuleRegistry":
        registry = cls()
        registry.load_from_practices()
        return registry

    def load_from_practices(self) -> None:
        from .guidance_rules_loader import load_graph_rules_from_markdown

        self.rules = load_graph_rules_from_markdown()

    def runnable(
        self,
        *,
        slugs: Optional[Set[str]] = None,
        skip: Optional[Set[str]] = None,
    ) -> tuple[List[GraphRule], List[GraphRule]]:
        seen: Set[str] = set()
        runnable: List[GraphRule] = []
        skipped: List[GraphRule] = []
        for rule in self.rules:
            if not rule.graph_evaluated or rule.slug in seen:
                continue
            if slugs is not None and rule.slug not in slugs:
                continue
            seen.add(rule.slug)
            if skip is not None and rule.slug in skip:
                skipped.append(rule)
                continue
            runnable.append(rule)
        return runnable, skipped

    def evaluate(
        self,
        graph,
        *,
        slugs: Optional[Set[str]] = None,
        skip: Optional[Set[str]] = None,
    ) -> Dict[str, List[RuleViolation]]:
        return graph._evaluate_graph_rules(slugs=slugs, skip=skip)

    def rules_for_node(
        self,
        *,
        practice: str,
        semantic_type: str,
        fidelity: Optional[str] = None,
        direct_only: bool = False,
    ) -> List[GraphRule]:
        matched: List[GraphRule] = []
        closest = closest_fidelity(practice, semantic_type)
        for rule in self.rules:
            if rule.practice != practice:
                continue
            if fidelity is not None and rule.fidelity != fidelity and not rule.shared:
                continue
            if rule.shared:
                if semantic_type not in rule.applies_to and not fidelity:
                    continue
            elif semantic_type not in rule.applies_to:
                continue
            if direct_only:
                if rule.shared:
                    continue
                if rule.fidelity != closest:
                    continue
            matched.append(rule)
        return matched

    def __iter__(self) -> Iterator[GraphRule]:
        return iter(self.rules)


def closest_fidelity(practice: str, semantic_type: str) -> Optional[str]:
    for fidelity in FIDELITY_ORDER.get(practice, []):
        scope = FIDELITY_NODE_SCOPE.get(practice, {}).get(fidelity, set())
        if semantic_type in scope:
            return fidelity
    return None
