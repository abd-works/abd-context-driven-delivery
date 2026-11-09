"""Java nodes: Java, then code, then the story model."""
from __future__ import annotations

import re
from typing import List

from cdd_guidance.practices.stories.model.code_story_model import CodeEpic, CodeScenario, CodeStory
from cdd_guidance.practices.stories.model.story_model import Background, Step, StepType


class JavaScenario(CodeScenario):
    _SCENARIO = re.compile(r"SCENARIO:\s*(?P<name>.+)")
    _EXAMPLES_LINE = re.compile(r"EXAMPLES:\s*(.+)")

    @classmethod
    def calls_in(cls, body: str) -> List[tuple]:
        calls = []
        for line in body.splitlines():
            match = re.match(r"\s*\*\s*(GIVEN|WHEN|THEN|AND|BUT):\s*(.+)", line, re.IGNORECASE)
            if match:
                calls.append((match.group(1), match.group(2).strip()))
        return calls

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

    def lines(self) -> List[str]:
        """This scenario as the comment lines a Java story test lists it in."""
        lines = [f" * SCENARIO: {self.name}"]
        for background in self.backgrounds:
            lines.append(f" * background: {background.name}")
            for step in background.steps:
                lines.append(f" * background-step: {step.keyword} | {step.text}")
                for extra in step.ands:
                    lines.append(f" * background-step: {extra.keyword} | {extra.text}")
        if self.examples:
            lines.append(" * EXAMPLES: " + ", ".join(self.examples))
        for step in self.steps:
            lines.append(f" * {step.keyword.upper()}: {step.text}")
            for extra in step.ands:
                lines.append(f" * {extra.keyword.upper()}: {extra.text}")
        return lines


class JavaStory(CodeStory):
    scenario_type = JavaScenario

    _STORY_START = re.compile(r"(?=/\*\* Story:)")


class JavaEpic(CodeEpic):
    pass
