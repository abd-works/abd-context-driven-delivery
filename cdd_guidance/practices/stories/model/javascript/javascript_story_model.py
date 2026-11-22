"""JavaScriptStoryModel - runnable `{story_snake}_story.test.js` under epic / sub-epic / story."""

from __future__ import annotations

import posixpath
from pathlib import Path

from cdd_guidance.practices.source_code import JAVASCRIPT
from cdd_guidance.practices.stories.model.brace_story import BraceStoryWriting
from cdd_guidance.practices.stories.model.javascript.nodes import JavaScriptEpic
from cdd_guidance.practices.stories.model.script_story_model import ScriptStoryModel, script_story_file_suffixes


class JavaScriptStoryWriting(BraceStoryWriting):
    """How JavaScript writes stories: a story file imports the story-test helpers by the path from its own folder to
    the step library (helpers, named from the workspace root), with the file's extension, as a JavaScript module
    import is written."""

    file_name_template = "{snake}_story.test.js"

    def story_test_import(self, parent: str) -> str:
        relative = posixpath.relpath(f"{self.helpers}.js", parent or ".")
        return f'import {{ background, scenario, story }} from "{relative if relative.startswith(".") else "./" + relative}";'


class JavaScriptStoryModel(ScriptStoryModel):
    LEAF_EXTENSION = ".js"
    story_file_suffixes = script_story_file_suffixes(LEAF_EXTENSION)
    seed_file = Path(__file__).resolve().parents[2] / "templates" / "js" / "story-test.js"
    epic_class = JavaScriptEpic
    language = JAVASCRIPT
    writing_class = JavaScriptStoryWriting
