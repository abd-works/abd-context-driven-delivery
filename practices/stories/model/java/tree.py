"""Java tree - `{Story}Story.java` per Story folder."""

from __future__ import annotations

from typing import Dict

from practices.stories.model.code_story_map import to_kebab, to_pascal
from practices.stories.model.java.story_file import render_story_file
from practices.stories.model.nodes import Epic, SubEpic
from practices.stories.model.story_map import StoryMap


class JavaTree:
    def render(self, story_map: StoryMap, tests_root: str = "tests") -> Dict[str, str]:
        self._tree: Dict[str, str] = {}
        self._root = tests_root.strip("/") or "tests"
        self._epic: Epic | None = None
        self._parent = self._root
        for epic in getattr(story_map, "epics", []) or []:
            self._render_epic(epic)
        return self._tree

    def _render_epic(self, epic: Epic) -> None:
        self._epic = epic
        epic_slug = to_kebab(epic.name)
        helper_class = f"{to_pascal(epic.name)}Helper"
        self._tree[f"{self._root}/{epic_slug}/{helper_class}.java"] = self._helper(
            helper_class
        )
        self._parent = f"{self._root}/{epic_slug}"
        for sub in getattr(epic, "sub_epics", []) or []:
            self._render_sub(sub)

    def _helper(self, helper_class: str) -> str:
        factories = self._epic.collected_example_factories()
        lines = [
            f"/** Epic helper - ExampleFactory accessors; AI fills given_* bodies. */",
            f"public class {helper_class} {{",
            "  // Explore/spec accessor. Tier test-helpers import this to build real collaborators.",
        ]
        for name in factories:
            method = name[0].lower() + name[1:]
            lines.append(f"  public {name} {method}() {{ return new {name}(); }}")
        if not factories:
            lines.append(f"  // No example_factories on epic {self._epic.name!r}")
        lines.append("}")
        lines.append("")
        return "\n".join(lines)

    def _render_sub(self, sub: SubEpic) -> None:
        folder = f"{self._parent}/{to_kebab(sub.name)}"
        saved_parent = self._parent
        self._parent = folder
        for nested in getattr(sub, "sub_epics", []) or []:
            self._render_sub(nested)
        self._parent = saved_parent
        for story in getattr(sub, "stories", []) or []:
            if not story.scenarios:
                continue
            story_folder = f"{folder}/{to_kebab(story.name)}"
            class_name = f"{to_pascal(story.name)}Story"
            self._tree[f"{story_folder}/{class_name}.java"] = render_story_file(story)


def render_java_tree(story_map: StoryMap, *, tests_root: str = "tests") -> Dict[str, str]:
    return JavaTree().render(story_map, tests_root)
