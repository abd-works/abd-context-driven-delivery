"""Java nodes: Java, then code, then the story model."""
from __future__ import annotations

import re
from typing import List

from cdd_guidance.practices.stories.model.code_story_model import CodeEpic, CodeScenario, CodeStory, StorySyntax
from cdd_guidance.practices.stories.model.story_model import Background, Step, StepType


_BACKGROUND_HEADING = re.compile(r"\s*\*\s*BACKGROUND:\s*(.+)")
_BACKGROUND_GIVEN = re.compile(r"\s*\*\s*GIVEN:\s*(.+)")
_CONTINUATION = re.compile(r"\s*\*\s*(AND|BUT):\s*(.+)", re.IGNORECASE)


class JavaSyntax(StorySyntax):
    """How a Java story test writes stories: the comment lines above its test methods, `SCENARIO:`, `GIVEN:` and the
    other step words in capitals."""

    scenario_pattern = re.compile(r"SCENARIO:\s*(?P<name>.+)")
    examples_line = re.compile(r"EXAMPLES:\s*(.+)")
    story_start = re.compile(r"(?=/\*\* Story:)")

    def backgrounds_in(self, content: str) -> List[Background]:
        found: List[Background] = []
        lines = content.splitlines()
        for line in lines[: next((index for index, line in enumerate(lines) if "SCENARIO:" in line), len(lines))]:
            self._read_background_line(line, found)
        return found

    def _read_background_line(self, line: str, found: List[Background]) -> None:
        """A background heading opens the next background; a GIVEN line adds its step to the last one, and an AND or BUT
        line chains onto that background's last step."""
        heading, given, extra = _BACKGROUND_HEADING.match(line), _BACKGROUND_GIVEN.match(line), _CONTINUATION.match(line)
        if heading:
            found.append(Background(heading.group(1).strip(), len(found) + 1))
        elif given and found:
            steps = found[-1].steps
            found[-1].steps = [*steps, Step(given.group(1).strip(), StepType.GIVEN, len(steps) + 1)]
        elif extra and found and found[-1].steps:
            found[-1].steps[-1].continue_with(extra.group(1).lower(), extra.group(2).strip())

    def _calls_in(self, body: str) -> List[tuple]:
        calls = []
        for line in body.splitlines():
            match = re.match(r"\s*\*\s*(GIVEN|WHEN|THEN|AND|BUT):\s*(.+)", line, re.IGNORECASE)
            if match:
                calls.append((match.group(1), match.group(2).strip()))
        return calls


class JavaScenario(CodeScenario):
    syntax = JavaSyntax()

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
    syntax = JavaScenario.syntax


class JavaEpic(CodeEpic):
    pass
