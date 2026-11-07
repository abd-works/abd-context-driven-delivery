"""JavaScript nodes: JavaScript, then the brace-language story nodes, then code, then the story model."""
from __future__ import annotations

import re
from typing import List

from cdd_guidance.practices.stories.model.brace_story import BraceScenario
from cdd_guidance.practices.stories.model.code_story_model import CodeEpic, CodeStory


class JavaScriptScenario(BraceScenario):
    """A scenario read from a JavaScript story file."""


class JavaScriptStory(CodeStory):
    scenario_type = JavaScriptScenario

    @classmethod
    def load_all(cls, content: str) -> List["JavaScriptStory"]:
        chunks = re.split(r"(?=/\*\*\s*\n \* Story:)", content)
        stories = [cls.load(chunk, "") for chunk in chunks if "Story:" in chunk or "story(" in chunk]
        return stories or [cls.load(content, "")]

    @classmethod
    def load(cls, content: str, story_slug: str) -> "JavaScriptStory":
        name_match = re.search(r"story\(\s*(['\"])((?:\\.|(?!\1).)*)\1", content)
        story = cls(cls.name_read(name_match.group(2) if name_match else None, story_slug), 1)
        story.read_description(content)
        story.fill(content)
        return story


class JavaScriptEpic(CodeEpic):
    pass
