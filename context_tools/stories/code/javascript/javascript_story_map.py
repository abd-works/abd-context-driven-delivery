"""JavaScriptStoryMap — CodeStoryMap backend for runnable `*_story.js` files.

Explore / specification leaf shape (via ``story_file.render_story_file``):

  export function createSubmitOrderStory(mode) {
    story("Submit Order", () => {
      scenario("…", ({ given, when, then }) => { … });
    });
  }

Per-epic ``<epic-slug>-helper.js`` carries ExampleFactory accessors when declared.
Engineering: ``*_spec.js`` (isolated); ``*_spec.{tier}.js`` for other tiers.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from context_tools.stories.code.code_story_map import CodeStoryMap, CodeStoryMapError, to_kebab
from context_tools.stories.code.javascript.tree import render_js_tree
from context_tools.stories.code.javascript.nodes import (
    JavaScriptEpic,
    JavaScriptStoryMap as _JavaScriptStoryMap,
    JavaScriptSubEpic,
)
from context_tools.stories.story_model.nodes import Epic, Story, SubEpic
from context_tools.stories.story_model.scenario import Scenario
from context_tools.stories.story_model.story_map import StoryMap


class JavaScriptStoryMap(CodeStoryMap):
    LEAF_EXTENSION = "_story.js"
    LANGUAGE_LINE_COMMENT = "//"

    def _make_story_map(self) -> _JavaScriptStoryMap:
        return _JavaScriptStoryMap()

    def _make_epic(self, name: str, order: int) -> JavaScriptEpic:
        return JavaScriptEpic(name, order)

    def _make_sub_epic(self, name: str, order: int) -> JavaScriptSubEpic:
        return JavaScriptSubEpic(name, order)

    def render(
        self,
        canonical: StoryMap,
        previous: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        tree = render_js_tree(canonical, tests_root=self.tests_root, include_shared=True)
        if previous:
            for path, body in list(tree.items()):
                if path in previous and path.endswith(self.LEAF_EXTENSION):
                    tree[path] = self._preserve_hand_written(previous[path], body)
        return tree

    def leaf_files_of(self, tree: Dict[str, str]) -> List[str]:
        return sorted(
            p for p in tree if p.endswith(self.LEAF_EXTENSION) and "/story-test.js" not in p
        )

    def _epic_helper_path(self, epic_root: str, epic: Epic) -> str:
        return f"{epic_root}/{to_kebab(epic.name)}-helper.js"

    def _render_epic_helper(self, epic: Epic) -> Optional[str]:
        # render() uses tree.py; keep hook for CodeStoryMap base paths
        return None

    def _render_leaf_file(self, sub_epic: SubEpic, owning_epic: Epic) -> str:
        raise NotImplementedError("JavaScriptStoryMap.render uses render_js_tree")

    def parse(self, external: Dict[str, str]) -> StoryMap:
        if not isinstance(external, dict):
            raise CodeStoryMapError("JavaScript story map parse expects a path→content dict")
        story_map = self._make_story_map()
        # Group *_story.js by epic / sub-epic / story folder
        for path, content in sorted(external.items()):
            if not path.endswith(self.LEAF_EXTENSION):
                continue
            parts = path.strip("/").split("/")
            # tests/epic/sub/story/name_story.js  → need ≥ 5 parts with tests root
            if len(parts) < 4:
                continue
            # Drop tests_root if present
            if parts[0] == self.tests_root:
                parts = parts[1:]
            # epic / …subs… / story-folder / file
            if len(parts) < 4:
                continue
            epic_slug = parts[0]
            story_slug = parts[-2]
            sub_slugs = parts[1:-2]
            if not sub_slugs:
                continue

            epic = self._ensure_epic(story_map, epic_slug)
            sub = self._ensure_sub_path(epic, sub_slugs)
            story = self._parse_story_file(content, story_slug)
            if story is not None:
                sub.stories.append(story)
        return story_map

    def _ensure_epic(self, story_map: StoryMap, epic_slug: str) -> Epic:
        for epic in story_map.epics:
            if to_kebab(epic.name) == epic_slug:
                return epic
        epic = self._make_epic(epic_slug.replace("-", " ").title(), len(story_map.epics) + 1)
        story_map.append_epic(epic)
        return epic

    def _ensure_sub_path(self, epic: Epic, sub_slugs: List[str]) -> SubEpic:
        parent_subs = epic.sub_epics
        current: SubEpic | None = None
        for slug in sub_slugs:
            found = next((s for s in parent_subs if to_kebab(s.name) == slug), None)
            if found is None:
                found = self._make_sub_epic(
                    slug.replace("-", " ").title(), len(parent_subs) + 1
                )
                parent_subs.append(found)
            current = found
            parent_subs = found.sub_epics
        assert current is not None
        return current

    def _parse_story_file(self, content: str, story_slug: str) -> Story | None:
        name_match = re.search(r'story\(\s*[\'"]([^\'"]+)[\'"]', content)
        story_name = (
            name_match.group(1)
            if name_match
            else story_slug.replace("-", " ").title()
        )
        story = Story(story_name, 1)

        actor_match = re.search(r"\*\s*Actor:\s*(.+)", content)
        if actor_match:
            story.users = [actor_match.group(1).strip()]

        for i, sc_name in enumerate(
            re.findall(r'scenario\(\s*[\'"]([^\'"]+)[\'"]', content), start=1
        ):
            story.scenarios.append(Scenario(name=sc_name, sequential_order=i))
        return story
