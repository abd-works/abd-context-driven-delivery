"""Node.rules — violation query surface on graph nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .graph_rules import RuleViolation, closest_fidelity, get_rule_registry

if TYPE_CHECKING:
    from .graph_node import GraphNodeMixin
    from .practice_graph import PracticeGraph


class NodeRulesPracticeView:
    def __init__(self, node: "GraphNodeMixin", graph: "PracticeGraph", practice: str) -> None:
        self._node = node
        self._graph = graph
        self._practice = practice

    def fidelity(self, name: str) -> "NodeRulesFidelityView":
        return NodeRulesFidelityView(self._node, self._graph, self._practice, name)

    @property
    def shared(self) -> "NodeRulesFidelityView":
        return NodeRulesFidelityView(self._node, self._graph, self._practice, None)


class NodeRulesFidelityView:
    def __init__(
        self,
        node: "GraphNodeMixin",
        graph: "PracticeGraph",
        practice: str,
        fidelity: Optional[str],
    ) -> None:
        self._node = node
        self._graph = graph
        self._practice = practice
        self._fidelity = fidelity

    @property
    def violations(self) -> List[RuleViolation]:
        return self._graph.violations_for_node(
            self._node,
            practice=self._practice,
            fidelity=self._fidelity,
            direct_only=False,
        )


class NodeRulesDirectView:
    def __init__(self, node: "GraphNodeMixin", graph: "PracticeGraph") -> None:
        self._node = node
        self._graph = graph

    @property
    def violations(self) -> List[RuleViolation]:
        return self._graph.violations_for_node(
            self._node,
            practice=None,
            fidelity=None,
            direct_only=True,
        )


class NodeRulesView:
    def __init__(self, node: "GraphNodeMixin") -> None:
        self._node = node

    @property
    def graph(self) -> "PracticeGraph":
        return self._node.graph

    @property
    def violations(self) -> List[RuleViolation]:
        return self.graph.violations_for_node(
            self._node,
            practice=None,
            fidelity=None,
            direct_only=False,
        )

    @property
    def direct(self) -> NodeRulesDirectView:
        return NodeRulesDirectView(self._node, self.graph)

    def practice(self, name: str) -> NodeRulesPracticeView:
        return NodeRulesPracticeView(self._node, self.graph, name)

    @property
    def closest_fidelity(self) -> Optional[str]:
        return closest_fidelity(self._node.practice, self._node._semantic_type_name)

    @property
    def applicable_rule_slugs(self) -> List[str]:
        registry = get_rule_registry()
        rules = registry.rules_for_node(
            practice=self._node.practice,
            semantic_type=self._node._semantic_type_name,
        )
        return [r.slug for r in rules]
