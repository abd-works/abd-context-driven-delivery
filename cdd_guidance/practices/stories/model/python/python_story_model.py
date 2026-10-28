"""PythonStoryModel - runnable `*_story.test.py` per Story.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from cdd_guidance.practices.clean_engineering.model.code_body import CodeLanguage, WrittenBlock
from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModel, CodeStoryModelError, example_names_of, flat_steps
from cdd_guidance.practices.stories.model.python.nodes import PythonEpic, PythonStory, quote
from cdd_guidance.practices.stories.model.python.story_reader import PythonStoryReader
from cdd_guidance.practices.stories.model.story_model import Background, Epic, Scenario, Step, Story

_VERBS = {"Given": "given", "When": "when", "Then": "then", "But": "but_", "And": "and_"}


class PythonStoryModel(CodeStoryModel):
    LEAF_EXTENSION = "_story.test.py"
    LANGUAGE_LINE_COMMENT = "#"
    epic_type = PythonEpic
    story_type = PythonStory
    language = CodeLanguage.named("python")
    scenario_indent = "        "
    scenario_gap: List[str] = []

    def save(self) -> Dict[str, str]:
        return self.write_epics({})

    def leaf_files_of(self, tree: Dict[str, str]) -> List[str]:
        return sorted(p for p in tree if p.endswith(self.LEAF_EXTENSION))

    def _epic_helper_path(self, epic_root: str, epic: Epic) -> str:
        return f"{epic_root}/{epic.snake()}_helper.py"

    def load(self, external: Dict[str, str]) -> "PythonStoryModel":
        if not isinstance(external, dict):
            raise CodeStoryModelError("Python story map parse expects a path->content dict")
        self.epics.clear()
        for path in self._ordered_paths(external):
            content = external[path]
            if not path.endswith(self.LEAF_EXTENSION):
                continue
            parts = path.strip("/").split("/")
            if parts and parts[0] == self.tests_root:
                parts = parts[1:]
            if self.take_sub_epic_file(parts, content, path):
                continue
            if len(parts) < 4:
                continue
            epic_slug = parts[0]
            story_slug = parts[-2]
            sub_slugs = parts[1:-2]
            if not sub_slugs:
                continue
            epic = self.epic_for(epic_slug)
            sub = self.sub_epic_for(epic, sub_slugs)
            sub.append_story(self.story_type.load(content, story_slug))
        return self

    def read_code(self, content: str, stories: List[Story], path: str) -> Optional[WrittenBlock]:
        return PythonStoryReader(self.language, content).read(stories, path)

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
        lines: List[str] = [f"# Story: {story.name}"]
        actor = (story.actors[0] if story.actors else "").strip()
        if actor:
            lines.append(f"# Actor: {actor}")
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
