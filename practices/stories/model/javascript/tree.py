"""JavaScript tree renderer - full file tree for a Workspace.

Story folder layout (explore / specification):

  {epic}/{sub-epic}/{story}/{story_snake}_story.test.js

Shared: story-types.js (legacy), story-test.js (GWT helpers).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

from practices.stories.model.code_story_map import to_kebab, to_pascal, to_snake
from practices.stories.model.javascript.example_factories import JavaScriptExampleFactories
from practices.stories.model.javascript.story_file import render_story_file
from practices.stories.model.nodes import Epic, Story, SubEpic
from practices.stories.model.story_map import StoryMap


TEMPLATES_DIR = Path(__file__).resolve().parent / "seeds"


class JavaScriptTree:
    def render(
        self,
        story_map: StoryMap,
        tests_root: str = "tests",
    ) -> Dict[str, str]:
        self._include_shared = True
        return self._render_tree(story_map, tests_root)

    def render_without_shared(self, story_map: StoryMap) -> Dict[str, str]:
        self._include_shared = False
        return self._render_tree(story_map, "tests")

    def _render_tree(self, story_map: StoryMap, tests_root: str) -> Dict[str, str]:
        tree: Dict[str, str] = {}
        root = tests_root.strip("/") or "tests"
        if self._include_shared:
            _types_body, test_body = self._read_shared_templates()
            tree[f"{root}/story-test.js"] = test_body
        self._tree = tree
        self._root = root
        for epic in getattr(story_map, "epics", []) or []:
            self._render_epic(epic)
        return tree

    def _render_epic(self, epic: Epic) -> None:
        epic_slug = to_kebab(epic.name)
        helper = self._render_epic_helper(epic)
        if helper is not None:
            self._tree[f"{self._root}/{epic_slug}/{epic_slug}-helper.js"] = helper
        self._epic = epic
        self._depth = 2
        for sub in getattr(epic, "sub_epics", []) or []:
            self._render_sub_epic(sub, f"{self._root}/{epic_slug}")

    def _render_epic_helper(self, epic: Epic) -> str | None:
        factories = epic.collected_example_factories()
        factories_js = JavaScriptExampleFactories()
        helper_class = f"{to_pascal(epic.name)}Helper"
        lines: list[str] = []
        lines.extend(factories_js.render_imports(factories))
        lines.append(f"export class {helper_class} {{")
        lines.append(
            "  /** Shared given/when/then helpers. Call ExampleFactory methods - do not invent Fakes. */"
        )
        lines.append("  /** Shared ExampleFactory accessors. Tier test-helpers import this to build real collaborators. */")
        lines.append("")
        lines.extend(factories_js.render_accessors(factories))
        if not factories:
            lines.append(f"  // No example_factories declared on epic {epic.name!r}")
            lines.append("")
        lines.append("}")
        lines.append("")
        return "\n".join(lines)

    def _render_sub_epic(self, sub: SubEpic, parent: str) -> None:
        folder = f"{parent}/{to_kebab(sub.name)}"
        saved_depth = self._depth
        self._depth = saved_depth + 1
        for nested in getattr(sub, "sub_epics", []) or []:
            self._render_sub_epic(nested, folder)
        for story in getattr(sub, "stories", []) or []:
            self._render_story(story, folder)
        self._depth = saved_depth

    def _render_story(self, story: Story, parent: str) -> None:
        if not getattr(story, "scenarios", None):
            return
        story_folder = f"{parent}/{to_kebab(story.name)}"
        relative_story_test = "../" * self._depth + "story-test.js"
        self._tree[f"{story_folder}/{to_snake(story.name)}_story.test.js"] = render_story_file(
            story,
            relative_story_test_path=relative_story_test,
        )

    def _read_shared_templates(self) -> Tuple[str, str]:
        types_path = TEMPLATES_DIR / "story-types.js"
        test_path = TEMPLATES_DIR / "story-test.js"
        types_body = types_path.read_text(encoding="utf-8") if types_path.exists() else ""
        if test_path.exists():
            return types_body, test_path.read_text(encoding="utf-8")
        test_body = (
            'import { before, describe, it } from "node:test";\n\n'
            "export function story(name, build) {\n  describe(name, build);\n}\n\n"
            "export function scenario(name, build) {\n"
            "  describe(name, () => {\n"
            "    const givens = [];\n    const whens = [];\n    const thens = [];\n"
            "    build({\n"
            "      given(step, fn) { givens.push({ step, fn }); },\n"
            "      when(step, fn) { whens.push({ step, fn }); },\n"
            "      then(step, fn) {\n"
            "        thens.push({ step, fn });\n"
            "        const chain = {\n"
            "          and(s, f) { thens.push({ step: s, fn: f }); return chain; },\n"
            "        };\n"
            "        return chain;\n"
            "      },\n"
            "    });\n"
            "    before(() => {\n"
            "      for (const g of givens) g.fn();\n"
            "      for (const w of whens) w.fn();\n"
            "    });\n"
            "    thens.forEach(({ step, fn }, i) => {\n"
            "      it(i === 0 ? `Then ${step}` : step, fn);\n"
            "    });\n"
            "  });\n}\n"
        )
        return types_body, test_body
