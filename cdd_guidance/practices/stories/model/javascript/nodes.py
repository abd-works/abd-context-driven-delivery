"""JavaScript nodes: JavaScript, then the brace-language story nodes, then code, then the story model."""
from __future__ import annotations

from cdd_guidance.practices.stories.model.brace_story import BraceScenario, BraceStory
from cdd_guidance.practices.stories.model.code_story_model import CodeEpic


class JavaScriptScenario(BraceScenario):
    """A scenario read from a JavaScript story file."""


class JavaScriptStory(BraceStory):
    scenario_type = JavaScriptScenario


class JavaScriptEpic(CodeEpic):
    pass
