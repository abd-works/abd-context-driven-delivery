"""Java nodes: Java, then code, then the story model."""
from __future__ import annotations

import re
from typing import List

from practices.stories.model.code_story_model import CodeEpic, CodeScenario, CodeStory
from practices.stories.model.story_model import Background, Story


class JavaScenario(CodeScenario):
    _SCENARIO = re.compile(r"SCENARIO:\s*(.+)")

    def calls_in(self, body: str) -> List[tuple]:
        return []

    @classmethod
    def scenario_blocks(cls, content: str) -> List[tuple]:
        return [(match.group(1).strip(), "") for match in cls._SCENARIO.finditer(content)]

    @classmethod
    def backgrounds_in(cls, content: str) -> List[Background]:
        return []

    @classmethod
    def example_names(cls, content: str) -> List[str]:
        return []

    @classmethod
    def create(cls, scenario) -> List[str]:
        return [f" * SCENARIO: {scenario.name}"]


class JavaStory(CodeStory):
    scenario_type = JavaScenario

    @classmethod
    def load_all(cls, content: str) -> List["JavaStory"]:
        chunks = re.split(r"(?=/\*\* Story:)", content)
        stories = [cls.load(chunk, "") for chunk in chunks if "Story:" in chunk]
        return stories or [cls.load(content, "")]

    @classmethod
    def load(cls, content: str, story_slug: str) -> "JavaStory":
        name_match = re.search(r"Story:\s*(.+)", content)
        story_name = name_match.group(1).strip() if name_match else story_slug.replace("-", " ").title()
        story_name = re.sub(r"\s*\(tier-neutral\)\.?\s*$", "", story_name).strip()
        story = cls(story_name, 1)
        actor_match = re.search(r"Actor:\s*(.+)", content)
        if actor_match:
            story.actors = [actor_match.group(1).strip()]
        story.fill(content)
        return story

    @classmethod
    def story_text(cls, story: Story) -> str:
        actor = (story.actors[0] if story.actors else "").strip()
        lines = [f"/** Story: {story.name}"]
        if actor:
            lines.append(f" * Actor: {actor}")
        for scenario in story.scenarios:
            lines.extend(JavaScenario.create(scenario))
        lines.append(" */")
        lines.append("")
        return "\n".join(lines)

    @classmethod
    def create(cls, story: Story, **kwargs) -> str:
        return cls.story_text(story)


class JavaEpic(CodeEpic):
    def _file_stories(self):
        return [story for story in self.stories if story.scenarios]

    def _write_stories(self, parent: str, files: dict, tests_root: str) -> None:
        stories = self._file_stories()
        if not stories:
            return
        blocks = "\n".join(JavaStory.story_text(story) for story in stories)
        files[f"{parent}/{self.pascal()}Story.java"] = "\n".join([
            f"// Epic: {self.name}",
            "",
            blocks,
        ])
