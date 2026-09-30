"""JavaScriptStoryMap - a story map stored as `*_story.js` files.

Each story file is `story` / `background` / `scenario` / `given` / `when` / `then`.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from pathlib import Path

from practices.stories.model.code_story_model import CodeStoryMap, CodeStoryMapError
from practices.stories.model.javascript.nodes import JavaScriptEpic, JavaScriptStory
from practices.stories.model.story_model import Epic


class JavaScriptStoryMap(CodeStoryMap):
    LEAF_EXTENSION = "_story.test.js"
    LANGUAGE_LINE_COMMENT = "//"
    epic_type = JavaScriptEpic
    epic_type = JavaScriptEpic
    story_type = JavaScriptStory

    def save(self, previous: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        tree: Dict[str, str] = {f"{self.tests_root}/story-test.js": _story_test_js()}
        for epic in self.epics:
            epic.write(self.tests_root, tree, self.tests_root)
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
        return f"{epic_root}/{epic.slug()}-helper.js"

    def load(self, external: Dict[str, str]) -> "JavaScriptStoryMap":
        if not isinstance(external, dict):
            raise CodeStoryMapError("JavaScript story map parse expects a path->content dict")
        self.epics.clear()
        # Group *_story.js by epic / sub-epic / story folder
        for path, content in sorted(external.items()):
            if not path.endswith(self.LEAF_EXTENSION):
                continue
            parts = path.strip("/").split("/")
            if parts and parts[0] == self.tests_root:
                parts = parts[1:]
            if self.take_sub_epic_file(parts, content):
                continue
            # epic / ...subs... / story-folder / file
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


def _story_test_js() -> str:
    seed = Path(__file__).resolve().parent / "seeds" / "story-test.js"
    if seed.exists():
        return seed.read_text(encoding="utf-8")
    return (
        'import { before, describe, it } from "node:test";\n\n'
        "export function story(name, build) {\n  describe(name, build);\n}\n"
    )
