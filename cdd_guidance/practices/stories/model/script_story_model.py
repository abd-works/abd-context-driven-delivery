"""ScriptStoryModel. Story files in the script languages, TypeScript and JavaScript: one model reads and writes both.

The two languages hold the same story files: a story test (``{story}_story.test``), a shared story file the tiers
replay (``.story.shared``), a screen spec (``.story.ui.spec``), an examples module in an ``examples`` folder, and the
step library (``story-test``) every story file imports. A language names only its extension, its code language, the
step library it seeds a new tree with, and how a story file imports that library.
"""

from __future__ import annotations

import re
from functools import cached_property
from pathlib import Path
from typing import Dict, Optional

from cdd_guidance.practices.stories.model.brace_story import BraceStory, BraceStoryModel, BraceStoryWriting
from cdd_guidance.practices.stories.model.screen_spec_file import SCREEN_SPEC_STEM, ScreenSpecFile, is_screen_spec
from cdd_guidance.practices.stories.model.story_file import StoryFile
from cdd_guidance.practices.stories.model.story_model import StoryModel

# How a story file's name ends before its language's extension; the first is the one a language writes.
_STORY_FILE_STEMS = ("_story.test", "_story.spec", ".story.shared", SCREEN_SPEC_STEM)


def script_story_file_suffixes(extension: str) -> tuple[str, ...]:
    """How a story file ends in the script language whose files end with extension (``.ts``, ``.js``)."""
    return tuple(f"{stem}{extension}" for stem in _STORY_FILE_STEMS)


class ScriptStory(BraceStory):
    """A story read from a script-language story file; a screen spec gives one for each ``test.describe``."""

    """A story read from a script-language story file; a screen spec gives one for each ``test.describe``."""


class ScriptStoryModel(BraceStoryModel):
    """A story tree in TypeScript or JavaScript. It keeps the step library folder, where ``story-test`` sits and
    where story files import it from, which a pattern may name; with none named it is the tests root."""

    LEAF_EXTENSION = ""
    """The extension the language's files end with, such as ``.ts``."""
    seed_file: Path
    """The step library a new tree in this language is seeded with."""
    # A story test's examples module sits in its epic's examples folder and holds no story.
    not_story_paths = re.compile(r"(?:^|/)examples/")

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
        """Step library folder: where the step library sits and where story files import it from."""
        return self._story_test_folder

    @property
    def story_test_import_path(self) -> str:
        """The step library as a path from the workspace root, without its extension."""
        return f"{self._story_test_folder}/story-test" if self._story_test_folder else "story-test"

    @property
    def _story_test_file_path(self) -> str:
        """Where the step library a new tree is seeded with is written."""
        return f"{self.story_test_import_path}{self.LEAF_EXTENSION}"

    def story_file(self, path: str, content: str, project: Optional[Path] = None) -> StoryFile:
        """The story file at path: a screen spec, read from its describes and tests, or any other, read block by
        block."""
        if is_screen_spec(content):
            return ScreenSpecFile(self, path, content, project if project is not None else self.project)
        return super().story_file(path, content, project)

    def save(self) -> Dict[str, str]:
        # WHY: a tree read from code already brings its own step library; only a new tree needs the seed.
        seed = {} if self.read_from_code else {self._story_test_file_path: self.seed_file.read_text(encoding="utf-8")}
        return self._write_epics(seed)

    def copy_of(self, source: Optional[StoryModel]) -> "ScriptStoryModel":
        return type(self)(source, tests_root=self.tests_root, story_test_folder=self._story_test_folder)

    @cached_property
    def writing(self) -> BraceStoryWriting:
        """How this model's language writes its story files, importing the step library from its folder."""
        return self.writing_type(self.language, self.story_test_import_path)
