"""TypeScriptStoryModel - runnable `{story_snake}_story.test.ts` under epic / sub-epic / story."""

from __future__ import annotations

import re
from typing import Dict, Optional

from cdd_guidance.practices.clean_engineering.model.code_body import TYPESCRIPT
from cdd_guidance.practices.stories.model.brace_story import BraceStoryModel
from cdd_guidance.practices.stories.model.story_model import Epic, StoryModel
from cdd_guidance.practices.stories.model.typescript.nodes import TypeScriptEpic, TypeScriptStory, _story_test_text


class TypeScriptStoryModel(BraceStoryModel):
    LEAF_EXTENSION = ".ts"
    story_file_suffixes = ("_story.test.ts", "_story.spec.ts", ".story.shared.ts")
    # A story test's examples module sits in its epic's examples folder and holds no story.
    not_story_paths = re.compile(r"(?:^|/)examples/")
    epic_type = TypeScriptEpic
    story_type = TypeScriptStory
    language = TYPESCRIPT

    def __init__(
        self,
        source: "StoryModel | str | None" = None,
        tests_root: str | None = None,
        story_test_folder: str | None = None,
    ):
        super().__init__(source, tests_root)
        folder = self._default_story_test_folder() if story_test_folder is None else story_test_folder
        self._story_test_folder = folder.strip("/")

    def _default_story_test_folder(self) -> str:
        """The step library folder when none is named: the stories workspace root, else the deploy root."""
        root = self.tests_root.strip("/")
        if root == "stories" or root.startswith("stories/"):
            return "stories"
        return root

    @property
    def story_test_folder(self) -> str:
        """Step library folder: where story-test.ts sits and where story files import it from."""
        return self._story_test_folder

    @property
    def story_test_import_path(self) -> str:
        """The workspace-root import every story file uses for story-test."""
        return f"{self._story_test_folder}/story-test" if self._story_test_folder else "story-test"

    @property
    def story_test_file_path(self) -> str:
        """Where the shared story-test.ts seed is written."""
        return f"{self.story_test_import_path}.ts"

    def save(self) -> Dict[str, str]:
        # WHY: a tree read from TypeScript already brings its own story-test helper; only a new tree needs the seed.
        seed_path = self.story_test_file_path
        seed = {} if self.read_from_code() else {seed_path: _story_test_text(self.tests_root)}
        return self.write_epics(seed)

    def copy_of(self, source: Optional[StoryModel]) -> "TypeScriptStoryModel":
        return type(self)(source, tests_root=self.tests_root, story_test_folder=self._story_test_folder)

    def file_name(self, epic: Epic) -> str:
        return f"{epic.snake()}_story.test.ts"

    def story_test_import(self, parent: str) -> str:
        return f'import {{ scenario, story }} from "{self.story_test_import_path}";'

    def folder_files(self, epic: Epic, folder: str, files: Dict[str, str]) -> None:
        """A new epic folder starts with example aggregates; a folder read from code already has its own."""
        if self.read_from_code():
            return
        name, text = epic.examples_file()
        files.setdefault(f"{folder}/examples/{name}", text)

