"""Sketch channel — indent story map from a Stories sketch.

Each line's indent is its depth: an epic at the left edge, nested epics four spaces in per level, a story as
``{actor} --> {story}`` under the epic that holds it, its scenarios one level in, and their steps as
``given`` / ``when`` / ``then`` lines with ``and`` / ``but`` lines indented beneath. A story that is not a user story
carries its kind in front: ``(S:system) {actor} --> {story}``.
"""

from __future__ import annotations

import re
from typing import List, Optional

from cdd_guidance.actions.sketch.sketch_outline import SketchLens, SketchOutline
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
_STORY = re.compile(r"^(?:\(S(?::(?P<kind>\w+))?\)\s+)?(?P<actor>.*?)\s*-->\s+(?P<name>.+)$")
_OUTLINE_EPIC = re.compile(r"^\(E\)\s+(.+)$")
_ESTIMATE = re.compile(r"^\*\s+(\S.+)$")
_INCREMENT = re.compile(r"^~>\s*(.+)$")
_STEP = re.compile(r"^(given|when|then|and|but)\s+(.+)$", re.I)
_STEP_TYPES = {"given": StepType.GIVEN, "when": StepType.WHEN, "then": StepType.THEN}


class SketchStoryModel(StoryModel):
    def parse(self, text: str) -> "SketchStoryModel":
        model = type(self)()
        body = SketchOutline(text, _NESTING_INDENT).body_for(SketchLens.of("stories"))
        _SketchReader(model).read(body)
        return model

    def render(self, story_map: StoryModel | None = None, previous: str | None = None) -> str:
        """Write *story_map* (this map when none is given) as a sketch. A sketch keeps no previous text."""
        return _SketchWriter().write(story_map or self)


class _SketchReader:
    """Reads sketch lines into a story map, keeping the epic, story, scenario, and step each next line belongs under."""

    def __init__(self, model: StoryModel) -> None:
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
            self.epic = Epic(name, len(self.model.epics) + 1)
            self.model.append_epic(self.epic)
            self.nested = []
            return
        parent = self._holder(level)
        if parent is None:
            return
        child = Epic(name, len(parent.epics) + 1)
        parent.append_epic(child)
        self.nested.append(child)

    def _add_story(self, match: "re.Match", level: int) -> None:
        if self.epic is None:
            self.epic = Epic("Stories", 1)
            self.model.append_epic(self.epic)
        parent = self._holder(level)
        story = Story(match.group("name").strip(), len(parent.stories) + 1, StoryType.from_mark(match.group("kind")))
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
        self.scenario = Scenario(name, len(self.story.scenarios) + 1, self.story.name)
        self.story.scenarios.append(self.scenario)
        self.last_step = None

    def _add_step(self, keyword: str, text: str) -> None:
        if keyword in {"and", "but"} and self.last_step is not None:
            extra = Step(text, self.last_step.step_type, len(self.last_step.ands) + 1, keyword=keyword)
            self.last_step.ands = [*self.last_step.ands, extra]
            return
        step = Step(text, _STEP_TYPES.get(keyword, StepType.THEN), 1, keyword=keyword)
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
            self.story.backgrounds.append(Background("background", 1))
        background = self.story.backgrounds[-1]
        step.sequential_order = len(background.steps) + 1
        background.steps = [*background.steps, step]


class _SketchWriter:
    """Writes a story map as sketch lines: each epic, then its stories, then its nested epics, one level deeper each."""

    def __init__(self) -> None:
        self.lines: List[str] = []

    def write(self, story_map: StoryModel) -> str:
        for epic in story_map.epics:
            self._epic(epic, 0)
        for increment in story_map.increments:
            self.lines.append(f"~> {increment.name}")
        return "\n".join(self.lines) + ("\n" if self.lines else "")

    def _epic(self, epic: Epic, depth: int) -> None:
        pad = "    " * depth
        self.lines.append(f"{pad}{epic.name}")
        if epic.estimate:
            self.lines.append(f"{pad}    * {epic.estimate}")
        for story in epic.stories:
            self._story(story, depth + 1)
        for child in epic.epics:
            self._epic(child, depth + 1)

    def _story(self, story: Story, depth: int) -> None:
        pad = "    " * depth
        actor = story.actors[0] if story.actors else ""
        mark = "" if story.story_type is StoryType.USER else f"{story.story_type.outline_mark} "
        self.lines.append(f"{pad}{mark}{actor} --> {story.name}" if actor else f"{pad}{mark}--> {story.name}")
        body = "    " * (depth + 1)
        for background in story.backgrounds:
            self._steps(background.steps, body, lowered=False)
        for scenario in story.scenarios:
            self.lines.append(f"{body}{scenario.name}")
            self._steps(scenario.steps, body + "    ", lowered=True)

    def _steps(self, steps: List[Step], pad: str, lowered: bool) -> None:
        for step in steps:
            keyword = step.keyword.lower() if lowered else "given"
            self.lines.append(f"{pad}{keyword} {step.text}")
            for extra in step.ands:
                self.lines.append(f"{pad}    {extra.keyword.lower()} {extra.text}")
