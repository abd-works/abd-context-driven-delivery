"""Python nodes: Python, then code, then the story model."""
from __future__ import annotations

import re
from typing import List

from cdd_guidance.practices.stories.model.code_story_model import CodeEpic, CodeScenario, CodeStory, unescaped
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


def quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


class PythonStory(CodeStory):
    scenario_type = PythonScenario
    description_mark = r"^#\s*"
    _STORY_START = re.compile(r"(?=^# Story:)", re.M)
    _STORY_MARK = re.compile(r'with story\("')
    _NAME = re.compile(r'with story\("(?P<name>[^"]+)"\)')


class PythonEpic(CodeEpic):
    pass
