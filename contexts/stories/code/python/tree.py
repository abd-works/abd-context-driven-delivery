"""Python tree renderer — runnable `*_story.py` per Story folder."""

from __future__ import annotations

from typing import Dict

from contexts.stories.code.code_story_map import to_kebab, to_pascal, to_snake
from contexts.stories.code.example_factories import collect_example_factories
from contexts.stories.code.python.example_factories import (
    render_python_factory_accessors,
    render_python_factory_imports,
)
from contexts.stories.code.python.story_file import render_story_file
from contexts.stories.story_model.nodes import Epic, Story, SubEpic
from contexts.stories.story_model.story_map import StoryMap


def render_py_tree(
    story_map: StoryMap,
    *,
    tests_root: str = "tests",
) -> Dict[str, str]:
    tree: Dict[str, str] = {}
    root = tests_root.strip("/") or "tests"
    for epic in getattr(story_map, "epics", []) or []:
        _render_epic(epic, root=root, tree=tree)
    return tree


def _render_epic(epic: Epic, *, root: str, tree: Dict[str, str]) -> None:
    epic_slug = to_kebab(epic.name)
    helper = _render_epic_helper(epic)
    if helper is not None:
        tree[f"{root}/{epic_slug}/{to_snake(epic.name)}_helper.py"] = helper
    for sub in getattr(epic, "sub_epics", []) or []:
        _render_sub_epic(sub, parent=f"{root}/{epic_slug}", tree=tree, epic=epic)


def _render_epic_helper(epic: Epic) -> str:
    factories = collect_example_factories(epic)
    helper_class = f"{to_pascal(epic.name)}Helper"
    lines: list[str] = [
        '"""Epic helper — ExampleFactory accessors; AI fills given_* bodies."""',
        "",
        "from __future__ import annotations",
        "",
    ]
    lines.extend(render_python_factory_imports(factories))
    lines.append(f"class {helper_class}:")
    lines.append('    """Shared helpers. Explore/spec → fake mode; tiers pass isolated|production."""')
    lines.append("")
    lines.extend(render_python_factory_accessors(factories))
    if not factories:
        lines.append(f"    # No example_factories declared on epic {epic.name!r}")
        lines.append("    pass")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_sub_epic(
    sub: SubEpic, *, parent: str, tree: Dict[str, str], epic: Epic
) -> None:
    folder = f"{parent}/{to_kebab(sub.name)}"
    for nested in getattr(sub, "sub_epics", []) or []:
        _render_sub_epic(nested, parent=folder, tree=tree, epic=epic)
    for story in getattr(sub, "stories", []) or []:
        _render_story(story, parent=folder, tree=tree, epic=epic)


def _render_story(
    story: Story, *, parent: str, tree: Dict[str, str], epic: Epic
) -> None:
    if not getattr(story, "scenarios", None):
        return
    story_slug = to_kebab(story.name)
    story_snake = to_snake(story.name)
    story_folder = f"{parent}/{story_slug}"
    helper_module = f"{to_snake(epic.name)}_helper"
    # Import path: story is 3 levels under epic (sub/story/file) → relative via package note
    relative_helper = f"..{to_snake(epic.name)}_helper"
    # Prefer simple module name; AI adjusts sys.path / package layout
    tree[f"{story_folder}/{story_snake}_story.py"] = render_story_file(
        story,
        relative_helper_module=helper_module,
        helper_class=f"{to_pascal(epic.name)}Helper",
    )
