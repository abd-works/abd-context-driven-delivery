"""Attach a schema-backed rules collection when a node is registered."""

from __future__ import annotations

from harness.graph.graph_rules_collection import GraphRule, GraphRulesCollection
from harness.graph.practice_rules_registry import checks_for_practice
from harness.graph.schema_rules import slugs_for_type


def attach_node_rules(node) -> GraphRulesCollection:
    """Build the rules collection for this node type from schema.yaml and practice checks."""
    slugs = slugs_for_type(node.practice.name, node.type)
    checks = checks_for_practice(node.practice.name)
    entries: dict[str, GraphRule] = {}
    for slug in slugs:
        check = checks.get(slug)
        if check is not None:
            entries[slug] = GraphRule.from_check(check)
        else:
            entries[slug] = GraphRule.prompt_only(slug, node_types=(node.type,))
    collection = GraphRulesCollection(node, entries)
    node._rules = collection
    return collection
