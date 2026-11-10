"""Attach a schema-backed rules collection when a node is registered."""

from __future__ import annotations

from harness.graph.graph_rules_collection import GraphRule, GraphRulesCollection
from harness.graph.guidance_prose_index import prose_by_slug
from harness.graph.practice_rules_registry import checks_for_practice
from harness.graph.schema_rules import active_overlay_patterns, slugs_for_type


def attach_node_rules(node) -> GraphRulesCollection:
    """Schema slugs on this node → GraphRule entries (prose + optional check class)."""
    overlays = tuple(node.practice.graph.overlays) if node.practice.graph else ()
    patterns = active_overlay_patterns(overlays)
    slugs = slugs_for_type(node.practice.name, node.type, patterns)
    checks = checks_for_practice(node.practice.name, patterns)
    prose = prose_by_slug(node.practice.name, patterns)
    entries: dict[str, GraphRule] = {}
    for slug in slugs:
        body = prose.get(slug, "")
        check = checks.get(slug)
        if check is not None:
            entries[slug] = GraphRule.from_check(check, body=body)
        else:
            entries[slug] = GraphRule.prose_only(slug, body=body, node_types=(node.type,))
    collection = GraphRulesCollection(node, entries)
    node._rules = collection
    return collection
