"""Sketch channel — indent story map from a Stories sketch.

Each line's indent is its depth: an epic at the left edge, nested epics four spaces in per level, a story as
``{actor} --> {story}`` under the epic that holds it, its scenarios one level in, and their steps as
``given`` / ``when`` / ``then`` lines with ``and`` / ``but`` lines indented beneath. A story that is not a user story
carries its kind in front: ``(S:system) {actor} --> {story}``.
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

from cdd_guidance.practices.sketch_document.sketch_outline import SketchOutline
from harness.guidance.guidance import SketchLens
from cdd_guidance.practices.stories.model.story_model import (
    Background,
    Epic,
    Increment,
    Scenario,
    Step,
    StepType,
    Story,
    StoryModel,
    StoryType,
)

_NESTING_INDENT = 4
# The headings that open the stories section of a sketch; the Stories practice declares them from here.
_LENS = SketchLens(("stories:",))
_STORY = re.compile(r"^(?:\(S(?::(?P<kind>\w+))?\)\s+)?(?P<actor>.*?)\s*-->\s+(?P<name>.+)$")
_OUTLINE_EPIC = re.compile(r"^\(E\)\s+(.+)$")
_ESTIMATE = re.compile(r"^\*\s+(\S.+)$")
_INCREMENT = re.compile(r"^~>\s*(.+)$")
_STEP = re.compile(r"^(given|when|then|and|but)\s+(.+)$", re.I)
_STEP_TYPES = {"given": StepType.GIVEN, "when": StepType.WHEN, "then": StepType.THEN}
_CHAINED = ("and", "but")


def _epic_name(text: str) -> str:
    """A line's name without the `(E)` an outline marks an epic with."""
    headed = _OUTLINE_EPIC.match(text)
    return headed.group(1) if headed else text


def read_sketch_lines(raws: List[str]) -> "SketchLines":
    """The lines raws write, each at the depth its indent gives: four spaces a level, or two when the indent is not a
    multiple of four."""
    return SketchLines([(raw.strip(), _depth(raw)) for raw in raws])


def _depth(raw: str) -> int:
    indent = len(raw) - len(raw.lstrip(" "))
    return indent // _NESTING_INDENT if indent % _NESTING_INDENT == 0 else indent // 2


class SketchLines:
    """Lines of a sketch's stories section that one node holds, each with how deep its indent puts it. An entry of
    these lines is itself a SketchLines: the line that names a node, then the lines nested under it."""

    def __init__(self, lines: List[Tuple[str, int]]) -> None:
        self._lines = lines

    @property
    def text(self) -> str:
        """The first line's text: the line that names the node these lines are an entry for."""
        return self._lines[0][0]

    @property
    def texts(self) -> List[str]:
        return [text for text, _depth in self._lines]

    @property
    def nested(self) -> "SketchLines":
        """The lines after the first: those nested under the line that names the node."""
        return SketchLines(self._lines[1:])

    def under(self) -> List["SketchLines"]:
        """Each entry these lines hold: a line at the shallowest depth among them opens one, and the deeper lines after
        it are its own."""
        if not self._lines:
            return []
        shallowest = min(depth for _text, depth in self._lines)
        entries: List[List[Tuple[str, int]]] = []
        for line in self._lines:
            if line[1] <= shallowest or not entries:
                entries.append([line])
            else:
                entries[-1].append(line)
        return [SketchLines(entry) for entry in entries]


class SketchStep(Step):
    """A step in the sketch: `{keyword} {text}` at pad, then each step chained onto it one level in."""

    @classmethod
    def from_line(cls, keyword: str, text: str, order: int) -> "SketchStep":
        return cls(text, _STEP_TYPES.get(keyword, StepType.THEN), order, keyword=keyword)

    def sketch_lines(self, pad: str, keyword: str) -> List[str]:
        return [f"{pad}{keyword} {self.text}"] + [f"{pad}    {extra.keyword.lower()} {extra.text}" for extra in self.ands]

    def read_lines(self, lines: SketchLines) -> None:
        """The `and` and `but` lines under this step, each chained onto it."""
        for text in lines.texts:
            self.chain(text)

    def chain(self, text: str) -> bool:
        """Chain an `and` or `but` line onto this step; false for any other line."""
        step = _STEP.match(text)
        if step is None or step.group(1).lower() not in _CHAINED:
            return False
        keyword = step.group(1).lower()
        self.ands = [*self.ands, SketchStep(step.group(2), self.step_type, len(self.ands) + 1, keyword=keyword)]
        return True


def _read_steps(lines: SketchLines, take) -> None:
    """Each step the lines write, with the `and` and `but` lines chained onto the step before them, handed to take."""
    last: Optional[SketchStep] = None
    for entry in lines.under():
        step = _STEP.match(entry.text)
        if step is None:
            continue
        if last is not None and last.chain(entry.text):
            continue
        last = SketchStep.from_line(step.group(1).lower(), step.group(2), 1)
        last.read_lines(entry.nested)
        take(last)


class SketchBackground(Background):
    """A story's background in the sketch: each of its steps as a `given` line."""

    step_type = SketchStep

    def sketch_lines(self, pad: str) -> List[str]:
        return [line for step in self.steps for line in step.sketch_lines(pad, "given")]


class SketchScenario(Scenario):
    """A scenario in the sketch: its name, then its steps one level in, each under its own keyword."""

    step_type = SketchStep
    background_type = SketchBackground

    def read_lines(self, lines: SketchLines) -> None:
        """Its steps: the lines under its name."""
        _read_steps(lines, self.take_step)

    def take_step(self, step: SketchStep) -> None:
        step.sequential_order = len(self.steps) + 1
        self.steps.append(step)

    def sketch_lines(self, pad: str) -> List[str]:
        steps = [line for step in self.steps for line in step.sketch_lines(pad + "    ", step.keyword.lower())]
        return [f"{pad}{self.name}"] + steps


class SketchStory(Story):
    """A story in the sketch: `{actor} --> {story}`, its background steps, then each scenario with its steps."""

    scenario_type = SketchScenario
    background_type = SketchBackground

    @classmethod
    def from_match(cls, match: "re.Match", order: int) -> "SketchStory":
        """The story a `{actor} --> {story}` line names, a system story's kind in front."""
        story = cls(match.group("name").strip(), order, StoryType.from_mark(match.group("kind")))
        actor = match.group("actor").strip()
        if actor:
            story.actors = [actor]
        return story

    def read_lines(self, lines: SketchLines) -> None:
        """The lines under the story: its background's `given` lines before any scenario, then each scenario named
        with its steps under it. A step with no scenario to hold it opens one named for the story."""
        for entry in lines.under():
            if _STEP.match(entry.text):
                _read_steps(entry, self._take_step)
                continue
            scenario = SketchScenario(entry.text, len(self.scenarios) + 1)
            self.scenarios.append(scenario)
            scenario.read_lines(entry.nested)

    def _take_step(self, step: SketchStep) -> None:
        if step.keyword.lower() == "given" and not self.scenarios:
            if not self.backgrounds:
                self.backgrounds.append(SketchBackground("background", 1))
            background = self.backgrounds[-1]
            step.sequential_order = len(background.steps) + 1
            background.steps = [*background.steps, step]
            return
        if not self.scenarios:
            self.scenarios.append(SketchScenario(self.name, 1))
        self.scenarios[-1].take_step(step)

    def sketch_lines(self, depth: int) -> List[str]:
        pad = "    " * depth
        actor = self.actors[0] if self.actors else ""
        mark = "" if self.story_type is StoryType.USER else f"{self.story_type.outline_mark} "
        lines = [f"{pad}{mark}{actor} --> {self.name}" if actor else f"{pad}{mark}--> {self.name}"]
        body = "    " * (depth + 1)
        for background in self.backgrounds:
            lines.extend(background.sketch_lines(body))
        for scenario in self.scenarios:
            lines.extend(scenario.sketch_lines(body))
        return lines


class SketchEpic(Epic):
    """An epic in the sketch: its name, its estimate, its stories, then its nested epics, one level deeper each."""

    def read_lines(self, lines: SketchLines) -> None:
        """The lines under the epic: its estimate, each story with its scenarios, and each nested epic with its own."""
        for entry in lines.under():
            estimate = _ESTIMATE.match(entry.text)
            if estimate:
                self.estimate = estimate.group(1)
                continue
            story = _STORY.match(_epic_name(entry.text))
            if story:
                read = SketchStory.from_match(story, len(self.stories) + 1)
                self.append_story(read)
                read.read_lines(entry.nested)
                continue
            child = SketchEpic(_epic_name(entry.text), len(self.epics) + 1)
            self.append_epic(child)
            child.read_lines(entry.nested)

    def sketch_lines(self, depth: int) -> List[str]:
        pad = "    " * depth
        lines = [f"{pad}{self.name}"]
        if self.estimate:
            lines.append(f"{pad}    * {self.estimate}")
        for story in self.stories:
            lines.extend(story.sketch_lines(depth + 1))
        for child in self.epics:
            lines.extend(child.sketch_lines(depth + 1))
        return lines


class SketchStoryModel(StoryModel):
    epic_type = SketchEpic
    story_type = SketchStory
    lens = _LENS
    """The section of a sketch Stories writes, opened by its `stories:` heading."""

    def parse(self, text: str) -> "SketchStoryModel":
        """Read the sketch's stories section into this map, and return it."""
        self.epics = []
        self.increments.refill([])
        body = SketchOutline(text, _NESTING_INDENT).body_for(self.lens)
        self.read_lines(self._story_lines(body))
        return self

    def read_lines(self, lines: SketchLines) -> None:
        """Each epic at the left edge with the lines under it; a story with no epic above it sits in a `Stories` epic."""
        for entry in lines.under():
            story = _STORY.match(_epic_name(entry.text))
            if story is None:
                epic = SketchEpic(_epic_name(entry.text), len(self.epics) + 1)
                self.append_epic(epic)
                epic.read_lines(entry.nested)
                continue
            if not self.epics:
                self.append_epic(SketchEpic("Stories", 1))
            read = SketchStory.from_match(story, len(self.epics[-1].stories) + 1)
            self.epics[-1].append_story(read)
            read.read_lines(entry.nested)

    def _story_lines(self, body: str) -> SketchLines:
        """The lines of the body that write the map; the increments it lists after `~>` are taken here, with the prose
        under them up to the next blank line."""
        lines: List[str] = []
        in_increments = False
        for raw in body.splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith(("//", "#", "Fidelity:")):
                in_increments = in_increments and bool(stripped)
                continue
            increment = _INCREMENT.match(stripped)
            if increment is not None:
                in_increments = True
                self.append_increment(Increment(increment.group(1), len(self.increments) + 1))
            elif not in_increments:
                lines.append(raw)
        return read_sketch_lines(lines)

    def render(self, canonical: StoryModel | None = None, previous: str | None = None) -> str:
        """Write canonical (this map when none is given) as a sketch: copied into a sketch map, which writes itself.
        A sketch keeps no previous text."""
        source = canonical or self
        return (source if isinstance(source, SketchStoryModel) else self.copy_of(source)).save()

    def save(self) -> str:
        lines = [line for epic in self.epics for line in epic.sketch_lines(0)]
        lines.extend(f"~> {increment.name}" for increment in self.increments)
        return "\n".join(lines) + ("\n" if lines else "")
