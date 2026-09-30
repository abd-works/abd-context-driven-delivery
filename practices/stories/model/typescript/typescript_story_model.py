"""TypeScriptStoryMap - runnable `{story_snake}_story.test.ts` under epic / sub-epic / story."""

from __future__ import annotations

from typing import Dict, List, Optional

from practices.stories.model.code_story_model import (
    CodeStoryMap,
    CodeStoryMapError,
)
from practices.stories.model.typescript.nodes import TypeScriptEpic, TypeScriptStory, _story_test_text
from practices.stories.model.typescript.story_file import story_test_file_path

_SKIP_NAMES = frozenset({"story-test.ts", "givens.ts"})


_STORY_TEST_SUFFIX = "_story.test.ts"


class TypeScriptStoryMap(CodeStoryMap):
    LEAF_EXTENSION = ".ts"
    LANGUAGE_LINE_COMMENT = "//"
    epic_type = TypeScriptEpic
    epic_type = TypeScriptEpic
    story_type = TypeScriptStory

    def save(self, previous: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        tree: Dict[str, str] = {story_test_file_path(self.tests_root): _story_test_text(self.tests_root)}
        for epic in self.epics:
            epic.write(self.tests_root, tree, self.tests_root)
        if previous:
            for path, body in list(tree.items()):
                if path in previous and self._is_gwt_leaf(path):
                    tree[path] = self._preserve_hand_written(previous[path], body)
        return tree

    def leaf_files_of(self, tree: Dict[str, str]) -> List[str]:
        return sorted(p for p in tree if self._is_gwt_leaf(p))

    def _is_gwt_leaf(self, path: str) -> bool:
        name = path.replace("\\", "/").rsplit("/", 1)[-1]
        if name in _SKIP_NAMES or name.endswith("-helper.ts"):
            return False
        if "/examples/" in path.replace("\\", "/"):
            return False
        return name.endswith(_STORY_TEST_SUFFIX)

    def _story_slug_from_filename(self, name: str) -> str | None:
        if not name.endswith(_STORY_TEST_SUFFIX):
            return None
        stem = name[: -len(_STORY_TEST_SUFFIX)]
        return stem.replace("_", "-")

    def load(self, external: Dict[str, str]) -> "TypeScriptStoryMap":
        if not isinstance(external, dict):
            raise CodeStoryMapError("TypeScript story map parse expects a path->content dict")
        self.epics.clear()
        seen: set[tuple[str, ...]] = set()
        for path, content in sorted(external.items()):
            if not self._is_gwt_leaf(path):
                continue
            parts = path.strip("/").replace("\\", "/").split("/")
            stripped = self.strip_tests_root_prefix(parts)
            if stripped is None:
                continue
            parts = stripped
            if self.take_sub_epic_file(parts, content):
                continue
            if len(parts) < 3:
                continue
            filename = parts[-1]
            story_slug = self._story_slug_from_filename(filename)
            if not story_slug:
                continue
            epic_slug, sub_slugs = parts[0], parts[1:-1]
            if sub_slugs and sub_slugs[-1] == story_slug:
                sub_slugs = sub_slugs[:-1]
            if not sub_slugs:
                continue
            key = (epic_slug, *sub_slugs, story_slug)
            if key in seen:
                continue
            seen.add(key)
            epic = self.epic_for(epic_slug)
            sub = self.sub_epic_for(epic, sub_slugs)
            sub.append_story(self.story_type.load(content, story_slug))
        return self
