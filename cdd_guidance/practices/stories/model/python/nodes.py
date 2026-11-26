"""Python nodes: Python, then code, then the story model."""
from __future__ import annotations

import re
from typing import List

from cdd_guidance.practices.stories.model.code_story_map import CodeEpic, CodeScenario, CodeStory, StorySyntax, unescaped
from cdd_guidance.practices.stories.model.story_map import Background


class PythonSyntax(StorySyntax):
    """How a Python story file writes stories: `with story(...)`, `with scenario(...)` and `with given(...)` blocks,
    a story's comment lines opening with `#`."""

    _CALL = re.compile(r'with (?P<kw>given|when|then|and_|but_)\("(?P<text>(?:\\.|[^"\\])*)"\)')
    scenario_pattern = re.compile(r'with scenario\("(?P<name>(?:\\.|[^"\\])*)"\)\s*:')
    import_pattern = re.compile(r"from\s+\S*examples\S*\s+import\s+(?P<names>.+)")
    description_mark = r"^#\s*"
    story_start = re.compile(r"(?=^# Story:)", re.M)
    story_mark = re.compile(r'with story\("')
    story_name_pattern = re.compile(r'with story\("(?P<name>[^"]+)"\)')

    def backgrounds_in(self, content: str) -> List[Background]:
        match = re.search(r"with background\.(\w+)\s*:", content)
        if match is None:
            return []
        start = match.end()
        scenario = self.scenario_pattern.search(content, start)
        body = content[start:scenario.start()] if scenario else content[start:]
        background = Background(match.group(1), 1)
        background.steps = self.steps_in(body)
        return [background]

    def _calls_in(self, body: str) -> List[tuple]:
        calls = []
        for match in self._CALL.finditer(body):
            keyword = {"and_": "and", "but_": "but"}.get(match.group("kw"), match.group("kw"))
            calls.append((keyword, unescaped(match.group("text"))))
        return calls


class PythonScenario(CodeScenario):
    syntax = PythonSyntax()


class PythonStory(CodeStory):
    scenario_class = PythonScenario
    syntax = PythonScenario.syntax


class PythonEpic(CodeEpic):
    story_class = PythonStory
