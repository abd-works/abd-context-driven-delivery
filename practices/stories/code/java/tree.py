"""Java tree renderer — emits the full expected file tree for a StoryMap.

Layout produced (reference architecture, Java flavour):

    <tests-root>/
      stories/
        StoryTypes.java             (shared, verbatim from code/java/seeds)
        StoryRunner.java            (shared, verbatim from code/java/seeds)
      <epic-snake>/
        <sub-epic-snake>/
          <story-slug>/
            <StoryPascalCase>Stories.java

Shared files land under `<tests-root>/stories/` so the package declaration
`package stories;` stays valid. Story spec files land in their own package
derived from the epic / sub-epic hierarchy.

Tier files (write-once) are emitted by `tier_scaffold.py`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from stories.code.java.spec_file import _pascal, render_java_story_spec_file
from stories.story_model.nodes import Epic, Story, SubEpic
from stories.story_model.story_map import StoryMap


TEMPLATES_DIR = Path(__file__).resolve().parent / "seeds"


def render_java_tree(
    story_map: StoryMap,
    *,
    tests_root: str = "tests",
    include_shared: bool = True,
) -> Dict[str, str]:
    """Render the full expected Java tree for a StoryMap."""
    tree: Dict[str, str] = {}
    root = tests_root.strip("/") or "tests"

    if include_shared:
        for name in ("StoryTypes.java", "StoryRunner.java"):
            src = TEMPLATES_DIR / name
            if src.exists():
                tree[f"{root}/stories/{name}"] = src.read_text(encoding="utf-8")

    for epic in getattr(story_map, "epics", []) or []:
        _render_epic(epic, root=root, tree=tree)

    return tree


def _render_epic(epic: Epic, *, root: str, tree: Dict[str, str]) -> None:
    epic_slug = _snake(epic.name)
    for sub in getattr(epic, "sub_epics", []) or []:
        _render_sub_epic(
            sub,
            package_parts=[root, epic_slug],
            parent=f"{root}/{epic_slug}",
            depth=2,
            tree=tree,
        )


def _render_sub_epic(
    sub: SubEpic,
    *,
    package_parts: List[str],
    parent: str,
    depth: int,
    tree: Dict[str, str],
) -> None:
    sub_slug = _snake(sub.name)
    folder = f"{parent}/{sub_slug}"
    new_pkg = package_parts + [sub_slug]
    for nested in getattr(sub, "sub_epics", []) or []:
        _render_sub_epic(
            nested,
            package_parts=new_pkg,
            parent=folder,
            depth=depth + 1,
            tree=tree,
        )
    for story in getattr(sub, "stories", []) or []:
        _render_story(story, package_parts=new_pkg, parent=folder, depth=depth + 1, tree=tree)


def _render_story(
    story: Story,
    *,
    package_parts: List[str],
    parent: str,
    depth: int,
    tree: Dict[str, str],
) -> None:
    if not getattr(story, "scenarios", None):
        return
    story_slug = _snake(story.name)
    story_folder = f"{parent}/{story_slug}"
    class_name = f"{_pascal(story.name)}Stories"
    pkg = package_parts + [story_slug]
    tree[f"{story_folder}/{class_name}.java"] = render_java_story_spec_file(
        story, package_parts=pkg
    )


def _snake(name: str) -> str:
    """Convert a name to snake_case for Java package segments."""
    words = [w for w in re.split(r"[^0-9A-Za-z]+", name) if w]
    return "_".join(w.lower() for w in words) or "stories"
