"""Node.rules — one query object on the node."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .graph_node import Kind, Node
from .graph_rules import RuleViolation, closest_fidelity

if TYPE_CHECKING:
    from .practice_graph import PracticeGraph


class NodeRules:
    def __init__(
        self,
        node: Node,
        *,
        practice: Optional[str] = None,
        fidelity: Optional[str] = None,
        rule_slug: Optional[str] = None,
        direct_only: bool = False,
    ) -> None:
        self._node = node
        self._practice = practice
        self._fidelity = fidelity
        self._rule_slug = rule_slug
        self._direct_only = direct_only

    @property
    def graph(self) -> "PracticeGraph":
        return self._node.graph

    @property
    def violations(self) -> List[RuleViolation]:
        hits = _matching(self._node, self.graph)
        if self._practice is not None:
            hits = [hit for hit in hits if hit.practice == self._practice]
        if self._fidelity is not None:
            hits = [hit for hit in hits if hit.fidelity == self._fidelity]
        if self._direct_only:
            closest = closest_fidelity(self._node.practice, self._node._semantic_type_name)
            hits = [hit for hit in hits if hit.fidelity == closest]
        if self._rule_slug is not None:
            hits = [hit for hit in hits if hit.rule_slug == self._rule_slug]
        return hits

    @property
    def direct(self) -> "NodeRules":
        return NodeRules(self._node, direct_only=True)

    def practice(self, name: str) -> "NodeRules":
        return NodeRules(self._node, practice=name)

    def fidelity(self, name: str) -> "NodeRules":
        return NodeRules(
            self._node,
            practice=self._practice,
            fidelity=name,
        )

    def slug(self, name: str) -> "NodeRules":
        return NodeRules(self._node, rule_slug=name)

    @property
    def closest_fidelity(self) -> Optional[str]:
        return closest_fidelity(self._node.practice, self._node._semantic_type_name)

    @property
    def applicable_rule_slugs(self) -> List[str]:
        rules = self.graph.rule_registry.rules_for_node(
            practice=self._node.practice,
            semantic_type=self._node._semantic_type_name,
        )
        return [rule.slug for rule in rules]


def _matching(node: Node, graph: "PracticeGraph") -> List[RuleViolation]:
    combined = _dedupe(
        list(graph._violations_by_node.get(node.node_id, []))
        + _inherited(node, graph)
    )
    return combined


def _inherited(node: Node, graph: "PracticeGraph") -> List[RuleViolation]:
    inherited: List[RuleViolation] = []
    for parent in node.related(Kind.OWNS, direction="in"):
        for violation in graph._violations_by_node.get(parent.node_id, []):
            if violation.rule_slug in (
                "scenario-scopes-example",
                "keep-classes-single-responsibility",
            ):
                continue
            inherited.append(violation)
        inherited.extend(_inherited(parent, graph))
    return inherited


def _dedupe(violations: List[RuleViolation]) -> List[RuleViolation]:
    seen: set[tuple] = set()
    out: List[RuleViolation] = []
    for violation in violations:
        key = (violation.rule_slug, violation.node_id, violation.message)
        if key in seen:
            continue
        seen.add(key)
        out.append(violation)
    return out
