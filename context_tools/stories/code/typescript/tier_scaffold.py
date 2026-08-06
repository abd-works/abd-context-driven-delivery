"""TypeScript tier scaffolder - write-once `*_test_helper.{tier}.ts` per tier.

Every tier is named explicitly, including the baseline (`domain`) - there is
no implicit no-suffix tier file. The `{story}_story.ts` file (no suffix) is
the scenario-fidelity GWT/requirements file, not a tier file, and is rendered
separately (see `tree.py`).
"""

from __future__ import annotations

from typing import Dict, Sequence

from context_tools.stories.code.code_story_map import to_kebab, to_snake
from context_tools.stories.code.typescript.story_file import render_test_helper_file
from context_tools.stories.story_model.nodes import Epic, Story, SubEpic
from context_tools.stories.story_model.story_map import StoryMap


def scaffold_ts_tier_tree(
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
        for sub in getattr(epic, "sub_epics", []) or []:
            _scaffold_sub(
                sub,
                tiers=tiers,
                parent=f"{root}/{to_kebab(epic.name)}",
                tree=tree,
            )
    return {p: b for p, b in tree.items() if p not in existing}


def _scaffold_sub(
    sub: SubEpic, *, tiers: Sequence[str], parent: str, tree: Dict[str, str]
) -> None:
    folder = f"{parent}/{to_kebab(sub.name)}"
    for nested in getattr(sub, "sub_epics", []) or []:
        _scaffold_sub(nested, tiers=tiers, parent=folder, tree=tree)
    for story in getattr(sub, "stories", []) or []:
        if not story.scenarios:
            continue
        story_folder = f"{folder}/{to_kebab(story.name)}"
        snake = to_snake(story.name)
        for tier in tiers:
            path = f"{story_folder}/{snake}_test_helper.{tier}.ts"
            tree[path] = render_test_helper_file(story, tier=tier)
