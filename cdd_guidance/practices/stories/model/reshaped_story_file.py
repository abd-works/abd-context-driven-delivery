"""ReshapedStoryFile. The scenarios a render brings, written onto the story file that is already there, losing nothing.

A story file holds what its scenarios do not: the body of each step, imports, helpers, comments, and whatever a
person wrote between scenarios. So a render never replaces it. The file is edited where it stands, matching story to
story, scenario to scenario, and step to step by their words:

- A step, scenario or story both hold stays exactly as the file has it.
- A step the scenarios gained is written into its scenario, empty, after the step it follows in the scenarios; a
  scenario they gained after the scenarios its story had; a story they gained at the end of the file.
- A step, scenario or story the scenarios lost stays where it is, with its code, under a line that says it is no
  longer in the model. A renamed step is one kept and one added: a person or an agent moves the kept body into the
  added step and then deletes the kept one.

Every line of the file stays where it was, and only lines are added, so the same scenarios written onto the result
change nothing. A file whose stories this language does not find as blocks, such as a step library, an examples
module, a Python shared story file or a screen spec, is left as it is.
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, List, Optional, Sequence

from harness.guidance.practice_formats import KeptMark, Reshaped

from cdd_guidance.practices.stories.model.story_file import StoryBlock, flat_steps
from cdd_guidance.practices.stories.model.story_writing import StepClause

if TYPE_CHECKING:
    from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModel
    from cdd_guidance.practices.stories.model.story_model import Scenario, Step, Story


class ReshapedStoryFile:
    """One story file's text edited into the shape a render brings: the lines to add, each before the line of the
    file it is written above, and the members kept and added, named as story, scenario and step
    (``Pack Order.Pack a paid order.the Shop Clerk packs the Order``)."""

    def __init__(self, model: "CodeStoryModel", rendered: str, existing: str) -> None:
        self._model = model
        self._writing = model.writing
        self._language = model.language
        self._existing = existing
        self._lines = existing.split("\n")
        self._rendered_stories: List["Story"] = model.story_file("", rendered).stories
        # Lines to write above a line of the file, by that line's index: the new members, and under them the line
        # that marks the member on that line, so a marking line stays directly above what it marks.
        self._above: dict[int, List[str]] = {}
        self._markings: dict[int, List[str]] = {}
        self._kept: List[str] = []
        self._added: List[str] = []

    def reshaped(self) -> Reshaped:
        """The file's text with the render's new members written in and its lost members marked."""
        blocks = self._story_blocks()
        if not blocks:
            return Reshaped(self._existing, [], [])
        by_name = {block.name: block for block in blocks}
        rendered = {story.name: story for story in self._rendered_stories}
        for block in blocks:
            if block.name in rendered:
                self._reshape_story(block, rendered[block.name])
            else:
                self._mark(block, f"story {block.name}", block.name)
        for story in self._rendered_stories:
            if story.name not in by_name:
                self._added.append(story.name)
                self._write_above(len(self._lines), ["", *self._writing.story_lines(story)])
        return Reshaped(self._text(), self._kept, self._added)

    def _story_blocks(self) -> List[StoryBlock]:
        """The story blocks the language finds in the file; none for a file it reads no block of."""
        return self._model.story_file("", self._existing).story_blocks() or []

    def _reshape_story(self, block: StoryBlock, story: "Story") -> None:
        scenarios = block.scenarios()
        by_name = {scenario.name: scenario for scenario in scenarios}
        rendered = {scenario.name: scenario for scenario in story.scenarios}
        for scenario in scenarios:
            name = f"{story.name}.{scenario.name}"
            if scenario.name in rendered:
                self._reshape_scenario(scenario, rendered[scenario.name], name)
            else:
                self._mark(scenario, f"scenario {scenario.name} of story {story.name}", name)
        indent = self._indent_of(scenarios[0]) if scenarios else self._writing.scenario_indent
        for scenario in story.scenarios:
            if scenario.name not in by_name:
                self._added.append(f"{story.name}.{scenario.name}")
                self._write_above(self._end_of(block), [*self._writing.scenario_gap, *self._writing._scenario_lines(scenario, indent)])

    def _reshape_scenario(self, block: StoryBlock, scenario: "Scenario", name: str) -> None:
        steps = sorted(block.steps(block.backgrounds([])), key=lambda step: step.line_span)
        rendered = flat_steps(scenario.steps)
        wanted = Counter(step.text for step in rendered)
        held = Counter(step.name for step in steps)
        for step in steps:
            if wanted[step.name] > 0:
                wanted[step.name] -= 1
            else:
                self._mark(step, f"step {step.name} of scenario {scenario.name}", f"{name}.{step.name}")
        indent = next((self._indent_of(step) for step in steps if not step.is_chained), self._indent_of(block) + self._language.indent)
        for place, step in enumerate(rendered):
            if held[step.text] > 0:
                held[step.text] -= 1
                continue
            self._added.append(f"{name}.{step.text}")
            self._write_above(self._line_after(steps, rendered[:place], block), self._empty_step(step, indent))

    def _line_after(self, steps: Sequence[StoryBlock], before: Sequence["Step"], scenario: StoryBlock) -> int:
        """The line a new step is written above: the one after the statement of the nearest step before it that the
        file holds, else the end of the scenario. A step chained onto another ends with the last step of its chain."""
        texts = {step.text for step in before}
        last = max((index for index, step in enumerate(steps) if step.name in texts), default=None)
        if last is None:
            return self._end_of(scenario)
        while last + 1 < len(steps) and steps[last + 1].is_chained:
            last += 1
        return steps[last].line_span[1] + 1

    def _empty_step(self, step: "Step", indent: str) -> List[str]:
        """The step written by itself with no body yet: under its own verb where the language has one for it, else
        under the verb of its phase, so a step the scenarios chain with And stands as a statement of its own."""
        alone = type(step)(step.text, step.step_type, step.sequential_order)
        alone.keyword = step.keyword
        return self._writing._step_lines(StepClause(alone, self._writing.verb_alone(alone)), indent)

    def _mark(self, block: StoryBlock, member: str, name: str) -> None:
        """Say above block that its member is no longer in the model, once: a member an earlier render marked keeps
        its line."""
        self._kept.append(name)
        line = block.opening_line
        if line > 0 and KeptMark.marks(self._lines[line - 1]):
            return
        indent = self._indent_of(block)
        marking = KeptMark.line_for(member, "Move its code into the member that replaced it, then delete it.")
        self._markings.setdefault(line, []).append(f"{indent}{self._language.comment(marking)}")

    def _indent_of(self, block: StoryBlock) -> str:
        line = self._lines[block.opening_line]
        return line[: len(line) - len(line.lstrip())]

    def _end_of(self, block: StoryBlock) -> int:
        """The line new members of block are written above: its closing line when the language closes a block with
        one, else the line after its last."""
        last = block.line_span[1]
        return last if self._writing.story_closing else last + 1

    def _write_above(self, line: int, lines: Optional[List[str]]) -> None:
        self._above.setdefault(line, []).extend(lines or [])

    def _text(self) -> str:
        """The file's lines with each write above its line. A write at the end of a file that ends with a newline goes
        above the empty last line the split leaves, so the file still ends with one."""
        end = len(self._lines) - 1 if self._lines and not self._lines[-1] else len(self._lines)
        above: dict[int, List[str]] = {}
        for written_above in (self._above, self._markings):
            for line, written in sorted(written_above.items()):
                above.setdefault(min(line, end), []).extend(written)
        lines: List[str] = []
        for index in range(len(self._lines) + 1):
            lines.extend(above.get(index, []))
            lines.extend(self._lines[index : index + 1])
        return "\n".join(lines)
