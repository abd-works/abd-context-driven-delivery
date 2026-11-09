"""PythonStoryModel - runnable `*_story.test.py` per Story.
"""

from __future__ import annotations

import re
from typing import List

from cdd_guidance.practices.clean_engineering.model.code_body import PYTHON
from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModel
from cdd_guidance.practices.stories.model.python.nodes import PythonEpic, PythonStory
from cdd_guidance.practices.stories.model.python.story_file import PythonStoryFile
from cdd_guidance.practices.stories.model.story_file import flat_steps
from cdd_guidance.practices.stories.model.story_model import Background, Epic, Story
from cdd_guidance.practices.stories.model.story_writing import StoryWriting, background_examples_line, example_names_of, story_description


class PythonStoryWriting(StoryWriting):
    """How Python writes stories: `with story(...)`, `with scenario(...)`, and `with given(...)` blocks, the
    scenarios back to back, and the story's description and background as comments."""

    file_name_template = "{snake}_story.test.py"
    scenario_indent = "        "
    scenario_gap: List[str] = []
    quote_mark = '"'
    no_scenarios = ["        pass"]
    empty_block = ["pass"]
    placeholder = "pass"
    scenario_opening = "{indent}with scenario({name}):"
    step_opening = "{indent}with {verb}({text}):"
    and_opening = "{indent}with {verb}({text}):"
    and_verbs = ("and_", "but_")
    verbs = {"Given": "given", "When": "when", "Then": "then", "But": "but_", "And": "and_"}
    default_verb = "then"

    def file_header(self, epic: Epic, parent: str) -> List[str]:
        names = example_names_of(list(epic.stories))
        example_import = [f"from examples import {', '.join(names)}", ""] if names else []
        heading = [self.language.comment(f"Epic: {epic.name}"), self.language.comment(f"Orders: {epic.order_path()}"), ""]
        return ["from __future__ import annotations", "", "from story_test import and_, background, given, scenario, story, then, when", *example_import, "", *heading]

    def story_open(self, story: "Story") -> List[str]:
        lines = [self.language.comment(f"Story: {story.name}"), *story_description(story, "# ")]
        if story.domain_terms:
            lines.append(self.language.comment("Domain terms: " + ", ".join(story.domain_terms)))
        return lines + background_examples_line(story, "# ") + [f"with story({self.quoted(story.name)}):"]

    def story_background_lines(self, background: "Background") -> List[str]:
        scope = background.name if re.fullmatch(r"\w+", background.name or "") else "each"
        lines = [f"{self.language.indent}with background.{scope}:"]
        for step in background.steps:
            lines.extend(self.step_lines((step, "given", []), self.language.indent * 2))
        return lines

    def scenario_background_lines(self, background: "Background", indent: str) -> List[str]:
        lines = [f"{indent}{self.language.comment('background: ' + background.name)}"]
        for step in flat_steps(background.steps):
            lines.append(f"{indent}{self.language.comment(f'background-step: {step.keyword} | {step.text}')}")
        return lines


class PythonStoryModel(CodeStoryModel):
    LEAF_EXTENSION = "_story.test.py"
    story_file_suffixes = (LEAF_EXTENSION,)
    epic_type = PythonEpic
    story_type = PythonStory
    language = PYTHON
    writing_type = PythonStoryWriting

    def story_file(self, content: str) -> PythonStoryFile:
        return PythonStoryFile(self.language, content)
