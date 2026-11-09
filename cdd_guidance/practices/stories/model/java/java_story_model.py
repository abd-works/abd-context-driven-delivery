"""JavaStoryModel - runnable `{Story}Story.java` per Story."""

from __future__ import annotations

import re
from typing import List

from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModel
from cdd_guidance.practices.stories.model.java.nodes import JavaEpic, JavaStory
from cdd_guidance.practices.stories.model.story_model import Story
from cdd_guidance.practices.stories.model.story_writing import StoryWriting, background_examples_line, story_description


class JavaStoryWriting(StoryWriting):
    """How Java writes stories: each story is a doc comment of names and steps, with no code, so there is no body to
    carry."""

    file_name_template = "{pascal}Story.java"
    heading_template = ["// Epic: {name}", "// Orders: {orders}", ""]

    def story_lines(self, story: "Story") -> List[str]:
        lines = [f"/** Story: {story.name}", *story_description(story, " * "), *background_examples_line(story, " * ")]
        for background in story.backgrounds:
            lines.append(f" * BACKGROUND: {background.name}")
            for step in background.steps:
                if step.keyword != "Given":
                    continue
                lines.append(f" * GIVEN: {step.text}")
                lines.extend(f" * {extra.keyword.upper()}: {extra.text}" for extra in step.ands)
        for scenario in story.scenarios:
            lines.extend(scenario.lines())
        return lines + [" */"]


class JavaStoryModel(CodeStoryModel):
    LEAF_EXTENSION = "Story.java"
    story_file_suffixes = (LEAF_EXTENSION,)
    # A spec beside the story files names itself a spec; a helper does not end like a story file at all.
    not_story_paths = re.compile(r"Spec[^/]*$")
    epic_type = JavaEpic
    story_type = JavaStory
    writing_type = JavaStoryWriting
