"""Run practice graph rules and attach violations on each node's rules collection."""

from __future__ import annotations

from pathlib import Path

from harness.graph.node_rules import attach_node_rules
from harness.graph.practice_rules_registry import checks_for_node, checks_for_practice
from harness.graph.rule_context import RuleCheckContext
from harness.graph.schema_rules import active_overlay_patterns, bind_practice_rules, slugs_for_type


def attach_rules(practice) -> None:
    """Run executable checks for this practice and attach violations to each node."""
    bind_practice_rules(practice)
    overlays = tuple(practice.graph.overlays) if practice.graph else ()
    patterns = active_overlay_patterns(overlays)
    registry = checks_for_practice(practice.name, patterns)
    if not registry:
        return
    root = Path(practice.source_root) if practice.source_root else None
    context = RuleCheckContext(practice, root)
    rows_by_slug: dict[str, list[list[str]]] = {}

    def schema_slugs_for(node) -> frozenset[str]:
        if hasattr(node, "_rules") and node._rules is not None:
            return frozenset(node._rules.slugs())
        overlays = tuple(node.practice.graph.overlays) if node.practice.graph else ()
        return frozenset(slugs_for_type(node.practice.name, node.type, active_overlay_patterns(overlays)))

    def record(slug: str, node_id: str, message: str) -> None:
        node = practice.registered(node_id)
        if node is None:
            return
        if slug not in schema_slugs_for(node):
            return
        if not hasattr(node, "_rules") or node._rules is None:
            attach_node_rules(node)
        node._rules.record_violation(slug, message)
        rows_by_slug.setdefault(slug, []).append([slug, node_id, message])

    checks = list(registry.values())
    for index, check in enumerate(checks, start=1):
        practice.graph.report_progress(f"{practice.name} · rule {check.slug} · {index}/{len(checks)}")
        for node_id, message in check.check_practice(context):
            record(check.slug, node_id, message)

    ce_slugs = _clean_engineering_slugs() if practice.name != "clean_engineering" else frozenset()
    ce_spans = _clean_engineering_class_spans(practice) if ce_slugs else {}
    nodes = [node for group in practice.nodes.values() for node in group]
    for index, node in enumerate(nodes, start=1):
        practice.graph.report_progress(f"{practice.name} · rules · {index}/{len(nodes)} · {node.type} {node.name}")
        if not hasattr(node, "_rules") or node._rules is None:
            attach_node_rules(node)
        allowed = schema_slugs_for(node)
        reported_by_clean_engineering = _covered_by_class(node, ce_spans)
        for check in checks_for_node(node).values():
            if check.slug not in allowed:
                continue
            if reported_by_clean_engineering and check.slug in ce_slugs:
                continue
            practice.graph.report_progress(
                f"{practice.name} · rule {check.slug} · {index}/{len(nodes)} · {node.name}"
            )
            for message in check.check(node, context):
                record(check.slug, node.node_id, message)

    for slug, rows in rows_by_slug.items():
        practice.apply_rules(slug, rows)


def _clean_engineering_slugs() -> frozenset[str]:
    """Slugs whose checks Clean Engineering runs itself on its own class nodes."""
    return frozenset(checks_for_practice("clean_engineering"))


def _clean_engineering_class_spans(practice) -> dict[str, list[tuple[int, int]]]:
    """Line spans of the classes the Clean Engineering practice loaded, by file."""
    graph = practice.graph
    if graph is None or "clean_engineering" not in graph.practices:
        return {}
    spans: dict[str, list[tuple[int, int]]] = {}
    for node in graph.practice("clean_engineering").by_id.values():
        if node.type != "OoadClass" or not node.source.file:
            continue
        spans.setdefault(node.source.file.replace("\\", "/"), []).append((node.source.start_line, node.source.end_line))
    return spans


def _covered_by_class(node, spans: dict[str, list[tuple[int, int]]]) -> bool:
    """A node whose lines overlap a Clean Engineering class: CE already reports its class rules there."""
    file = (node.source.file or "").replace("\\", "/")
    start, end = node.source.start_line, node.source.end_line
    return any(start <= class_end and class_start <= end for class_start, class_end in spans.get(file, ()))
