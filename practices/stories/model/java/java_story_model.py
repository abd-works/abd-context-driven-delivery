"""JavaStoryMap - runnable `{Story}Story.java` per Story."""

from __future__ import annotations

from typing import Dict, List, Optional

from practices.stories.model.code_story_model import CodeStoryMap, CodeStoryMapError
from practices.stories.model.java.nodes import JavaEpic, JavaStory


class JavaStoryMap(CodeStoryMap):
    LEAF_EXTENSION = "Story.java"
    LANGUAGE_LINE_COMMENT = "//"
    epic_type = JavaEpic
    epic_type = JavaEpic
    story_type = JavaStory

    def save(self, previous: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        tree: Dict[str, str] = {}
        for epic in self.epics:
            epic.write(self.tests_root, tree, self.tests_root)
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

    def load(self, external: Dict[str, str]) -> "JavaStoryMap":
        if not isinstance(external, dict):
            raise CodeStoryMapError("Java story map parse expects a path->content dict")
        self.epics.clear()
        for path, content in sorted(external.items()):
            if not path.endswith(self.LEAF_EXTENSION) or path.endswith("Helper.java"):
                continue
            if "Spec" in path.split("/")[-1]:
                continue
            parts = path.strip("/").split("/")
            if parts and parts[0] == self.tests_root:
                parts = parts[1:]
            if self.take_sub_epic_file(parts, content):
                continue
            if len(parts) < 4:
                continue
            epic_slug, story_slug, sub_slugs = parts[0], parts[-2], parts[1:-2]
            if not sub_slugs:
                continue
            epic = self.epic_for(epic_slug)
            sub = self.sub_epic_for(epic, sub_slugs)
            sub.append_story(self.story_type.load(content, story_slug))
        return self
