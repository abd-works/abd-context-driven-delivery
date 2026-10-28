"""JavaScript nodes: JavaScript, then the brace-language story nodes, then code, then the story model."""
from __future__ import annotations

import re
from typing import List

from cdd_guidance.practices.stories.model.brace_story import BraceScenario
from cdd_guidance.practices.stories.model.code_story_model import CodeEpic, CodeStory
from cdd_guidance.practices.stories.model.story_model import Story


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
        story_name = name_match.group(2) if name_match else story_slug.replace("-", " ").title()
        story = cls(story_name, 1)
        actor_match = re.search(r"\*\s*Actor:\s*(.+)", content)
        if actor_match:
            story.actors = [actor_match.group(1).strip()]
        story.fill(content)
        return story

    @classmethod
    def create(
        cls,
        story: Story,
        relative_story_test_path: str = "../../story-test.js",
        relative_types_path: str | None = None,
        **kwargs,
    ) -> str:
        from cdd_guidance.practices.stories.model.javascript.javascript_story_model import JavaScriptStoryModel

        import_path = relative_types_path or relative_story_test_path
        return "\n".join([
            f'import {{ background, scenario, story }} from "{import_path}";',
            "",
            JavaScriptStoryModel().story_text(cls(story)),
        ])


class JavaScriptEpic(CodeEpic):
    pass
