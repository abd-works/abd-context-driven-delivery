"""Spec support: evaluate story rules against TypeScript .examples stubs, one source or a folder of files."""

from __future__ import annotations

import re
import shutil
import tempfile
from pathlib import Path

from harness.graph.graph import Graph, Node, PracticeGraph, Source
from harness.graph.rule_context import RuleCheckContext

_EXAMPLES = Path(__file__).resolve().parents[1] / "model" / "typescript" / "_examples"


def stories_rule_by_slug(slug: str):
    from cdd_guidance.practices.stories.rules import BY_SLUG

    rule = BY_SLUG[slug]
    if rule is None:
        raise KeyError(slug)
    return rule


def _record_stories(practice: PracticeGraph, names: list[str], relative: str) -> list[Node]:
    """Record the stories through the story model, so each Story node carries the facts a live build loads."""
    from cdd_guidance.practices.stories.model.graph_story_model import GraphStoryModel
    from cdd_guidance.practices.stories.model.source_location import SourceLocation
    from cdd_guidance.practices.stories.model.story_model import Epic, Story, StoryModel

    if not names:
        return []
    model = StoryModel()
    epic = Epic("Submit Fixture Stories", 1)
    for index, name in enumerate(names, start=1):
        story = Story(name, index)
        story.source = SourceLocation(relative, 1, 1)
        epic.append_story(story)
    model.append_epic(epic)
    GraphStoryModel(model).record(practice)
    return list(practice.nodes.get("Story", []))


def _story_nodes_from_ts(
    practice: PracticeGraph, source: str, relative: str, *, node_type: str | None = None
) -> list[Node]:
    from cdd_guidance.practices.stories.model.story_model import Step, StepType

    names = re.findall(r"""story\s*\(\s*['"]([^'"]+)['"]""", source)
    nodes: list[Node] = _record_stories(practice, names, relative)
    for index, name in enumerate(re.findall(r"""given\s*\(\s*['"]([^'"]+)['"]""", source)):
        step = Step(name, StepType.GIVEN, index + 1, keyword="Given")
        step.type = "Given"
        nodes.append(practice.add(step, f"stories:Step:map.given.{index}", relative, 1, 1))
    return nodes


def violations_for_story_source(
    rule, source: str, *, relative: str = "faultyAsset.ts", node_type: str | None = None
) -> list[str]:
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    path = root / relative
    path.write_text(source.strip() + "\n", encoding="utf-8")
    practice = Graph().practice("stories")
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
    root = _EXAMPLES / slug
    fault = (root / "faulty" / "faultyAsset.ts").read_text(encoding="utf-8")
    clean = (root / "repaired" / "repairedAsset.ts").read_text(encoding="utf-8")
    assert_stories_ts_pair(slug, fault, clean)


def _practice_from_folder(folder: Path, *, relative_file: str) -> tuple[PracticeGraph, Path, Node]:
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    for item in folder.rglob("*"):
        if item.is_file():
            target = root / item.relative_to(folder)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
    practice = Graph().practice("stories")
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
    base = _EXAMPLES / example_slug
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
