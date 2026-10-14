"""BDD rule checks on python spec fixtures."""

from __future__ import annotations

import tempfile
from pathlib import Path

from graph import Node, PracticeGraph, Source
from harness.graph.rule_context import RuleCheckContext


def bdd_rule_by_slug(slug: str):
    from practices.bdd.rules import BY_SLUG

    return BY_SLUG[slug]


def violations_for_spec_source(rule, source: str, *, filename: str = "widget_spec.py") -> list[str]:
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    path = root / filename
    path.write_text(source.strip() + "\n", encoding="utf-8")
    practice = PracticeGraph("bdd")
    practice.source_root = str(root)
    practice._temp_dir = temp  # type: ignore[attr-defined]
    node = Node(
        practice,
        "Spec",
        f"bdd:Spec:{filename}:widget",
        "widget",
        Source(filename, 1, max(1, source.count("\n"))),
    )
    practice.by_id[node.node_id] = node
    practice.nodes.setdefault("Spec", []).append(node)
    context = RuleCheckContext(practice, root)
    return list(rule.check(node, context))


def assert_bdd_source_pair(slug: str, fault: str, clean: str, *, filename: str = "widget_spec.py") -> None:
    rule = bdd_rule_by_slug(slug)
    fault_hits = violations_for_spec_source(rule, fault, filename=filename)
    clean_hits = violations_for_spec_source(rule, clean, filename=filename)
    if not fault_hits:
        raise AssertionError(f"{slug}: expected fault violations")
    if clean_hits:
        raise AssertionError(f"{slug}: expected clean, got {clean_hits!r}")
