"""Java nodes: Java, then code, then the story model."""
from __future__ import annotations

import re
from typing import List

from practices.stories.model.code_story_model import CodeEpic, CodeScenario, CodeStory
from practices.stories.model.story_model import Background, Step, StepType, Story


class JavaScenario(CodeScenario):
    _SCENARIO = re.compile(r"SCENARIO:\s*(.+)")

    def calls_in(self, body: str) -> List[tuple]:
        calls = []
        for line in body.splitlines():
            match = re.match(r"\s*\*\s*(GIVEN|WHEN|THEN|AND|BUT):\s*(.+)", line, re.IGNORECASE)
            if match:
                calls.append((match.group(1), match.group(2).strip()))
        return calls

    @classmethod
    def scenario_blocks(cls, content: str) -> List[tuple]:
        matches = list(cls._SCENARIO.finditer(content))
        blocks = []
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
            blocks.append((match.group(1).strip(), content[match.end():end]))
        return blocks

    @classmethod
    def backgrounds_in(cls, content: str) -> List[Background]:
        found: List[Background] = []
        for line in content.splitlines():
            if re.search(r"SCENARIO:", line):
                break
            heading = re.match(r"\s*\*\s*BACKGROUND:\s*(.+)", line)
            if heading:
                found.append(Background(heading.group(1).strip(), len(found) + 1))
                continue
            given = re.match(r"\s*\*\s*GIVEN:\s*(.+)", line)
            if given and found:
                step = Step(
                    text=given.group(1).strip(),
                    step_type=StepType.GIVEN,
                    sequential_order=len(found[-1].steps) + 1,
                    keyword="Given",
                )
                found[-1].steps = [*found[-1].steps, step]
                continue
            extra = re.match(r"\s*\*\s*(AND|BUT):\s*(.+)", line, re.IGNORECASE)
            if extra and found and found[-1].steps:
                previous = found[-1].steps[-1]
                word = extra.group(1).lower()
                previous.ands = [
                    *previous.ands,
                    Step(extra.group(2).strip(), previous.step_type, len(previous.ands) + 1, keyword=word),
                ]
        return found

    @classmethod
    def example_names(cls, content: str) -> List[str]:
        names: List[str] = []
        for match in re.finditer(r"EXAMPLES:\s*(.+)", content):
            for part in match.group(1).split(","):
                name = part.strip()
                if name and name not in names:
                    names.append(name)
        return names

    @classmethod
    def create(cls, scenario) -> List[str]:
        lines = [f" * SCENARIO: {scenario.name}"]
        for background in scenario.backgrounds:
            lines.append(f" * background: {background.name}")
            for step in background.steps:
                lines.append(f" * background-step: {step.keyword} | {step.text}")
                for extra in step.ands:
                    lines.append(f" * background-step: {extra.keyword} | {extra.text}")
        if scenario.examples:
            lines.append(" * EXAMPLES: " + ", ".join(scenario.examples))
        for step in scenario.steps:
            lines.append(f" * {step.keyword.upper()}: {step.text}")
            for extra in step.ands:
                lines.append(f" * {extra.keyword.upper()}: {extra.text}")
        return lines


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
        example_line = CodeStory.background_example_line(story, " * ")
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
            lines.extend(JavaScenario.create(scenario))
        lines.append(" */")
        lines.append("")
        return "\n".join(lines)

    @classmethod
    def create(cls, story: Story, **kwargs) -> str:
        return cls.story_text(story)


class JavaEpic(CodeEpic):
    def _write_stories(self, parent: str, files: dict, tests_root: str) -> None:
        stories = self._file_stories()
        if not stories:
            return
        blocks = "\n".join(JavaStory.story_text(story) for story in stories)
        files[f"{parent}/{self.pascal()}Story.java"] = "\n".join([
            f"// Epic: {self.name}",
            f"// Orders: {self.order_path()}",
            "",
            blocks,
        ])
