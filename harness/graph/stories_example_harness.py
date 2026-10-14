"""Evaluate story rules against TypeScript .examples stubs."""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

from graph import Node, PracticeGraph, Source
from harness.graph.rule_context import RuleCheckContext


def stories_rule_by_slug(slug: str):
    from practices.stories.rules import BY_SLUG

    rule = BY_SLUG[slug]
    if rule is None:
        raise KeyError(slug)
    return rule


def _story_nodes_from_ts(
    practice: PracticeGraph, source: str, relative: str, *, node_type: str | None = None
) -> list[Node]:
    nodes: list[Node] = []
    for index, name in enumerate(re.findall(r"""story\s*\(\s*['"]([^'"]+)['"]""", source)):
        node_id = f"stories:Story:map.{index}.{name.replace(' ', '_')}"
        node = Node(practice, "Story", node_id, name, Source(relative, 1, 1))
        practice.by_id[node_id] = node
        practice.nodes.setdefault("Story", []).append(node)
        nodes.append(node)
    for index, name in enumerate(re.findall(r"""given\s*\(\s*['"]([^'"]+)['"]""", source)):
        node_id = f"stories:Step:map.given.{index}"
        node = Node(practice, "Given", node_id, name, Source(relative, 1, 1))
        practice.by_id[node_id] = node
        practice.nodes.setdefault("Step", []).append(node)
        nodes.append(node)
    return nodes


def violations_for_story_source(
    rule, source: str, *, relative: str = "faultyAsset.ts", node_type: str | None = None
) -> list[str]:
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    path = root / relative
    path.write_text(source.strip() + "\n", encoding="utf-8")
    practice = PracticeGraph("stories")
    practice.source_root = str(root)
    practice._temp_dir = temp  # type: ignore[attr-defined]
    _story_nodes_from_ts(practice, source, relative)
    if node_type:
        for nodes in practice.nodes.values():
            for node in nodes:
                node.type = node_type
    context = RuleCheckContext(practice, root)
    messages: list[str] = []
    for _node_id, message in rule.check_practice(context):
        messages.append(message)
    for nt in rule.node_types:
        for node in practice.nodes.get(nt, []):
            messages.extend(rule.check(node, context))
    # Story rules often register as Step; match Given/When/Then nodes too.
    if "Step" in rule.node_types:
        for phase in ("Given", "When", "Then"):
            for node in practice.nodes.get(phase, []):
                messages.extend(rule.check(node, context))
    return messages


def assert_stories_ts_pair(
    slug: str,
    fault_source: str,
    clean_source: str,
    *,
    relative: str = "faultyAsset.ts",
    clean_relative: str | None = None,
) -> None:
    rule = stories_rule_by_slug(slug)
    fault_hits = violations_for_story_source(rule, fault_source, relative=relative)
    clean_hits = violations_for_story_source(
        rule, clean_source, relative=clean_relative or relative
    )
    if not fault_hits:
        raise AssertionError(f"{slug}: expected fault violations, got none")
    if clean_hits:
        raise AssertionError(f"{slug}: expected clean, got {clean_hits!r}")


def assert_stories_example_pair(slug: str) -> None:
    root = (
        Path(__file__).resolve().parents[2]
        / "practices/stories/model/typescript/.examples"
        / slug
    )
    fault = (root / "faulty" / "faultyAsset.ts").read_text(encoding="utf-8")
    clean = (root / "repaired" / "repairedAsset.ts").read_text(encoding="utf-8")
    assert_stories_ts_pair(slug, fault, clean)
