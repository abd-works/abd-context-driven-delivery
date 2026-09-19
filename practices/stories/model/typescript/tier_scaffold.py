"""TypeScript scaffolder - write-once `{story_snake}_story.test.ts` under the sub-epic."""

from __future__ import annotations

from typing import Dict, Sequence

from practices.stories.model.code_story_map import to_kebab, to_snake
from practices.stories.model.typescript.story_file import (
    render_story_file,
    render_test_helper_file,
    story_test_import_path,
)
from practices.stories.model.typescript.tree import DEFAULT_TIERS
from practices.stories.model.nodes import SubEpic
from practices.stories.model.story_map import StoryMap


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
                deploy_root=root,
                tree=tree,
            )
    return {p: b for p, b in tree.items() if p not in existing}


def _scaffold_sub(
    sub: SubEpic,
    *,
    tiers: Sequence[str],
    parent: str,
    deploy_root: str,
    tree: Dict[str, str],
) -> None:
    folder = f"{parent}/{to_kebab(sub.name)}"
    for nested in getattr(sub, "sub_epics", []) or []:
        _scaffold_sub(
            nested, tiers=tiers, parent=folder, deploy_root=deploy_root, tree=tree
        )
    for story in getattr(sub, "stories", []) or []:
        if not story.scenarios:
            continue
        gwt = render_story_file(
            story, story_test_import_path=story_test_import_path(deploy_root)
        )
        path = f"{folder}/{to_snake(story.name)}_story.test.ts"
        tree[path] = gwt + render_test_helper_file(story, tier="", same_file=True)
