"""JavaScript tier scaffolder - write-once `{story}_test_helper.{tier}.js`.

Every tier is named explicitly, including the baseline (`domain`) - there is
no implicit no-suffix tier file. Each tier file is a skeleton class
implementing the story's helper interface with `not implemented` stubs.
"""

from __future__ import annotations

from typing import Dict, Sequence

from context_tools.stories.code.code_story_map import to_kebab, to_snake
from context_tools.stories.code.javascript.story_file import render_test_helper_file
from context_tools.stories.story_model.nodes import Epic, Story, SubEpic
from context_tools.stories.story_model.story_map import StoryMap


def scaffold_js_tier_tree(
    story_map: StoryMap,
    tiers: Sequence[str],
    *,
    tests_root: str = "tests",
    existing_tree: Dict[str, str] | None = None,
    tier_extensions: Dict[str, str] | None = None,
) -> Dict[str, str]:
    existing = existing_tree or {}
    tree: Dict[str, str] = {}
    root = tests_root.strip("/") or "tests"

    for epic in getattr(story_map, "epics", []) or []:
        _scaffold_epic(epic, tiers=tiers, root=root, tree=tree, existing=existing)

    return {path: body for path, body in tree.items() if path not in existing}


def _scaffold_epic(
    epic: Epic,
    *,
    tiers: Sequence[str],
    root: str,
    tree: Dict[str, str],
    existing: Dict[str, str],
) -> None:
    epic_slug = to_kebab(epic.name)
    for sub in getattr(epic, "sub_epics", []) or []:
        _scaffold_sub_epic(
            sub,
            tiers=tiers,
            parent=f"{root}/{epic_slug}",
            tree=tree,
            existing=existing,
        )


def _scaffold_sub_epic(
    sub: SubEpic,
    *,
    tiers: Sequence[str],
    parent: str,
    tree: Dict[str, str],
    existing: Dict[str, str],
) -> None:
    sub_slug = to_kebab(sub.name)
    folder = f"{parent}/{sub_slug}"
    for nested in getattr(sub, "sub_epics", []) or []:
        _scaffold_sub_epic(
            nested, tiers=tiers, parent=folder, tree=tree, existing=existing
        )
    for story in getattr(sub, "stories", []) or []:
        _scaffold_story(
            story, tiers=tiers, parent=folder, tree=tree, existing=existing
        )


def _scaffold_story(
    story: Story,
    *,
    tiers: Sequence[str],
    parent: str,
    tree: Dict[str, str],
    existing: Dict[str, str],
) -> None:
    if not getattr(story, "scenarios", None):
        return
    story_slug = to_kebab(story.name)
    story_snake = to_snake(story.name)
    story_folder = f"{parent}/{story_slug}"
    for tier in tiers:
        tier_path = f"{story_folder}/{story_snake}_test_helper.{tier}.js"
        tree[tier_path] = render_test_helper_file(story, tier=tier)
