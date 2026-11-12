"""Python nodes: Python, then code, then the story model."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List

from cdd_guidance.practices.stories.model.code_story_model import CodeEpic, CodeScenario, CodeStory, unescaped
from cdd_guidance.practices.stories.model.python.shared_story_file import SharedStoryFile
from cdd_guidance.practices.stories.model.story_model import Background


class PythonScenario(CodeScenario):
    _CALL = re.compile(r'with (?P<kw>given|when|then|and_|but_)\("(?P<text>(?:\\.|[^"\\])*)"\)')
    _SCENARIO = re.compile(r'with scenario\("(?P<name>(?:\\.|[^"\\])*)"\)\s*:')
    _IMPORT = re.compile(r"from\s+\S*examples\S*\s+import\s+(?P<names>.+)")

    @classmethod
    def calls_in(cls, body: str) -> List[tuple]:
        calls = []
        for match in cls._CALL.finditer(body):
            keyword = {"and_": "and", "but_": "but"}.get(match.group("kw"), match.group("kw"))
            calls.append((keyword, unescaped(match.group("text"))))
        return calls

    @classmethod
    def backgrounds_in(cls, content: str) -> List[Background]:
        match = re.search(r"with background\.(\w+)\s*:", content)
        if match is None:
            return []
        start = match.end()
        scenario = cls._SCENARIO.search(content, start)
        body = content[start:scenario.start()] if scenario else content[start:]
        steps = cls.steps_from(cls.calls_in(body))
        background = Background(match.group(1), 1)
        background.steps = steps
        return [background]


class PythonStory(CodeStory):
    scenario_type = PythonScenario
    description_mark = r"^#\s*"
    _STORY_START = re.compile(r"(?=^# Story:)", re.M)
    _STORY_MARK = re.compile(r'with story\("')
    _NAME = re.compile(r'with story\("(?P<name>[^"]+)"\)')

    @classmethod
    def load_all(cls, content: str) -> List["CodeStory"]:
        """Every story in one story file: a shared story file's, read from its scenario and step functions; any other
        story file's, from its `with story` blocks."""
        return cls.stories_in(content, None)

    @classmethod
    def stories_in(cls, content: str, project: Path | None) -> List["CodeStory"]:
        """Every story in one story file of project: a shared story file's examples module is looked for there first,
        then in the folders Python imports from."""
        if SharedStoryFile.holds(content):
            search = [*([project] if project is not None else []), Path.cwd(), *map(Path, sys.path)]
            return SharedStoryFile(content, search).stories(cls)
        return super().load_all(content)


class PythonEpic(CodeEpic):
    pass
