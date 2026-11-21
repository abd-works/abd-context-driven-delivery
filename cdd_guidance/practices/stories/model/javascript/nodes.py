"""JavaScript nodes: JavaScript, then the script languages, then code, then the story model."""
from __future__ import annotations

from cdd_guidance.practices.clean_engineering.model.code_body import JAVASCRIPT
from cdd_guidance.practices.stories.model.brace_story import BraceScenario
from cdd_guidance.practices.stories.model.code_story_model import CodeEpic
from cdd_guidance.practices.stories.model.script_story_model import ScriptStory


class JavaScriptScenario(BraceScenario):
    """A scenario read from a JavaScript story file."""


class JavaScriptStory(ScriptStory):
    scenario_type = JavaScriptScenario
    language = JAVASCRIPT


class JavaScriptEpic(CodeEpic):
    """An epic or sub-epic whose stories a JavaScript story file holds."""
