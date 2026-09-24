"""Python tree renderer - runnable `*_story.test.py` per Story folder."""

from __future__ import annotations

from typing import Dict

from practices.stories.model.code_story_map import to_kebab, to_pascal, to_snake
from practices.stories.model.python.example_factories import PythonExampleFactories
from practices.stories.model.python.story_file import render_story_file
from practices.stories.model.nodes import Epic, Story, SubEpic
from practices.stories.model.story_map import StoryMap


class PythonTree:
    def render(self, story_map: StoryMap, tests_root: str = "tests") -> Dict[str, str]:
        tree: Dict[str, str] = {}
        self._tree = tree
        self._root = tests_root.strip("/") or "tests"
        for epic in getattr(story_map, "epics", []) or []:
            self._render_epic(epic)
        return tree

    def _render_epic(self, epic: Epic) -> None:
        epic_slug = to_kebab(epic.name)
        helper = self._render_epic_helper(epic)
        if helper is not None:
            self._tree[f"{self._root}/{epic_slug}/{to_snake(epic.name)}_helper.py"] = helper
        self._epic = epic
        for sub in getattr(epic, "sub_epics", []) or []:
            self._render_sub_epic(sub, f"{self._root}/{epic_slug}")

    def _render_epic_helper(self, epic: Epic) -> str:
        factories = epic.collected_example_factories()
        factories_py = PythonExampleFactories()
        helper_class = f"{to_pascal(epic.name)}Helper"
        lines: list[str] = [
            '"""Epic helper - ExampleFactory accessors; AI fills given_* bodies."""',
            "",
            "from __future__ import annotations",
            "",
        ]
        lines.extend(factories_py.render_imports(factories))
        lines.append(f"class {helper_class}:")
        lines.append('    """Shared ExampleFactory accessors. Tier test-helpers import this to build real collaborators."""')
        lines.append("")
        lines.extend(factories_py.render_accessors(factories))
        if not factories:
            lines.append(f"    # No example_factories declared on epic {epic.name!r}")
            lines.append("    pass")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def _render_sub_epic(self, sub: SubEpic, parent: str) -> None:
        folder = f"{parent}/{to_kebab(sub.name)}"
        for nested in getattr(sub, "sub_epics", []) or []:
            self._render_sub_epic(nested, folder)
        for story in getattr(sub, "stories", []) or []:
            self._render_story(story, folder)

    def _render_story(self, story: Story, parent: str) -> None:
        if not getattr(story, "scenarios", None):
            return
        story_folder = f"{parent}/{to_kebab(story.name)}"
        self._tree[f"{story_folder}/{to_snake(story.name)}_story.test.py"] = render_story_file(story)
