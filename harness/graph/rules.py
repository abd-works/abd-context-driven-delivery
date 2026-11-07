"""Run a practice's graph rules and record each violation on the node it was found on."""

from __future__ import annotations

from pathlib import Path

from harness.graph.graph_practice import GraphPractices
from harness.graph.rule_context import RuleCheckContext
from harness.graph.schema_rules import active_overlay_patterns, apply_practice_rules


def attach_rules(practice) -> None:
    """Run every check this practice runs, over the whole practice and then node by node, and record what they find."""
    apply_practice_rules(practice)
    patterns = active_overlay_patterns(tuple(practice.graph.overlays) if practice.graph else ())
    graph_practice = GraphPractices.named(practice.name)
    checks = list(graph_practice.checks(patterns).values())
    if not checks:
        return
    context = RuleCheckContext(practice, Path(practice.source_root) if practice.source_root else None)
    for index, check in enumerate(checks, start=1):
        practice.graph.report_progress(f"{practice.name} · rule {check.slug} · {index}/{len(checks)}")
        for node_id, message in check.check_practice(context):
            node = practice.registered(node_id)
            if node is not None:
                node.rules.record_violation(check.slug, message)
    _check_each_node(practice, graph_practice, patterns, context)


def _check_each_node(practice, graph_practice, patterns: tuple[str, ...], context: RuleCheckContext) -> None:
    """A node another practice's class covers skips the Clean Engineering checks, since Clean Engineering already ran
    them on that class."""
    ce_slugs = frozenset(GraphPractices.named("clean_engineering").checks()) if practice.name != "clean_engineering" else frozenset()
    ce_spans = _clean_engineering_class_spans(practice) if ce_slugs else {}
    nodes = [node for group in practice.nodes.values() for node in group]
    for index, node in enumerate(nodes, start=1):
        practice.graph.report_progress(f"{practice.name} · rules · {index}/{len(nodes)} · {node.type} {node.name}")
        covered = _covered_by_class(node, ce_spans)
        for check in graph_practice.checks_for(node, patterns).values():
            if check.slug not in node.rules.slugs or (covered and check.slug in ce_slugs):
                continue
            practice.graph.report_progress(f"{practice.name} · rule {check.slug} · {index}/{len(nodes)} · {node.name}")
            for message in check.check(node, context):
                node.rules.record_violation(check.slug, message)


def _clean_engineering_class_spans(practice) -> dict[str, list[tuple[int, int]]]:
    """Line spans of the classes the Clean Engineering practice loaded, by file."""
    graph = practice.graph
    if graph is None or "clean_engineering" not in graph.practices:
        return {}
    spans: dict[str, list[tuple[int, int]]] = {}
    for node in graph.practice("clean_engineering").nodes.get("OoadClass", []):
        if node.source.file:
            spans.setdefault(node.source.file.replace("\\", "/"), []).append((node.source.start_line, node.source.end_line))
    return spans


def _covered_by_class(node, spans: dict[str, list[tuple[int, int]]]) -> bool:
    """A node whose lines overlap a Clean Engineering class: CE already reports its class rules there."""
    file = (node.source.file or "").replace("\\", "/")
    start, end = node.source.start_line, node.source.end_line
    return any(start <= class_end and class_start <= end for class_start, class_end in spans.get(file, ()))
