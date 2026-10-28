"""Python nodes: Python, then code, then the story model."""
from __future__ import annotations

import re
from typing import List

from cdd_guidance.practices.stories.model.code_story_model import CodeEpic, CodeScenario, CodeStory
from cdd_guidance.practices.stories.model.story_model import Background, Story


class PythonScenario(CodeScenario):
    _CALL = re.compile(r'with (?P<kw>given|when|then|and_|but_)\("(?P<text>(?:\\.|[^"\\])*)"\)')
    _SCENARIO = re.compile(r'with scenario\("(?P<name>(?:\\.|[^"\\])*)"\)\s*:')
    _IMPORT = re.compile(r"from\s+\S*examples\S*\s+import\s+(?P<names>.+)")

    def calls_in(self, body: str) -> List[tuple]:
        calls = []
        for match in self._CALL.finditer(body):
            keyword = {"and_": "and", "but_": "but"}.get(match.group("kw"), match.group("kw"))
            calls.append((keyword, _unescape(match.group("text"))))
        return calls

    @classmethod
    def scenario_blocks(cls, content: str) -> List[tuple]:
        matches = list(cls._SCENARIO.finditer(content))
        blocks = []
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
            blocks.append((match.group("name"), content[match.end():end]))
        return blocks

    @classmethod
    def backgrounds_in(cls, content: str) -> List[Background]:
        match = re.search(r"with background\.(\w+)\s*:", content)
        if match is None:
            return []
        start = match.end()
        scenario = cls._SCENARIO.search(content, start)
        body = content[start:scenario.start()] if scenario else content[start:]
        steps = cls.steps_from(cls(name="").calls_in(body))
        background = Background(match.group(1), 1)
        background.steps = steps
        return [background]

    @classmethod
    def example_names(cls, content: str) -> List[str]:
        names: List[str] = []
        for match in cls._IMPORT.finditer(content):
            for part in match.group("names").split(","):
                name = part.strip().split(" as ")[-1].strip()
                if name and name != "(" and name not in names:
                    names.append(name)
        for match in re.finditer(r"examples:\s*(.+)", content):
            for part in match.group(1).split(","):
                name = part.strip()
                if name and name not in names:
                    names.append(name)
        return names


def _unescape(value: str) -> str:
    return value.replace('\\"', '"').replace("\\\\", "\\")


def quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


class PythonStory(CodeStory):
    scenario_type = PythonScenario

    @classmethod
    def load_all(cls, content: str) -> List["PythonStory"]:
        chunks = re.split(r"(?=^# Story:)", content, flags=re.M)
        stories = [cls.load(chunk, "") for chunk in chunks if 'with story("' in chunk]
        return stories or [cls.load(content, "")]

    @classmethod
    def load(cls, content: str, story_slug: str) -> "PythonStory":
        name_match = re.search(r'with story\("([^"]+)"\)', content)
        story_name = (
            name_match.group(1).strip()
            if name_match
            else story_slug.replace("-", " ").title()
        )
        story_name = re.sub(r"\s*\(tier-neutral\)\.?\s*$", "", story_name).strip()
        story = cls(story_name, 1)
        actor_match = re.search(r"^# Actor:\s*(.+)$", content, re.MULTILINE)
        if actor_match:
            story.actors = [actor_match.group(1).strip()]
        domain_match = re.search(r"^# Domain terms:\s*(.+)$", content, re.MULTILINE)
        if domain_match:
            story.domain_terms = [term.strip() for term in domain_match.group(1).split(",") if term.strip()]
        story.fill(content)
        return story

    @classmethod
    def create(cls, story: Story, **kwargs) -> str:
        from cdd_guidance.practices.stories.model.python.python_story_model import PythonStoryModel

        return "\n".join([
            "from __future__ import annotations",
            "",
            "from story_test import and_, background, given, scenario, story, then, when",
            "",
            PythonStoryModel().story_text(cls(story)),
        ])


class PythonEpic(CodeEpic):
    pass
