"""Python tree renderer — emits the full expected file tree for a Workspace.

Layout produced:

    <tests-root>/
      story_types.py           (shared, verbatim from templates/py)
      story_runner.py          (shared, verbatim from templates/py)
      conftest.py              (adds <tests-root> to sys.path so kebab-case
                                folders don't get in the way of importing the
                                shared modules by name)
      <epic-slug>/
        <sub-epic-slug>/
          <story-slug>/
            <story_slug>_stories.py

Tier files are emitted by `tier_scaffold.py` and are write-once.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

from stories.code.code_story_map import to_kebab
from stories.code.python.spec_file import render_story_spec_file
from stories.story_model.nodes import Epic, Story, SubEpic
from stories.story_model.story_map import StoryMap


TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "py"

CONFTEST_BODY = '''"""Test-root conftest.

Adds this directory to `sys.path` so kebab-case folder names don't block
imports of the shared `story_types` and `story_runner` modules. Each story
folder's spec + tier files import those siblings by name.
"""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
'''


def render_py_tree(
    story_map: StoryMap,
    *,
    tests_root: str = "tests",
    include_shared: bool = True,
) -> Dict[str, str]:
    """Render the full expected Python tree for a StoryMap."""
    tree: Dict[str, str] = {}
    root = tests_root.strip("/") or "tests"

    if include_shared:
        types_body, runner_body = _read_shared_templates()
        tree[f"{root}/story_types.py"] = types_body
        tree[f"{root}/story_runner.py"] = runner_body
        tree[f"{root}/conftest.py"] = CONFTEST_BODY

    for epic in getattr(story_map, "epics", []) or []:
        _render_epic(epic, root=root, tree=tree)
    return tree


def _render_epic(epic: Epic, *, root: str, tree: Dict[str, str]) -> None:
    epic_slug = to_kebab(epic.name)
    for sub in getattr(epic, "sub_epics", []) or []:
        _render_sub_epic(sub, parent=f"{root}/{epic_slug}", tree=tree)


def _render_sub_epic(sub: SubEpic, *, parent: str, tree: Dict[str, str]) -> None:
    sub_slug = to_kebab(sub.name)
    folder = f"{parent}/{sub_slug}"
    for nested in getattr(sub, "sub_epics", []) or []:
        _render_sub_epic(nested, parent=folder, tree=tree)
    for story in getattr(sub, "stories", []) or []:
        _render_story(story, parent=folder, tree=tree)


def _render_story(story: Story, *, parent: str, tree: Dict[str, str]) -> None:
    if not getattr(story, "scenarios", None):
        return
    story_slug_kebab = to_kebab(story.name)
    story_slug_snake = story_slug_kebab.replace("-", "_")
    story_folder = f"{parent}/{story_slug_kebab}"
    tree[f"{story_folder}/{story_slug_snake}_stories.py"] = render_story_spec_file(story)


def _read_shared_templates() -> Tuple[str, str]:
    types_path = TEMPLATES_DIR / "story_types.py"
    runner_path = TEMPLATES_DIR / "story_runner.py"
    return (
        types_path.read_text(encoding="utf-8"),
        runner_path.read_text(encoding="utf-8"),
    )
