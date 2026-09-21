"""Guidance rule registry and fidelity scope for graph nodes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional, Set

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

# Graph-evaluated rules (predicate over edges) keyed by slug.
GRAPH_EVALUATED_RULES: Set[str] = {
    "scenario-scopes-example",
    "gwt-steps-trace-to-domain-operations",
    "examples-trace-domain-model",
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


@dataclass
class GraphRule:
    slug: str
    body: str
    practice: str
    fidelity: Optional[str] = None
    shared: bool = False
    applies_to: Set[str] = field(default_factory=set)
    inherits_to_children: bool = False
    graph_evaluated: bool = False

    @classmethod
    def from_rule(
        cls,
        rule,
        *,
        practice: str,
        fidelity: Optional[str],
        shared: bool,
    ) -> "GraphRule":
        scopes = FIDELITY_NODE_SCOPE.get(practice, {})
        applies = set(scopes.get(fidelity or "", set()))
        if shared:
            applies = _all_types_for_practice(practice)
        return cls(
            slug=rule.slug,
            body=rule.body,
            practice=practice,
            fidelity=fidelity,
            shared=shared,
            applies_to=applies,
            inherits_to_children=shared,
            graph_evaluated=rule.slug in GRAPH_EVALUATED_RULES,
        )


def _all_types_for_practice(practice: str) -> Set[str]:
    out: Set[str] = set()
    for types in FIDELITY_NODE_SCOPE.get(practice, {}).values():
        out.update(types)
    return out


class RuleRegistry:
    def __init__(self) -> None:
        self.rules: List[GraphRule] = []

    def load_from_practices(self) -> None:
        from .guidance_rules_loader import load_graph_rules_from_markdown

        self.rules = load_graph_rules_from_markdown()

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


_REGISTRY: Optional[RuleRegistry] = None


def get_rule_registry() -> RuleRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = RuleRegistry()
        _REGISTRY.load_from_practices()
    return _REGISTRY
