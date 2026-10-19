"""PythonStoryModel - runnable `*_story.test.py` per Story.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from practices.stories.model.code_story_model import CodeStoryModel, CodeStoryModelError
from practices.stories.model.python.nodes import PythonEpic, PythonStory
from practices.stories.model.story_model import Epic


class PythonStoryModel(CodeStoryModel):
    LEAF_EXTENSION = "_story.test.py"
    LANGUAGE_LINE_COMMENT = "#"
    epic_type = PythonEpic
    epic_type = PythonEpic
    story_type = PythonStory

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
        return sorted(p for p in tree if p.endswith(self.LEAF_EXTENSION))

    def _epic_helper_path(self, epic_root: str, epic: Epic) -> str:
        return f"{epic_root}/{epic.snake()}_helper.py"

    def load(self, external: Dict[str, str]) -> "PythonStoryModel":
        if not isinstance(external, dict):
            raise CodeStoryModelError("Python story map parse expects a path->content dict")
        self.epics.clear()
        for path in self._ordered_paths(external):
            content = external[path]
            if not path.endswith(self.LEAF_EXTENSION):
                continue
            parts = path.strip("/").split("/")
            if parts and parts[0] == self.tests_root:
                parts = parts[1:]
            if self.take_sub_epic_file(parts, content):
                continue
            if len(parts) < 4:
                continue
            epic_slug = parts[0]
            story_slug = parts[-2]
            sub_slugs = parts[1:-2]
            if not sub_slugs:
                continue
            epic = self.epic_for(epic_slug)
            sub = self.sub_epic_for(epic, sub_slugs)
            sub.append_story(self.story_type.load(content, story_slug))
        return self
