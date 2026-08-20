"""TypeScript tier scaffolder - write-once `{story}.{tier}.ts` under the sub-epic."""

from __future__ import annotations

from typing import Dict, Sequence

from context_tools.stories.code.code_story_map import to_kebab
from context_tools.stories.code.typescript.story_file import (
    render_story_file,
    render_test_helper_file,
)
from context_tools.stories.code.typescript.tree import DEFAULT_TIERS
from context_tools.stories.story_model.nodes import SubEpic
from context_tools.stories.story_model.story_map import StoryMap


def scaffold_ts_tier_tree(
    story_map: StoryMap,
    tiers: Sequence[str] | None = None,
    *,
    tests_root: str = "tests",
    existing_tree: Dict[str, str] | None = None,
) -> Dict[str, str]:
    existing = existing_tree or {}
    tree: Dict[str, str] = {}
    root = tests_root.strip("/") or "tests"
    seam_tiers = tuple(tiers) if tiers else DEFAULT_TIERS
    for epic in getattr(story_map, "epics", []) or []:
        for sub in getattr(epic, "sub_epics", []) or []:
            _scaffold_sub(
                sub,
                tiers=seam_tiers,
                parent=f"{root}/{to_kebab(epic.name)}",
                depth=2,
                tree=tree,
            )
    return {p: b for p, b in tree.items() if p not in existing}


def _scaffold_sub(
    sub: SubEpic,
    *,
    tiers: Sequence[str],
    parent: str,
    depth: int,
    tree: Dict[str, str],
) -> None:
    folder = f"{parent}/{to_kebab(sub.name)}"
    for nested in getattr(sub, "sub_epics", []) or []:
        _scaffold_sub(
            nested, tiers=tiers, parent=folder, depth=depth + 1, tree=tree
        )
    for story in getattr(sub, "stories", []) or []:
        if not story.scenarios:
            continue
        slug = to_kebab(story.name)
        relative_test = "../" * depth + "story-test"
        gwt = render_story_file(story, relative_story_test_path=relative_test)
        for tier in tiers:
            path = f"{folder}/{slug}.{tier}.ts"
            tree[path] = gwt + render_test_helper_file(story, tier=tier, same_file=True)
