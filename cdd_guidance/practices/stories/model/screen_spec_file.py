"""ScreenSpecFile. A screen spec in TypeScript or JavaScript (``*.story.ui.spec.ts``, ``*.story.ui.spec.js``) read as
the code of its stories' scenarios.

A screen spec does what a person does on a page: each ``test.describe('Story', ...)`` is one story, and each
``test('Scenario', async ({ page }) => { ... })`` inside it one of its scenarios, written as code with no step words. Its
steps are read from the test's statements: those that only seed the fixture before anything happens are its Givens,
those that check what the page shows (``expect(...)``) its Thens, and the rest its Whens. Each step's text is the first
line of its first statement, and its body the statements it is made of, so it is linked to what they call.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import cached_property
from typing import TYPE_CHECKING

from cdd_guidance.practices.source_code import BracketStructure
from cdd_guidance.practices.source_code import CodeBody
from cdd_guidance.practices.stories.model.story_file import StoryFile
from cdd_guidance.practices.stories.model.story_model import StepType

if TYPE_CHECKING:
    from cdd_guidance.practices.stories.model.story_model import Scenario, Story

# How a screen spec's name ends before its language's extension.
SCREEN_SPEC_STEM = ".story.ui.spec"
# The call and its callback up to the `{` opening the callback's body: `test('Name', async ({ page }) => {`.
_DESCRIBE = re.compile(r"\btest\.describe\(\s*(['\"`])(?P<name>.+?)\1\s*,.*?=>\s*\{", re.S)
_TEST = re.compile(r"\btest\(\s*(['\"`])(?P<name>.+?)\1\s*,.*?=>\s*\{", re.S)
_CHECK = re.compile(r"\bexpect\s*\(")
_SEED = re.compile(r"\b(?:write|seed|reset)\w*\s*\(")
_KEYWORDS = {StepType.GIVEN: "Given", StepType.WHEN: "When", StepType.THEN: "Then"}


@dataclass
class StepLines:
    """One step of a test: the phase its statements are in and the statements' lines."""

    phase: StepType
    lines: list[str] = field(default_factory=list)


class ScreenSpecFile(StoryFile):
    """One screen spec, read once: a story for each ``test.describe``, with a scenario for each of its tests, whose steps'
    code is written in its model's language. Its own code is not kept."""

    @cached_property
    def _read(self) -> tuple[list, None]:
        return self._stories(), None

    @cached_property
    def _brackets(self) -> BracketStructure:
        return BracketStructure(self.text)

    def _stories(self) -> list:
        """The stories the file describes, each with a scenario for each of its tests."""
        story_class = self.model.story_class
        stories: dict[str, object] = {}
        for describe in _DESCRIBE.finditer(self.text):
            story = stories.setdefault(describe.group("name"), story_class(describe.group("name"), len(stories) + 1))
            for test in _TEST.finditer(self._brackets.braced(describe.end() - 1) or ""):
                story.scenarios.append(self._scenario(story, test))
        return list(stories.values())

    def _scenario(self, story: "Story", test: re.Match) -> "Scenario":
        scenario = story.scenario_class(name=test.group("name"), sequential_order=len(story.scenarios) + 1)
        body = BracketStructure(test.string).braced(test.end() - 1) or ""
        for order, step in enumerate(self._steps_in(body), start=1):
            made = scenario.step_class(step.lines[0].strip(), step.phase, order)
            made.keyword = _KEYWORDS[step.phase]
            made.body = CodeBody("\n".join(step.lines), self.model.language)
            scenario.steps.append(made)
        return scenario

    def _steps_in(self, body: str) -> list[StepLines]:
        """The test's statements grouped into steps: each run of statements of one phase is one step. A statement starts
        on a line at the body's own indentation; deeper lines continue it."""
        lines = [line for line in body.splitlines() if line.strip() and not line.strip().startswith("//")]
        base = min((len(line) - len(line.lstrip()) for line in lines), default=0)
        steps: list[StepLines] = []
        for line in lines:
            starts = len(line) - len(line.lstrip()) == base
            phase = self._phase_of(line, acted=any(step.phase is not StepType.GIVEN for step in steps)) if starts else steps[-1].phase
            if not steps or (starts and phase is not steps[-1].phase):
                steps.append(StepLines(phase))
            steps[-1].lines.append(line)
        return steps

    def _phase_of(self, statement: str, acted: bool) -> StepType:
        """A check is a Then; a seed before anything is done is a Given; anything else is a When."""
        if _CHECK.search(statement):
            return StepType.THEN
        if not acted and _SEED.search(statement):
            return StepType.GIVEN
        return StepType.WHEN


def is_screen_spec(text: str) -> bool:
    """True for the text of a screen spec: it describes its stories with ``test.describe(...)``."""
    return bool(_DESCRIBE.search(text))
