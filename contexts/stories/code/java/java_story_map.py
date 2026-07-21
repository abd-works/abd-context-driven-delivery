"""JavaStoryMap — runnable `{Story}Story.java` per Story."""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from contexts.stories.code.code_story_map import CodeStoryMap, CodeStoryMapError, to_kebab
from contexts.stories.code.java.nodes import (
    JavaEpic,
    JavaStoryMap as _JavaStoryMap,
    JavaSubEpic,
)
from contexts.stories.code.java.tree import render_java_tree
from contexts.stories.story_model.nodes import Epic, Story, SubEpic
from contexts.stories.story_model.scenario import Scenario
from contexts.stories.story_model.story_map import StoryMap


class JavaStoryMap(CodeStoryMap):
    LEAF_EXTENSION = "Story.java"
    LANGUAGE_LINE_COMMENT = "//"

    def _make_story_map(self) -> _JavaStoryMap:
        return _JavaStoryMap()

    def _make_epic(self, name: str, order: int) -> JavaEpic:
        return JavaEpic(name, order)

    def _make_sub_epic(self, name: str, order: int) -> JavaSubEpic:
        return JavaSubEpic(name, order)

    def render(
        self, canonical: StoryMap, previous: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        tree = render_java_tree(canonical, tests_root=self.tests_root)
        if previous:
            for path, body in list(tree.items()):
                if path in previous and path.endswith(self.LEAF_EXTENSION):
                    tree[path] = self._preserve_hand_written(previous[path], body)
        return tree

    def leaf_files_of(self, tree: Dict[str, str]) -> List[str]:
        return sorted(
            p
            for p in tree
            if p.endswith(self.LEAF_EXTENSION) and not p.endswith("Helper.java")
        )

    def _render_leaf_file(self, sub_epic: SubEpic, owning_epic: Epic) -> str:
        raise NotImplementedError("JavaStoryMap.render uses render_java_tree")

    def parse(self, external: Dict[str, str]) -> StoryMap:
        if not isinstance(external, dict):
            raise CodeStoryMapError("Java story map parse expects a path→content dict")
        story_map = self._make_story_map()
        for path, content in sorted(external.items()):
            if not path.endswith(self.LEAF_EXTENSION) or path.endswith("Helper.java"):
                continue
            if "Spec" in path.split("/")[-1]:
                continue
            parts = path.strip("/").split("/")
            if parts and parts[0] == self.tests_root:
                parts = parts[1:]
            if len(parts) < 4:
                continue
            epic_slug, story_slug, sub_slugs = parts[0], parts[-2], parts[1:-2]
            if not sub_slugs:
                continue
            epic = self._ensure_epic(story_map, epic_slug)
            sub = self._ensure_sub_path(epic, sub_slugs)
            story = self._parse_story_file(content, story_slug)
            if story:
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
                found = self._make_sub_epic(slug.replace("-", " ").title(), len(parent_subs) + 1)
                parent_subs.append(found)
            current = found
            parent_subs = found.sub_epics
        assert current is not None
        return current

    def _parse_story_file(self, content: str, story_slug: str) -> Story | None:
        name_match = re.search(r"Story:\s*(.+)", content)
        story_name = name_match.group(1).strip() if name_match else story_slug.replace("-", " ").title()
        story_name = re.sub(r"\s*\(tier-neutral\)\.?\s*$", "", story_name).strip()
        story = Story(story_name, 1)
        actor_match = re.search(r"Actor:\s*(.+)", content)
        if actor_match:
            story.users = [actor_match.group(1).strip()]
        for i, sc in enumerate(re.findall(r"SCENARIO:\s*(.+)", content), start=1):
            story.scenarios.append(Scenario(name=sc.strip(), sequential_order=i))
        return story
