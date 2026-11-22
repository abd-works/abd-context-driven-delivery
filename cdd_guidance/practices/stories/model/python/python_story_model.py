"""PythonStoryModel - runnable `*_story.test.py` per Story.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from cdd_guidance.practices.source_code import PYTHON
from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModel
from cdd_guidance.practices.stories.model.python.nodes import PythonEpic
from cdd_guidance.practices.stories.model.python.shared_story_file import SHARED_SUFFIX, SharedStoryFile, is_shared_story_file
from cdd_guidance.practices.stories.model.python.story_file import PythonStoryFile
from cdd_guidance.practices.stories.model.story_file import StoryFile, flat_steps
from cdd_guidance.practices.stories.model.story_model import Background, Story
from cdd_guidance.practices.stories.model.story_writing import StepClause, StoryFilePlace, StoryWriting, background_examples_line, example_names_of, story_description


class PythonStoryWriting(StoryWriting):
    """How Python writes stories: `with story(...)`, `with scenario(...)`, and `with given(...)` blocks, the
    scenarios back to back, and the story's description and background as comments."""

    file_name_template = "{snake}_story.test.py"
    scenario_indent = "    "
    scenario_gap: List[str] = []
    quote_mark = '"'
    no_scenarios = ["    pass"]
    empty_block = ["pass"]
    placeholder = "pass"
    scenario_opening = "{indent}with scenario({name}):"
    step_opening = "{indent}with {verb}({text}):"
    and_opening = "{indent}with {verb}({text}):"
    and_verbs = ("and_", "but_")
    verbs = {"Given": "given", "When": "when", "Then": "then", "But": "but_", "And": "and_"}
    default_verb = "then"

    def file_header(self, place: StoryFilePlace) -> List[str]:
        names = example_names_of(place.stories)
        example_import = [f"from examples import {', '.join(names)}", ""] if names else []
        heading = [self.language.comment(f"Epic: {place.epic.name}"), self.language.comment(f"Orders: {place.orders}"), ""]
        return ["from __future__ import annotations", "", "from story_test import and_, background, but_, given, scenario, story, then, when", *example_import, "", *heading]

    def story_open(self, story: "Story") -> List[str]:
        lines = [self.language.comment(f"Story: {story.name}"), *story_description(story, "# ")]
        if story.domain_terms:
            lines.append(self.language.comment("Domain terms: " + ", ".join(story.domain_terms)))
        return lines + background_examples_line(story, "# ") + [f"with story({self._quoted(story.name)}):"]

    def story_background_lines(self, background: "Background") -> List[str]:
        scope = background.name if re.fullmatch(r"\w+", background.name or "") else "each"
        lines = [f"{self.language.indent}with background.{scope}:"]
        for step in background.steps:
            lines.extend(self._step_lines(StepClause(step, "given"), self.language.indent * 2))
        return lines

    def scenario_background_lines(self, background: "Background", indent: str) -> List[str]:
        lines = [f"{indent}{self.language.comment('background: ' + background.name)}"]
        for step in flat_steps(background.steps):
            lines.append(f"{indent}{self.language.comment(f'background-step: {step.keyword} | {step.text}')}")
        return lines


class PythonStoryModel(CodeStoryModel):
    LEAF_EXTENSION = "_story.test.py"
    story_file_suffixes = (LEAF_EXTENSION, SHARED_SUFFIX)
    epic_class = PythonEpic
    language = PYTHON
    writing_class = PythonStoryWriting

    def story_file(self, path: str, content: str, project: Optional[Path] = None) -> StoryFile:
        """The story file at path: a shared story file, read from its scenario and step functions, or a story test,
        read block by block."""
        kind = SharedStoryFile if is_shared_story_file(content) else PythonStoryFile
        return kind(self, path, content, project if project is not None else self.project)
