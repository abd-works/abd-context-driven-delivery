"""TypeScript nodes: TypeScript, then the script languages, then code, then the story model."""
from __future__ import annotations

from cdd_guidance.practices.source_code import TYPESCRIPT
from cdd_guidance.practices.stories.model.brace_story import BraceScenario
from cdd_guidance.practices.stories.model.code_story_model import CodeEpic
from cdd_guidance.practices.stories.model.script_story_model import ScriptStory


class TypeScriptScenario(BraceScenario):
    """A scenario read from a TypeScript story file."""


class TypeScriptStory(ScriptStory):
    scenario_type = TypeScriptScenario
    language = TYPESCRIPT


class TypeScriptEpic(CodeEpic):
    """An epic or sub-epic whose stories a TypeScript story file holds."""
