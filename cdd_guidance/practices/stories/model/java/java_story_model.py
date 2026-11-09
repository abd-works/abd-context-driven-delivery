"""JavaStoryModel - runnable `{Story}Story.java` per Story."""

from __future__ import annotations

import re
from typing import List

from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModel
from cdd_guidance.practices.stories.model.java.nodes import JavaEpic, JavaStory
from cdd_guidance.practices.stories.model.story_model import Epic, Story


class JavaStoryModel(CodeStoryModel):
    LEAF_EXTENSION = "Story.java"
    story_file_suffixes = (LEAF_EXTENSION,)
    # A spec beside the story files names itself a spec; a helper does not end like a story file at all.
    not_story_paths = re.compile(r"Spec[^/]*$")
    epic_type = JavaEpic
    story_type = JavaStory

    def file_name(self, epic: Epic) -> str:
        return f"{epic.pascal()}{self.LEAF_EXTENSION}"

    def file_header(self, epic: Epic, parent: str) -> List[str]:
        return [f"// Epic: {epic.name}", f"// Orders: {epic.order_path()}", ""]

    def story_lines(self, story: Story) -> List[str]:
        """A Java story is a doc comment: names and steps, no code, so there is no body to carry."""
        lines = [f"/** Story: {story.name}", *self.description_lines(story, " * ")]
        example_line = self.story_type.background_example_line(story, " * ")
        if example_line:
            lines.append(example_line)
        for background in story.backgrounds:
            lines.append(f" * BACKGROUND: {background.name}")
            for step in background.steps:
                if step.keyword != "Given":
                    continue
                lines.append(f" * GIVEN: {step.text}")
                for extra in step.ands:
                    lines.append(f" * {extra.keyword.upper()}: {extra.text}")
        for scenario in story.scenarios:
            lines.extend(scenario.lines())
        lines.append(" */")
        return lines
