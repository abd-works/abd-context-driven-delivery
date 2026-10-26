"""BDD rule checks on spec fixtures, loaded through the real working-copy build.

The spec file's language model parses its describe tree and every node loads its own facts;
rules read only those facts.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from harness.graph.graph import Graph
from harness.graph.rule_context import RuleCheckContext


def bdd_rule_by_slug(slug: str):
    from cdd_guidance.practices.bdd.rules import BY_SLUG

    return BY_SLUG[slug]


def violations_for_spec_source(rule, source: str, *, filename: str = "widget_spec.py") -> list[str]:
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    (root / filename).write_text(source.strip() + "\n", encoding="utf-8")
    graph = Graph()
    graph.load_working_copy(str(root), {"bdd": str(root)}, force=True)
    practice = graph.practice("bdd")
    practice._temp_dir = temp  # type: ignore[attr-defined]
    context = RuleCheckContext(practice, root)
    return [
        message
        for node_type in rule.node_types
        for node in practice.nodes.get(node_type, [])
        for message in rule.check(node, context)
    ]


def assert_bdd_source_pair(slug: str, fault: str, clean: str, *, filename: str = "widget_spec.py") -> None:
    rule = bdd_rule_by_slug(slug)
    fault_hits = violations_for_spec_source(rule, fault, filename=filename)
    clean_hits = violations_for_spec_source(rule, clean, filename=filename)
    if not fault_hits:
        raise AssertionError(f"{slug}: expected fault violations")
    if clean_hits:
        raise AssertionError(f"{slug}: expected clean, got {clean_hits!r}")
