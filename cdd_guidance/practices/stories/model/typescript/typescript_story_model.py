"""TypeScriptStoryModel - runnable `{story_snake}_story.test.ts` under epic / sub-epic / story."""

from __future__ import annotations

from pathlib import Path

from cdd_guidance.practices.clean_engineering.model.code_body import TYPESCRIPT
from cdd_guidance.practices.stories.model.brace_story import BraceStoryWriting
from cdd_guidance.practices.stories.model.script_story_model import ScriptStoryModel, script_story_file_suffixes
from cdd_guidance.practices.stories.model.typescript.nodes import TypeScriptEpic, TypeScriptStory


class TypeScriptStoryWriting(BraceStoryWriting):
    """How TypeScript writes stories: a story file imports the story-test helpers from the step library folder,
    named from the workspace root (helpers), as a path alias resolves it."""

    file_name_template = "{snake}_story.test.ts"

    def story_test_import(self, parent: str) -> str:
        return f'import {{ background, scenario, story }} from "{self.helpers}";'


class TypeScriptStoryModel(ScriptStoryModel):
    LEAF_EXTENSION = ".ts"
    story_file_suffixes = script_story_file_suffixes(LEAF_EXTENSION)
    seed_file = Path(__file__).resolve().parent / "seeds" / "story-test.ts"
    epic_type = TypeScriptEpic
    story_type = TypeScriptStory
    language = TYPESCRIPT
    writing_type = TypeScriptStoryWriting
