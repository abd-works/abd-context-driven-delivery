"""Python tier scaffolder - write-once `*_test_helper.{tier}.py`.

Every tier is named explicitly, including the baseline (`domain`) - there is
no implicit no-suffix tier file.
"""

from __future__ import annotations

from typing import Dict, Sequence

from context_tools.stories.code.code_story_map import to_kebab, to_snake
from context_tools.stories.code.python.story_file import render_test_helper_file
from context_tools.stories.story_model.nodes import Epic, Story, SubEpic
from context_tools.stories.story_model.story_map import StoryMap


def scaffold_py_tier_tree(
    story_map: StoryMap,
    tiers: Sequence[str],
    *,
    tests_root: str = "tests",
    existing_tree: Dict[str, str] | None = None,
) -> Dict[str, str]:
    existing = existing_tree or {}
    tree: Dict[str, str] = {}
    root = tests_root.strip("/") or "tests"

    for epic in getattr(story_map, "epics", []) or []:
        _scaffold_epic(epic, tiers=tiers, root=root, tree=tree)

    return {path: body for path, body in tree.items() if path not in existing}


def _scaffold_epic(
    epic: Epic, *, tiers: Sequence[str], root: str, tree: Dict[str, str]
) -> None:
    for sub in getattr(epic, "sub_epics", []) or []:
        _scaffold_sub_epic(
            sub, tiers=tiers, parent=f"{root}/{to_kebab(epic.name)}", tree=tree
        )


def _scaffold_sub_epic(
    sub: SubEpic, *, tiers: Sequence[str], parent: str, tree: Dict[str, str]
) -> None:
    folder = f"{parent}/{to_kebab(sub.name)}"
    for nested in getattr(sub, "sub_epics", []) or []:
        _scaffold_sub_epic(nested, tiers=tiers, parent=folder, tree=tree)
    for story in getattr(sub, "stories", []) or []:
        _scaffold_story(story, tiers=tiers, parent=folder, tree=tree)


def _scaffold_story(
    story: Story, *, tiers: Sequence[str], parent: str, tree: Dict[str, str]
) -> None:
    if not getattr(story, "scenarios", None):
        return
    story_folder = f"{parent}/{to_kebab(story.name)}"
    story_snake = to_snake(story.name)
    for tier in tiers:
        path = f"{story_folder}/{story_snake}_test_helper.{tier}.py"
        tree[path] = render_test_helper_file(story, tier=tier)
