"""JavaStoryModel - runnable `{Story}Story.java` per Story."""

from __future__ import annotations

from pathlib import Path
from typing import List

from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModel
from cdd_guidance.practices.stories.model.java.nodes import JavaEpic, JavaStory
from cdd_guidance.practices.stories.model.story_model import Epic, Story


class JavaStoryModel(CodeStoryModel):
    LEAF_EXTENSION = "Story.java"
    story_file_suffixes = (LEAF_EXTENSION,)
    epic_type = JavaEpic
    story_type = JavaStory

    @classmethod
    def is_story_file(cls, path: "str | Path") -> bool:
        """A story file, not a helper or a spec beside it."""
        name = Path(path).name
        return super().is_story_file(path) and not name.endswith("Helper.java") and "Spec" not in name

    def file_name(self, epic: Epic) -> str:
        return f"{epic.pascal()}Story.java"

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
