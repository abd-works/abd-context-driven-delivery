"""Run practice graph rules and attach violations on each node's rules collection."""

from __future__ import annotations

from pathlib import Path

from harness.graph.node_rules import attach_node_rules
from harness.graph.practice_rules_registry import checks_for_node, checks_for_practice
from harness.graph.rule_context import RuleCheckContext
from harness.graph.schema_rules import bind_practice_rules, slugs_for_type


def attach_rules(practice) -> None:
    """Run executable checks for this practice and attach violations to each node."""
    bind_practice_rules(practice)
    registry = checks_for_practice(practice.name)
    if not registry:
        return
    root = Path(practice.source_root) if practice.source_root else None
    context = RuleCheckContext(practice, root)
    rows_by_slug: dict[str, list[list[str]]] = {}

    def schema_slugs_for(node) -> frozenset[str]:
        if hasattr(node, "_rules") and node._rules is not None:
            return frozenset(node._rules.slugs())
        return frozenset(slugs_for_type(node.practice.name, node.type))

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

    for check in registry.values():
        for node_id, message in check.check_practice(context):
            record(check.slug, node_id, message)

    for nodes in practice.nodes.values():
        for node in nodes:
            if not hasattr(node, "_rules") or node._rules is None:
                attach_node_rules(node)
            allowed = schema_slugs_for(node)
            for check in checks_for_node(node).values():
                if check.slug not in allowed:
                    continue
                for message in check.check(node, context):
                    record(check.slug, node.node_id, message)

    for slug, rows in rows_by_slug.items():
        practice.apply_rules(slug, rows)
