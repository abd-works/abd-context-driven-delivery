"""TypeScriptStoryMap - runnable `{story}.{tier}.ts` under epic / sub-epic."""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from context_tools.stories.code.code_story_map import CodeStoryMap, CodeStoryMapError, to_kebab
from context_tools.stories.code.typescript.nodes import (
    TypeScriptEpic,
    TypeScriptStoryMap as _TypeScriptStoryMap,
    TypeScriptSubEpic,
)
from context_tools.stories.code.typescript.tree import render_ts_tree
from context_tools.stories.story_model.nodes import Epic, Story, SubEpic
from context_tools.stories.story_model.scenario import Scenario
from context_tools.stories.story_model.story_map import StoryMap

_SKIP_NAMES = frozenset({"story-test.ts", "givens.ts"})


def _is_gwt_leaf(path: str) -> bool:
    name = path.replace("\\", "/").rsplit("/", 1)[-1]
    if name in _SKIP_NAMES or name.endswith("-helper.ts"):
        return False
    if "/examples/" in path.replace("\\", "/"):
        return False
    if not name.endswith(".ts"):
        return False
    return "." in name[:-3]


def _story_slug_from_filename(name: str) -> str | None:
    if not name.endswith(".ts"):
        return None
    stem = name[:-3]
    if "." not in stem:
        return None
    return stem.rsplit(".", 1)[0]


class TypeScriptStoryMap(CodeStoryMap):
    LEAF_EXTENSION = ".ts"
    LANGUAGE_LINE_COMMENT = "//"

    def _make_story_map(self) -> _TypeScriptStoryMap:
        return _TypeScriptStoryMap()

    def _make_epic(self, name: str, order: int) -> TypeScriptEpic:
        return TypeScriptEpic(name, order)

    def _make_sub_epic(self, name: str, order: int) -> TypeScriptSubEpic:
        return TypeScriptSubEpic(name, order)

    def render(
        self, canonical: StoryMap, previous: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        tree = render_ts_tree(canonical, tests_root=self.tests_root, include_shared=True)
        if previous:
            for path, body in list(tree.items()):
                if path in previous and _is_gwt_leaf(path):
                    tree[path] = self._preserve_hand_written(previous[path], body)
        return tree

    def leaf_files_of(self, tree: Dict[str, str]) -> List[str]:
        return sorted(p for p in tree if _is_gwt_leaf(p))

    def _render_leaf_file(self, sub_epic: SubEpic, owning_epic: Epic) -> str:
        raise NotImplementedError("TypeScriptStoryMap.render uses render_ts_tree")

    def parse(self, external: Dict[str, str]) -> StoryMap:
        if not isinstance(external, dict):
            raise CodeStoryMapError("TypeScript story map parse expects a path->content dict")
        story_map = self._make_story_map()
        seen: set[tuple[str, ...]] = set()
        for path, content in sorted(external.items()):
            if not _is_gwt_leaf(path):
                continue
            parts = path.strip("/").replace("\\", "/").split("/")
            if parts and parts[0] == self.tests_root:
                parts = parts[1:]
            if len(parts) < 3:
                continue
            filename = parts[-1]
            story_slug = _story_slug_from_filename(filename)
            if not story_slug:
                continue
            epic_slug, sub_slugs = parts[0], parts[1:-1]
            if not sub_slugs:
                continue
            key = (epic_slug, *sub_slugs, story_slug)
            if key in seen:
                continue
            seen.add(key)
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
        name_match = re.search(r"\*\s*Story:\s*(.+)", content)
        story_name = name_match.group(1).strip() if name_match else story_slug.replace("-", " ").title()
        story_name = re.sub(r"\s*\([^)]*\)\.?\s*$", "", story_name).strip()
        story = Story(story_name, 1)
        actor_match = re.search(r"\*\s*Actor:\s*(.+)", content)
        if actor_match:
            story.users = [actor_match.group(1).strip()]
        for i, sc in enumerate(re.findall(r"scenario\(\s*['\"]([^'\"]+)['\"]", content), start=1):
            story.scenarios.append(Scenario(name=sc, sequential_order=i))
        return story
