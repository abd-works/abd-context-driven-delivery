"""Evaluate guidance rules on a loaded practice graph."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from .codeql_export import load_codeql_export, resolve_codeql_results_path
from .graph_node import GraphNodeMixin
from .graph_rules import RuleViolation, closest_fidelity, get_rule_registry
from .rule_evaluators import evaluate_graph_rule_violations


def evaluate_rules(
    graph,
    root: Path,
    *,
    codeql_results: Path | None = None,
) -> None:
    """Bind guidance rules and evaluate graph + CodeQL violations onto nodes."""
    registry = get_rule_registry()
    graph.rule_registry = registry  # type: ignore[attr-defined]

    by_node = evaluate_graph_rule_violations(graph)
    _merge_codeql_violations(graph, root, by_node, codeql_results)

    for node_id, violations in by_node.items():
        node = graph.nodes.get(node_id)
        if node is None:
            continue
        for violation in violations:
            violation.direct = _is_direct_violation(node, violation, registry)

    graph._violations_by_node = by_node  # type: ignore[attr-defined]


def _is_direct_violation(node: GraphNodeMixin, violation: RuleViolation, registry) -> bool:
    closest = closest_fidelity(node.practice, node._semantic_type_name)
    if violation.fidelity is not None:
        return violation.fidelity == closest
    return violation.practice == node.practice


def _merge_codeql_violations(
    graph,
    root: Path,
    by_node: Dict[str, List[RuleViolation]],
    codeql_results: Path | None,
) -> None:
    export_path = resolve_codeql_results_path(root, codeql_results)
    if export_path is None:
        return
    export = load_codeql_export(export_path)
    for entry in export.rule_violations:
        node = _resolve_violation_node(graph, entry)
        if node is None:
            continue
        violation = RuleViolation(
            rule_slug=entry.rule_slug,
            message=entry.message,
            practice=entry.practice,
            fidelity=entry.fidelity or None,
            node_id=node.node_id,
            location=entry.file,
            line=entry.line,
            source="codeql",
        )
        by_node.setdefault(node.node_id, []).append(violation)


def _resolve_violation_node(graph, entry):
    if entry.node_id and entry.node_id in graph.nodes:
        return graph.nodes[entry.node_id]
    for node in graph.nodes.values():
        if node._semantic_type_name != entry.semantic_type:
            continue
        if node.name != entry.node_name:
            continue
        return node
    return None


def filter_violations(
    graph,
    node: GraphNodeMixin,
    *,
    practice: Optional[str] = None,
    fidelity: Optional[str] = None,
    direct_only: bool = False,
) -> List[RuleViolation]:
    all_for_node: List[RuleViolation] = list(
        graph._violations_by_node.get(node.node_id, [])  # type: ignore[attr-defined]
    )
    inherited = _inherited_violations(graph, node)
    combined = _dedupe_violations(all_for_node + inherited)

    registry = getattr(graph, "rule_registry", None) or get_rule_registry()
    result: List[RuleViolation] = []
    closest = closest_fidelity(node.practice, node._semantic_type_name)

    for v in combined:
        if practice is not None and v.practice != practice:
            continue
        if fidelity is not None and v.fidelity != fidelity:
            continue
        if direct_only:
            if v.fidelity != closest:
                continue
        result.append(v)
    return result


def _inherited_violations(graph, node: GraphNodeMixin) -> List[RuleViolation]:
    from .graph_node import Kind

    inherited: List[RuleViolation] = []
    for parent, kind in graph.incoming(node, Kind.OWNS):
        del kind
        if not isinstance(parent, GraphNodeMixin):
            continue
        parent_v = graph._violations_by_node.get(parent.node_id, [])  # type: ignore[attr-defined]
        for v in parent_v:
            if v.rule_slug in ("scenario-scopes-example",):
                continue
            inherited.append(v)
        inherited.extend(_inherited_violations(graph, parent))
    return inherited


def _dedupe_violations(violations: List[RuleViolation]) -> List[RuleViolation]:
    seen: set[tuple] = set()
    out: List[RuleViolation] = []
    for v in violations:
        key = (v.rule_slug, v.node_id, v.message)
        if key in seen:
            continue
        seen.add(key)
        out.append(v)
    return out
