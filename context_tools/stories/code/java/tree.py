"""Java tree - `{Story}Story.java` per Story folder."""

from __future__ import annotations

from typing import Dict

from context_tools.stories.code.code_story_map import to_kebab, to_pascal
from context_tools.stories.code.example_factories import collect_example_factories
from context_tools.stories.code.java.story_file import render_story_file
from context_tools.stories.story_model.nodes import Epic, Story, SubEpic
from context_tools.stories.story_model.story_map import StoryMap


def render_java_tree(story_map: StoryMap, *, tests_root: str = "tests") -> Dict[str, str]:
    tree: Dict[str, str] = {}
    root = tests_root.strip("/") or "tests"
    for epic in getattr(story_map, "epics", []) or []:
        _render_epic(epic, root=root, tree=tree)
    return tree


def _render_epic(epic: Epic, *, root: str, tree: Dict[str, str]) -> None:
    epic_slug = to_kebab(epic.name)
    helper_class = f"{to_pascal(epic.name)}Helper"
    tree[f"{root}/{epic_slug}/{helper_class}.java"] = _helper(epic, helper_class)
    for sub in getattr(epic, "sub_epics", []) or []:
        _render_sub(sub, parent=f"{root}/{epic_slug}", tree=tree, epic=epic)


def _helper(epic: Epic, helper_class: str) -> str:
    factories = collect_example_factories(epic)
    lines = [
        f"/** Epic helper - ExampleFactory accessors; AI fills given_* bodies. */",
        f"public class {helper_class} {{",
        "  // explore/spec -> fake mode; tiers -> isolated|production",
    ]
    for name in factories:
        method = name[0].lower() + name[1:]
        lines.append(f"  public {name} {method}() {{ return new {name}(); }}")
    if not factories:
        lines.append(f"  // No example_factories on epic {epic.name!r}")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _render_sub(
    sub: SubEpic, *, parent: str, tree: Dict[str, str], epic: Epic
) -> None:
    folder = f"{parent}/{to_kebab(sub.name)}"
    for nested in getattr(sub, "sub_epics", []) or []:
        _render_sub(nested, parent=folder, tree=tree, epic=epic)
    for story in getattr(sub, "stories", []) or []:
        if not story.scenarios:
            continue
        story_folder = f"{folder}/{to_kebab(story.name)}"
        class_name = f"{to_pascal(story.name)}Story"
        tree[f"{story_folder}/{class_name}.java"] = render_story_file(
            story, helper_class=f"{to_pascal(epic.name)}Helper"
        )
