"""DesktopStoryTest. A desktop story test as Stories reads it for a walk in the Claude desktop app: each story the file
writes, its scenarios, and each step with the lines the file holds below it."""

from __future__ import annotations

import itertools
import re
from pathlib import Path

from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownScenario
from cdd_guidance.practices.stories.model.markdown.scenario_file import ScenarioFileReading
from cdd_guidance.practices.stories.model.story_file import flat_steps
from cdd_guidance.practices.stories.model.story_map_files import STORY_TESTS_FOLDER, StoryMapFiles

# A line that ends the lines below a step: the next step, or a heading.
_ENDS_STEP = re.compile(r"^\s*(\*(Given|When|Then|And|But)\*\s|#)", re.IGNORECASE)


class DesktopStoryStep:
    """One step of a desktop story test, its chained steps counted as steps of their own: its keyword, its words, and
    the lines the file holds below it, up to the next step or heading."""

    def __init__(self, keyword: str, text: str, lines_below: list[str]) -> None:
        self.keyword = keyword
        self.text = text
        self.lines_below = lines_below


class DesktopStoryScenario:
    """One scenario of a desktop story test, with its steps in the file's order."""

    def __init__(self, name: str, steps: list[DesktopStoryStep]) -> None:
        self.name = name
        self.steps = steps


class DesktopStoryTest:
    """One story of a desktop story test file: the story's name, the file as a path from the project, and its
    scenarios."""

    def __init__(self, story: str, file: str, scenarios: list[DesktopStoryScenario]) -> None:
        self.story = story
        self.file = file
        self.scenarios = scenarios

    @staticmethod
    def every_one_in(project: Path) -> list["DesktopStoryTest"]:
        """The stories of every desktop story test under project's story_tests folder, in file order."""
        files = StoryMapFiles(project / STORY_TESTS_FOLDER).desktop_story_tests_below()
        return [test for file in files for test in DesktopStoryTest.read(file, file.relative_to(project).as_posix())]

    @staticmethod
    def read(file: Path, named: str) -> list["DesktopStoryTest"]:
        """The stories the desktop story test at file writes, named as named from the project."""
        text = file.read_text(encoding="utf-8")
        lines = text.splitlines()
        return [
            DesktopStoryTest(section.name.strip(), named, [_scenario(read, lines) for read in section.scenarios])
            for section in ScenarioFileReading(text, named, MarkdownScenario).read()
        ]


def _scenario(read: MarkdownScenario, lines: list[str]) -> DesktopStoryScenario:
    steps = [
        DesktopStoryStep(step.keyword, step.text, list(itertools.takewhile(lambda line: not _ENDS_STEP.match(line), lines[step.source.start_line:])))
        for step in flat_steps(read.steps)
    ]
    return DesktopStoryScenario(read.name, steps)
