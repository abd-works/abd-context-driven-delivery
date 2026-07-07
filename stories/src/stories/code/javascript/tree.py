"""JavaScript tree renderer — full file tree for a Workspace.

Mirrors `typescript/tree.py` with `.js` extensions and JSDoc-typed shared
modules. `story-types.js` and `story-runner.js` are copied verbatim from the
templates directory.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

from stories.src.stories.code.code_story_map import to_kebab
from stories.src.stories.code.javascript.spec_file import render_story_spec_file
from stories.src.stories.model.nodes import Epic, Story, SubEpic
from stories.src.stories.model.story_map import StoryMap


TEMPLATES_DIR = Path(__file__).resolve().parents[5] / "templates" / "js"


def render_js_tree(
    story_map: StoryMap,
    *,
    tests_root: str = "tests",
    include_shared: bool = True,
) -> Dict[str, str]:
    tree: Dict[str, str] = {}
    root = tests_root.strip("/") or "tests"

    if include_shared:
        types_body, runner_body = _read_shared_templates()
        tree[f"{root}/story-types.js"] = types_body
        tree[f"{root}/story-runner.js"] = runner_body

    for epic in getattr(story_map, "epics", []) or []:
        _render_epic(epic, root=root, tree=tree)
    return tree


def _render_epic(epic: Epic, *, root: str, tree: Dict[str, str]) -> None:
    epic_slug = to_kebab(epic.name)
    for sub in getattr(epic, "sub_epics", []) or []:
        _render_sub_epic(sub, parent=f"{root}/{epic_slug}", depth=2, tree=tree)


def _render_sub_epic(sub: SubEpic, *, parent: str, depth: int, tree: Dict[str, str]) -> None:
    sub_slug = to_kebab(sub.name)
    folder = f"{parent}/{sub_slug}"
    for nested in getattr(sub, "sub_epics", []) or []:
        _render_sub_epic(nested, parent=folder, depth=depth + 1, tree=tree)
    for story in getattr(sub, "stories", []) or []:
        _render_story(story, parent=folder, depth=depth + 1, tree=tree)


def _render_story(story: Story, *, parent: str, depth: int, tree: Dict[str, str]) -> None:
    if not getattr(story, "scenarios", None):
        return
    story_slug = to_kebab(story.name)
    story_folder = f"{parent}/{story_slug}"
    relative_types_path = "../" * depth + "story-types"
    tree[f"{story_folder}/{story_slug}-stories.js"] = render_story_spec_file(
        story, relative_types_path=relative_types_path
    )


def _read_shared_templates() -> Tuple[str, str]:
    return (
        (TEMPLATES_DIR / "story-types.js").read_text(encoding="utf-8"),
        (TEMPLATES_DIR / "story-runner.js").read_text(encoding="utf-8"),
    )
