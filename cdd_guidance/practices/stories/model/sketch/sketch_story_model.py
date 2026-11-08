"""Sketch channel — indent story map from a Stories sketch.

Each line's indent is its depth: an epic at the left edge, nested epics four spaces in per level, a story as
``{actor} --> {story}`` under the epic that holds it, its scenarios one level in, and their steps as
``given`` / ``when`` / ``then`` lines with ``and`` / ``but`` lines indented beneath. A story that is not a user story
carries its kind in front: ``(S:system) {actor} --> {story}``.
"""

from __future__ import annotations

import re
from typing import List, Optional

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


class SketchStep(Step):
    """A step in the sketch: `{keyword} {text}` at pad, then each step chained onto it one level in."""

    def sketch_lines(self, pad: str, keyword: str) -> List[str]:
        return [f"{pad}{keyword} {self.text}"] + [f"{pad}    {extra.keyword.lower()} {extra.text}" for extra in self.ands]


class SketchBackground(Background):
    """A story's background in the sketch: each of its steps as a `given` line."""

    step_type = SketchStep

    def sketch_lines(self, pad: str) -> List[str]:
        return [line for step in self.steps for line in step.sketch_lines(pad, "given")]


class SketchScenario(Scenario):
    """A scenario in the sketch: its name, then its steps one level in, each under its own keyword."""

    step_type = SketchStep
    background_type = SketchBackground

    def sketch_lines(self, pad: str) -> List[str]:
        steps = [line for step in self.steps for line in step.sketch_lines(pad + "    ", step.keyword.lower())]
        return [f"{pad}{self.name}"] + steps


class SketchStory(Story):
    """A story in the sketch: `{actor} --> {story}`, its background steps, then each scenario with its steps."""

    scenario_type = SketchScenario
    background_type = SketchBackground

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
        self.increments = []
        body = SketchOutline(text, _NESTING_INDENT).body_for(self.lens)
        _SketchReader(self).read(body)
        return self

    def render(self, canonical: StoryModel | None = None, previous: str | None = None) -> str:
        """Write canonical (this map when none is given) as a sketch: copied into a sketch map, which writes itself.
        A sketch keeps no previous text."""
        source = canonical or self
        return (source if isinstance(source, SketchStoryModel) else self.copy_of(source)).save()

    def save(self) -> str:
        lines = [line for epic in self.epics for line in epic.sketch_lines(0)]
        lines.extend(f"~> {increment.name}" for increment in self.increments)
        return "\n".join(lines) + ("\n" if lines else "")


class _SketchReader:
    """Reads sketch lines into the sketch map that parses them, keeping the epic, story, scenario, and step each next
    line belongs under. One reader serves one parse."""

    def __init__(self, model: "SketchStoryModel") -> None:
        self.model = model
        self.epic: Optional[Epic] = None
        self.nested: List[Epic] = []
        self.story: Optional[Story] = None
        self.story_level = 0
        self.scenario: Optional[Scenario] = None
        self.last_step: Optional[Step] = None
        self.in_increments = False

    def read(self, body: str) -> None:
        for raw in body.splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith(("//", "#", "Fidelity:")):
                self.in_increments = self.in_increments and bool(stripped)
                continue
            if self._read_increment(stripped) or self.in_increments:
                continue
            self._read_line(stripped, self._level_of(raw))

    def _read_line(self, stripped: str, level: int) -> None:
        estimate = _ESTIMATE.match(stripped)
        if estimate:
            self._estimate(estimate.group(1))
            return
        step = _STEP.match(stripped)
        if step and self.story is not None:
            self._add_step(step.group(1).lower(), step.group(2))
            return
        headed = _OUTLINE_EPIC.match(stripped)
        name = headed.group(1) if headed else stripped
        story = _STORY.match(name)
        if story:
            self._add_story(story, level)
        elif self.story is not None and level > self.story_level:
            self._add_scenario(name)
        else:
            self._add_epic(name, level)

    def _level_of(self, raw: str) -> int:
        indent = len(raw) - len(raw.lstrip(" "))
        return indent // _NESTING_INDENT if indent % _NESTING_INDENT == 0 else indent // 2

    def _read_increment(self, stripped: str) -> bool:
        increment = _INCREMENT.match(stripped)
        if increment is None:
            return False
        self.in_increments = True
        self.model.append_increment(Increment(increment.group(1), len(self.model.increments) + 1))
        return True

    def _estimate(self, estimate: str) -> None:
        target = self.nested[-1] if self.nested else self.epic
        if target is not None:
            target.estimate = estimate

    def _add_epic(self, name: str, level: int) -> None:
        self.story, self.scenario, self.last_step = None, None, None
        if level <= 0:
            self.epic = SketchEpic(name, len(self.model.epics) + 1)
            self.model.append_epic(self.epic)
            self.nested = []
            return
        parent = self._holder(level)
        if parent is None:
            return
        child = SketchEpic(name, len(parent.epics) + 1)
        parent.append_epic(child)
        self.nested.append(child)

    def _add_story(self, match: "re.Match", level: int) -> None:
        if self.epic is None:
            self.epic = SketchEpic("Stories", 1)
            self.model.append_epic(self.epic)
        parent = self._holder(level)
        story = SketchStory(match.group("name").strip(), len(parent.stories) + 1, StoryType.from_mark(match.group("kind")))
        actor = match.group("actor").strip()
        if actor:
            story.actors = [actor]
        parent.append_story(story)
        self.story, self.story_level = story, level
        self.scenario, self.last_step = None, None

    def _holder(self, level: int) -> Optional[Epic]:
        """The epic a line at *level* sits under: the nested epic one level up, else the top-level epic."""
        while len(self.nested) >= level:
            self.nested.pop()
        return self.nested[-1] if self.nested else self.epic

    def _add_scenario(self, name: str) -> None:
        self.scenario = SketchScenario(name, len(self.story.scenarios) + 1, self.story.name)
        self.story.scenarios.append(self.scenario)
        self.last_step = None

    def _add_step(self, keyword: str, text: str) -> None:
        if keyword in {"and", "but"} and self.last_step is not None:
            extra = SketchStep(text, self.last_step.step_type, len(self.last_step.ands) + 1, keyword=keyword)
            self.last_step.ands = [*self.last_step.ands, extra]
            return
        step = SketchStep(text, _STEP_TYPES.get(keyword, StepType.THEN), 1, keyword=keyword)
        self.last_step = step
        if keyword == "given" and self.scenario is None:
            self._add_background_step(step)
            return
        if self.scenario is None:
            self._add_scenario(self.story.name)
            self.last_step = step
        step.sequential_order = len(self.scenario.steps) + 1
        self.scenario.steps.append(step)

    def _add_background_step(self, step: Step) -> None:
        if not self.story.backgrounds:
            self.story.backgrounds.append(SketchBackground("background", 1))
        background = self.story.backgrounds[-1]
        step.sequential_order = len(background.steps) + 1
        background.steps = [*background.steps, step]
