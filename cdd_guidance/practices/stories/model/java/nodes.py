"""Java nodes: Java, then code, then the story model."""
from __future__ import annotations

import re
from typing import List

from cdd_guidance.practices.stories.model.code_story_model import CodeEpic, CodeScenario, CodeStory
from cdd_guidance.practices.stories.model.story_model import Background, Step, StepType


_BACKGROUND_HEADING = re.compile(r"\s*\*\s*BACKGROUND:\s*(.+)")
_BACKGROUND_GIVEN = re.compile(r"\s*\*\s*GIVEN:\s*(.+)")
_CONTINUATION = re.compile(r"\s*\*\s*(AND|BUT):\s*(.+)", re.IGNORECASE)


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
        lines = content.splitlines()
        for line in lines[: next((index for index, line in enumerate(lines) if "SCENARIO:" in line), len(lines))]:
            heading, given, extra = _BACKGROUND_HEADING.match(line), _BACKGROUND_GIVEN.match(line), _CONTINUATION.match(line)
            if heading:
                found.append(Background(heading.group(1).strip(), len(found) + 1))
            elif given and found:
                steps = found[-1].steps
                found[-1].steps = [*steps, Step(given.group(1).strip(), StepType.GIVEN, len(steps) + 1, keyword="Given")]
            elif extra and found and found[-1].steps:
                previous = found[-1].steps[-1]
                continued = Step(extra.group(2).strip(), previous.step_type, len(previous.ands) + 1, keyword=extra.group(1).lower())
                previous.ands = [*previous.ands, continued]
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
