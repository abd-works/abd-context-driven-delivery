"""PythonStoryModel - runnable `*_story.test.py` per Story.
"""

from __future__ import annotations

import re
from typing import List

from cdd_guidance.practices.clean_engineering.model.code_body import PYTHON
from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModel, example_names_of
from cdd_guidance.practices.stories.model.python.nodes import PythonEpic, PythonStory, quote
from cdd_guidance.practices.stories.model.python.story_file import PythonStoryFile
from cdd_guidance.practices.stories.model.story_file import flat_steps
from cdd_guidance.practices.stories.model.story_model import Background, Epic, Scenario, Step, Story

_VERBS = {"Given": "given", "When": "when", "Then": "then", "But": "but_", "And": "and_"}


class PythonStoryModel(CodeStoryModel):
    LEAF_EXTENSION = "_story.test.py"
    story_file_suffixes = (LEAF_EXTENSION,)
    epic_type = PythonEpic
    story_type = PythonStory
    language = PYTHON
    scenario_indent = "        "
    scenario_gap: List[str] = []

    def story_file(self, content: str) -> PythonStoryFile:
        return PythonStoryFile(self.language, content)

    def file_name(self, epic: Epic) -> str:
        return f"{epic.snake()}_story.test.py"

    def file_header(self, epic: Epic, parent: str) -> List[str]:
        names = example_names_of(list(epic.stories))
        example_import = [f"from examples import {', '.join(names)}", ""] if names else []
        return [
            "from __future__ import annotations",
            "",
            "from story_test import and_, background, given, scenario, story, then, when",
            *example_import,
            "",
            f"# Epic: {epic.name}",
            f"# Orders: {epic.order_path()}",
            "",
        ]

    def verb(self, step: Step) -> str:
        return _VERBS.get(step.keyword, "then")

    def story_open(self, story: Story) -> List[str]:
        lines: List[str] = [f"# Story: {story.name}", *self.description_lines(story, "# ")]
        if story.domain_terms:
            lines.append("# Domain terms: " + ", ".join(story.domain_terms))
        example_line = self.story_type.background_example_line(story, "# ")
        if example_line:
            lines.append(example_line)
        return lines + [f'with story("{quote(story.name)}"):']

    def story_background_lines(self, background: Background) -> List[str]:
        scope = background.name if re.fullmatch(r"\w+", background.name or "") else "each"
        lines = [f"    with background.{scope}:"]
        for step in background.steps:
            lines.extend(self.step_lines((step, "given", []), "        "))
        return lines

    def no_scenarios_lines(self) -> List[str]:
        return ["        pass"]

    def scenario_open(self, scenario: Scenario, indent: str) -> List[str]:
        return [f'{indent}with scenario("{quote(scenario.name)}"):']

    def scenario_background_lines(self, background: Background, indent: str) -> List[str]:
        lines = [f"{indent}# background: {background.name}"]
        for step in flat_steps(background.steps):
            lines.append(f"{indent}# background-step: {step.keyword} | {step.text}")
        return lines

    def step_open(self, verb: str, step: Step, indent: str) -> str:
        return f'{indent}with {verb}("{quote(step.text)}"):'

    def and_open(self, step: Step, indent: str) -> str:
        return f'{indent}with {"but_" if step.keyword == "But" else "and_"}("{quote(step.text)}"):'

    def step_placeholder(self) -> str:
        return "pass"

    def empty_block(self) -> List[str]:
        return ["pass"]
