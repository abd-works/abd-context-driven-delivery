"""Graph predicate evaluators for guidance rules (CodeQL supplies facts; these query edges)."""

from __future__ import annotations

from typing import Dict, List

from practices.stories.model.scenario import Phase

from .graph_node import Kind
from .graph_rules import RuleViolation
from .nodes import GraphExample, GraphScenario, GraphStep
from .practice_graph import PracticeGraph


def evaluate_graph_rule_violations(graph: PracticeGraph) -> Dict[str, List[RuleViolation]]:
    """Return violations keyed by node_id."""
    by_node: Dict[str, List[RuleViolation]] = {}

    def add(node_id: str, violation: RuleViolation) -> None:
        by_node.setdefault(node_id, []).append(violation)

    for scenario in graph.nodes_of_type(GraphScenario):
        has_examples = bool(scenario.examples) or bool(
            graph.outgoing_nodes(scenario, Kind.SCOPES)
        )
        if not has_examples:
            add(
                scenario.node_id,
                RuleViolation(
                    rule_slug="scenario-scopes-example",
                    message="Scenario has no scoped examples.",
                    practice="stories",
                    fidelity="scenarios",
                    node_id=scenario.node_id,
                    location=getattr(getattr(scenario, "source", None), "file", "") or "",
                    line=getattr(getattr(scenario, "source", None), "line", 0) or 0,
                    source="graph",
                ),
            )

    for step in graph.nodes_of_type(GraphStep):
        if step.phase != Phase.WHEN:
            continue
        if graph.outgoing_nodes(step, Kind.INVOKES):
            continue
        add(
            step.node_id,
            RuleViolation(
                rule_slug="gwt-steps-trace-to-domain-operations",
                message="When step has no Step — invokes — Operation edge.",
                practice="stories",
                fidelity="acceptance_tests",
                node_id=step.node_id,
                location=_step_location(step),
                line=_step_line(step),
                source="graph",
            ),
        )

    for example in graph.nodes_of_type(GraphExample):
        if graph.outgoing_nodes(example, Kind.DEMONSTRATES):
            continue
        add(
            example.node_id,
            RuleViolation(
                rule_slug="examples-trace-domain-model",
                message="Example has no Example — demonstrates — Class edge.",
                practice="stories",
                fidelity="acceptance_tests",
                node_id=example.node_id,
                source="graph",
            ),
        )

    return by_node


def _step_location(step: GraphStep) -> str:
    src = getattr(step, "source", None)
    return str(getattr(src, "file", "") or "")


def _step_line(step: GraphStep) -> int:
    src = getattr(step, "source", None)
    return int(getattr(src, "line", 0) or 0)
