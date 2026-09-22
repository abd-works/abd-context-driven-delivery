"""Guidance rule registry and fidelity scope for graph nodes."""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Set

from actions.scan.rule import Rule

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

# Fidelity order: first match wins as "closest" (most specific first).
FIDELITY_ORDER: Dict[str, List[str]] = {
    "stories": ["acceptance_tests", "scenarios", "story_map"],
    "clean_engineering": ["code", "model", "modules", "language"],
    "ddd": ["tactics", "building_blocks", "bounded_context"],
    "bdd": ["behavior"],
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
    def for_rows(cls, rule: "GraphRule", graph, rows) -> List["RuleViolation"]:
        grouped: Dict[str, dict] = {}
        for row in rows:
            name = row.get("name", "")
            bucket = grouped.setdefault(
                name,
                {"message": row.get("message", ""), "contributors": []},
            )
            contributor = row.get("contributor")
            if contributor:
                bucket["contributors"].append(contributor)
        violations: List[RuleViolation] = []
        for name, payload in grouped.items():
            subjects = [
                candidate
                for candidate in graph.nodes.values()
                if getattr(candidate, "name", None) == name and rule._is_subject(candidate)
            ]
            contributor_ids = [
                child.node_id
                for contributor in payload["contributors"]
                for child in graph.nodes.values()
                if getattr(child, "name", None) == contributor
            ]
            for subject in subjects:
                violations.append(
                    rule._violation(
                        subject,
                        payload["message"],
                        contributors=contributor_ids,
                        source="codeql",
                    )
                )
        return violations


class GraphRule:
    def __init__(self, rule: Rule, *, practice: str, shared: bool = False) -> None:
        self.rule = rule
        self.practice = practice
        self.shared = shared

    def __getattr__(self, name: str):
        return getattr(self.rule, name)

    @property
    def inherits_to_children(self) -> bool:
        return self.shared

    @property
    def applies_to(self) -> Set[str]:
        if self.slug == "keep-classes-single-responsibility":
            return set(_CLASS_TYPES)
        if self.shared:
            return _all_types_for_practice(self.practice)
        return set(FIDELITY_NODE_SCOPE.get(self.practice, {}).get(self.fidelity or "", set()))

    @property
    def graph_evaluated(self) -> bool:
        return self.graphQuery is not None

    @property
    def graphQuery(self) -> Optional[Path]:
        path = _PRACTICES / self.practice / "model" / "codeql" / f"{self.slug}.ql"
        return path if path.is_file() else None

    def load_graph_query(self) -> str:
        path = self.graphQuery
        if path is None:
            return ""
        return path.read_text(encoding="utf-8")

    def evaluate(self, graph, rows=None) -> List[RuleViolation]:
        path = self.graphQuery
        if path is None:
            raise FileNotFoundError(f"no graphQuery file for {self.slug}")
        if rows is None:
            from .codeql import CodeQL

            rows = CodeQL(graph.root).run(path)
        return RuleViolation.for_rows(self, graph, rows)

    def _is_subject(self, node) -> bool:
        from practices.clean_engineering.model.base_class_model import OoadClass

        if isinstance(node, OoadClass):
            return True
        return getattr(node, "_semantic_type_name", "") in self.applies_to

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


def _all_types_for_practice(practice: str) -> Set[str]:
    out: Set[str] = set()
    for types in FIDELITY_NODE_SCOPE.get(practice, {}).values():
        out.update(types)
    return out


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

    def evaluate(
        self,
        graph,
        *,
        slugs: Optional[Set[str]] = None,
        skip: Optional[Set[str]] = None,
    ) -> Dict[str, List[RuleViolation]]:
        from .codeql import CodeQL

        by_node: Dict[str, List[RuleViolation]] = {}
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
        for rule in skipped:
            print(f"skip {rule.slug} (0 hits)", flush=True)
            graph.record_rule_timing(rule.slug, 0.0, 0, "skipped")
        by_pack: Dict[Path, List[GraphRule]] = defaultdict(list)
        for rule in runnable:
            if rule.graphQuery is None:
                continue
            by_pack[rule.graphQuery.parent].append(rule)
        codeql = CodeQL(graph.root)
        for pack, pack_rules in by_pack.items():
            if not pack_rules:
                continue
            codeql._write_subject_filter(pack)
            queries = [rule.graphQuery for rule in pack_rules if rule.graphQuery is not None]
            print(f"run-queries {pack.name} ({len(queries)} rules) ...", flush=True)
            started = time.perf_counter()
            try:
                batch = codeql.run_queries(queries)
            except Exception as error:
                seconds = time.perf_counter() - started
                graph.record_rule_timing(f"run-queries:{pack.name}", seconds, 0, f"{type(error).__name__}: {error}")
                graph.record_partial_failure(f"run-queries {pack.name}", error)
                print(f"run-queries {pack.name}  {seconds:.2f}s  ERROR {error}", flush=True)
                continue
            seconds = time.perf_counter() - started
            graph.record_rule_timing(
                f"run-queries:{pack.name}",
                seconds,
                sum(len(batch.get(rule.slug) or []) for rule in pack_rules),
            )
            print(f"run-queries {pack.name}  {seconds:.2f}s", flush=True)
            for rule in pack_rules:
                print(f"rule {rule.slug} ...", flush=True)
                mapped = time.perf_counter()
                try:
                    hits = rule.evaluate(graph, rows=codeql._select_rows(batch.get(rule.slug) or []))
                except Exception as error:
                    elapsed = time.perf_counter() - mapped
                    graph.record_rule_timing(rule.slug, elapsed, 0, f"{type(error).__name__}: {error}")
                    graph.record_partial_failure(f"rule {rule.slug}", error)
                    print(f"rule {rule.slug}  {elapsed:.2f}s  ERROR {error}", flush=True)
                    continue
                elapsed = time.perf_counter() - mapped
                graph.record_rule_timing(rule.slug, elapsed, len(hits))
                print(f"rule {rule.slug}  {elapsed:.2f}s  hits={len(hits)}", flush=True)
                for violation in hits:
                    by_node.setdefault(violation.node_id, []).append(violation)
        return by_node

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
