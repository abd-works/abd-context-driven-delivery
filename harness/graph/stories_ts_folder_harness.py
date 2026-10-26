"""Story rules on TypeScript .examples trees (multi-file fixtures)."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from graph import Node, PracticeGraph, Source
from harness.graph.rule_context import RuleCheckContext
from harness.graph.stories_example_harness import stories_rule_by_slug


def _practice_from_folder(folder: Path, *, relative_file: str) -> tuple[PracticeGraph, Path, Node]:
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    for item in folder.rglob("*"):
        if item.is_file():
            target = root / item.relative_to(folder)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
    practice = PracticeGraph("stories")
    practice.source_root = str(root)
    practice._temp_dir = temp  # type: ignore[attr-defined]
    rel = relative_file.replace("\\", "/")
    text = (root / rel).read_text(encoding="utf-8") if (root / rel).is_file() else ""
    node = Node(
        practice,
        "Example",
        f"stories:Example:{rel}:fixture",
        Path(rel).stem,
        Source(rel, 1, max(1, text.count("\n"))),
    )
    practice.by_id[node.node_id] = node
    practice.nodes.setdefault("Example", []).append(node)
    _load_file_facts(node, root, rel)
    return practice, root, node


def _load_file_facts(node: Node, root: Path, relative: str) -> None:
    """The facts the story model loads for a story file, set on the fixture node as a live build sets them."""
    from cdd_guidance.practices.stories.model.graph_story_model import GraphStoryModel
    from cdd_guidance.practices.stories.model.story_model import StoryModel

    for name, value in GraphStoryModel(StoryModel())._file_facts(str(root), relative).items():
        node.set_fact(name, value)


def assert_stories_folder_pair(
    slug: str,
    example_slug: str,
    relative_file: str,
    *,
    node_type: str = "Example",
) -> None:
    base = (
        Path(__file__).resolve().parents[2]
        / "cdd_guidance/practices/stories/model/typescript/_examples"
        / example_slug
    )
    rule = stories_rule_by_slug(slug)
    for kind, expect_fault in (("faulty", True), ("repaired", False)):
        folder = base / kind
        practice, root, node = _practice_from_folder(folder, relative_file=relative_file)
        node.type = node_type
        context = RuleCheckContext(practice, root)
        hits = list(rule.check(node, context))
        if expect_fault and not hits:
            raise AssertionError(f"{slug}/{kind}: expected violations on {relative_file}")
        if not expect_fault and hits:
            raise AssertionError(f"{slug}/{kind}: expected clean, got {hits!r}")
