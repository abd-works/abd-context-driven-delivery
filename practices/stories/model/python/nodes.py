"""Python nodes: Python, then code, then the story model."""
from __future__ import annotations

import re
from typing import List

from practices.stories.model.code_story_model import CodeEpic, CodeScenario, CodeStory
from practices.stories.model.story_model import Background, StepType, Story


class PythonScenario(CodeScenario):
    _CALL = re.compile(r'with (?P<kw>given|when|then|and_)\("(?P<text>(?:\\.|[^"\\])*)"\)')
    _SCENARIO = re.compile(r'with scenario\("(?P<name>(?:\\.|[^"\\])*)"\)\s*:')
    _IMPORT = re.compile(r"from\s+\S*examples\S*\s+import\s+(?P<names>.+)")

    def calls_in(self, body: str) -> List[tuple]:
        calls = []
        for match in self._CALL.finditer(body):
            keyword = "and" if match.group("kw") == "and_" else match.group("kw")
            calls.append((keyword, match.group("text")))
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
                if name and name != "(":
                    names.append(name)
        return names

    @classmethod
    def create(cls, scenario) -> List[str]:
        lines: List[str] = []
        for step in scenario.steps_in(StepType.GIVEN):
            lines.extend(cls._step("given", step, 12))
        for when_steps, then_steps in scenario.when_then_runs():
            for index, step in enumerate(when_steps):
                lines.extend(cls._step("when" if index == 0 else "and_", step, 12))
            for index, step in enumerate(then_steps):
                lines.extend(cls._step("then" if index == 0 else "and_", step, 12))
        if not lines:
            lines.append("            pass")
        return lines

    @staticmethod
    def _step(verb: str, step, indent: int) -> List[str]:
        pad = " " * indent
        lines = [
            f'{pad}with {verb}("{_quote(step.text)}"):',
            f"{pad}    pass",
        ]
        for extra in step.ands:
            lines.extend([
                f'{pad}with and_("{_quote(extra.text)}"):',
                f"{pad}    pass",
            ])
        return lines


def _quote(value: str) -> str:
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
    def story_text(cls, story: Story) -> str:
        lines: List[str] = [f"# Story: {story.name}"]
        actor = (story.actors[0] if story.actors else "").strip()
        if actor:
            lines.append(f"# Actor: {actor}")
        if story.domain_terms:
            lines.append("# Domain terms: " + ", ".join(story.domain_terms))
        lines.append(f'with story("{_quote(story.name)}"):')
        lines.append("    with background.each:")
        for background in story.backgrounds:
            for step in background.steps:
                lines.extend(PythonScenario._step("given", step, 8))
        if not story.scenarios and not story.backgrounds:
            lines.append("        pass")
        for scenario in story.scenarios:
            lines.append(f'        with scenario("{_quote(scenario.name)}"):')
            lines.extend(PythonScenario.create(scenario))
        lines.append("")
        return "\n".join(lines)

    @classmethod
    def create(cls, story: Story, **kwargs) -> str:
        return "\n".join([
            "from __future__ import annotations",
            "",
            "from story_test import and_, background, given, scenario, story, then, when",
            "",
            cls.story_text(story),
        ])


class PythonEpic(CodeEpic):
    def _file_stories(self):
        return [story for story in self.stories if story.scenarios]

    def _write_stories(self, parent: str, files: dict, tests_root: str) -> None:
        stories = self._file_stories()
        if not stories:
            return
        blocks = "\n".join(PythonStory.story_text(story) for story in stories)
        files[f"{parent}/{self.snake()}_story.test.py"] = "\n".join([
            "from __future__ import annotations",
            "",
            "from story_test import and_, background, given, scenario, story, then, when",
            "",
            f"# Epic: {self.name}",
            "",
            blocks,
        ])
