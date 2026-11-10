"""Reads a Python story file's blocks as written: `with story`, `with background`, `with scenario`, and step blocks."""

from __future__ import annotations

import ast
import re
from typing import List, Optional, Tuple

from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody, CodeLanguage, WrittenBlock
from cdd_guidance.practices.stories.model.code_story_model import flat_steps
from cdd_guidance.practices.stories.model.story_reader import StoryReader
from cdd_guidance.practices.stories.model.story_model import Background, Scenario, Story

_STEP_CALLS = frozenset({"given", "when", "then", "and_", "but_"})
# Comments the scenario writes for itself; they are not code the scenario holds.
_OWN_COMMENT = re.compile(r"^\s*#\s*(?:background|background-step|examples):")


class PythonStoryReader(StoryReader[ast.With]):
    """Reads one story file and gives each story, background, scenario, and step the code it was written with."""

    def __init__(self, language: CodeLanguage, content: str) -> None:
        super().__init__(language, content)
        try:
            self._tree: Optional[ast.Module] = ast.parse(content)
        except SyntaxError:
            self._tree = None

    def story_blocks(self) -> Optional[List[ast.With]]:
        if self._tree is None:
            return None
        return [item for item in self._tree.body if self._call(item) == "story"]

    def name_of(self, block: ast.With) -> str:
        return self._name(block)

    def line_span(self, block: ast.With) -> Tuple[int, int]:
        return block.lineno - 1, block.end_lineno - 1

    def read_story(self, story: Story, block: ast.With, lead: List[str]) -> None:
        scenarios = self._within(block, "scenario")
        backgrounds = [item for item in self._within(block, "background") if not self._is_inside(item, scenarios)]
        for background, item in zip(story.backgrounds, backgrounds):
            self._read_steps(background, self._steps_in(item, scenarios))
        written = WrittenBlock(self._language, None, lead, self._heading(block))
        written.inside, leads, written.closing = WrittenBlock.split_inside(
            self._lines, self._inside(block), [self.line_span(item) for item in scenarios]
        )
        pending = list(story.scenarios)
        for item, scenario_lead in zip(scenarios, leads):
            scenario = self.take(pending, self._name(item))
            if scenario is not None:
                self._read_scenario(scenario, item, scenario_lead)
        written.key = story.code_key
        story.written = written

    def _read_scenario(self, scenario: Scenario, block: ast.With, lead: List[str]) -> None:
        steps = self._steps_in(block, [])
        self._read_steps(scenario, steps)
        scenario.setup = self._setup(block, steps)
        written = WrittenBlock(self._language, None, lead, self._heading(block))
        written.inside = self._lines[slice(*self._inside(block))]
        written.key = scenario.code_key
        scenario.written = written

    def _read_steps(self, owner: "Scenario | Background", blocks: List[ast.With]) -> None:
        """Each step block's body onto the owner's steps, in file order. A step whose text differs keeps no body."""
        for step, block in zip(flat_steps(owner.steps), blocks):
            if step.text == self._name(block):
                step.body = CodeBody("\n".join(self._lines[slice(*self._inside(block))]), self._language)

    def _steps_in(self, block: ast.With, skip: List[ast.With]) -> List[ast.With]:
        return [
            item
            for item in ast.walk(block)
            if self._call(item) in _STEP_CALLS and not self._is_inside(item, skip)
        ]

    def _within(self, block: ast.With, call: str) -> List[ast.With]:
        """The blocks of one kind inside block, outermost first and in file order."""
        found = [item for item in ast.walk(block) if item is not block and self._call(item) == call]
        found.sort(key=lambda item: item.lineno)
        return [item for item in found if not self._is_inside(item, [other for other in found if other is not item])]

    def _setup(self, block: ast.With, steps: List[ast.With]) -> CodeBody:
        """The lines in a scenario that are no step and none of the comments the scenario writes for itself."""
        first, last = self._inside(block)
        covered = {line for item in steps for line in range(item.lineno - 1, item.end_lineno)}
        kept = [self._lines[index] for index in range(first, last) if index not in covered and not _OWN_COMMENT.match(self._lines[index])]
        return CodeBody("\n".join(kept), self._language)

    def _call(self, item: ast.AST) -> str:
        """The block's call: story, scenario, given, ... ; background for `with background.<scope>`."""
        if not isinstance(item, ast.With) or not item.items:
            return ""
        expression = item.items[0].context_expr
        if isinstance(expression, ast.Attribute) and isinstance(expression.value, ast.Name):
            return "background" if expression.value.id == "background" else ""
        if isinstance(expression, ast.Call) and isinstance(expression.func, ast.Name):
            return expression.func.id
        return ""

    def _name(self, block: ast.With) -> str:
        expression = block.items[0].context_expr
        if isinstance(expression, ast.Call) and expression.args and isinstance(expression.args[0], ast.Constant):
            return str(expression.args[0].value)
        return ""

    def _heading(self, block: ast.With) -> List[str]:
        return self._lines[block.lineno - 1 : self._inside(block)[0]]

    def _inside(self, block: ast.With) -> Tuple[int, int]:
        """The lines below the `with ...:` opening; comments and blank lines below it belong inside."""
        index = block.body[0].lineno - 2
        while index > block.lineno - 1 and (not self._lines[index].strip() or self._lines[index].strip().startswith("#")):
            index -= 1
        return index + 1, block.end_lineno

    def _is_inside(self, item: ast.AST, blocks: List[ast.With]) -> bool:
        return any(block.lineno < item.lineno <= block.end_lineno for block in blocks)
