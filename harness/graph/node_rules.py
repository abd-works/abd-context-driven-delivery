"""Attach a schema-backed rules collection when a node is registered."""

from __future__ import annotations

from harness.graph.graph_practice import GraphPractices
from harness.graph.graph_rules_collection import GraphRule, GraphRulesCollection
from harness.graph.guidance_prose_index import prose_by_slug
from harness.graph.schema_rules import active_overlay_patterns, slugs_for_type


def attach_node_rules(node) -> GraphRulesCollection:
    """Schema slugs on this node become GraphRule entries, each with its prose and, when one exists, its check."""
    overlays = tuple(node.practice.graph.overlays) if node.practice.graph else ()
    patterns = active_overlay_patterns(overlays)
    checks = GraphPractices.named(node.practice.name).checks(patterns)
    prose = prose_by_slug(node.practice.name, patterns)
    entries: dict[str, GraphRule] = {}
    for slug in slugs_for_type(node.practice.name, node.type, patterns):
        check = checks.get(slug)
        node_types = tuple(check.node_types) if check is not None else (node.type,)
        entries[slug] = GraphRule(node, slug, body=prose.get(slug, ""), node_types=node_types, check=check)
    collection = GraphRulesCollection(node, entries)
    node._rules = collection
    return collection
