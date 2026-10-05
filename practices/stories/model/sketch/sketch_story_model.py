"""Sketch channel — indent story map from a Stories sketch."""

from __future__ import annotations

import re

from harness.sketch.sketch_outline import SketchLens, SketchOutline
from practices.stories.model.story_model import (
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
_STORY = re.compile(r"^(?:\(S\)\s+)?(.+?)\s*-->\s+(.+)$")
_OUTLINE_EPIC = re.compile(r"^\(E\)\s+(.+)$")
_ESTIMATE = re.compile(r"^\*\s+(\S.+)$")
_INCREMENT = re.compile(r"^~>\s*(.+)$")
_STEP = re.compile(r"^(given|when|then|and|but)\s+(.+)$", re.I)


class SketchStoryModel(StoryModel):
    def parse(self, text: str) -> "SketchStoryModel":
        model = type(self)()
        body = SketchOutline(text, _NESTING_INDENT).body_for(SketchLens.stories)
        epic: Epic | None = None
        subs: list[Epic] = []
        story: Story | None = None
        scenario: Scenario | None = None
        last_step: Step | None = None
        for raw in body.splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith(("//", "#", "Fidelity:")):
                continue
            increment = _INCREMENT.match(stripped)
            if increment:
                model.append_increment(
                    Increment(increment.group(1), len(model.increments) + 1)
                )
                continue
            estimate = _ESTIMATE.match(stripped)
            if estimate:
                target = subs[-1] if subs else epic
                if target is not None:
                    target.estimate = estimate.group(1)
                continue
            step = _STEP.match(stripped)
            if step and story is not None:
                last_step = _add_step(story, scenario, last_step, step.group(1), step.group(2))
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            level = indent // 4 if indent % 4 == 0 else indent // 2
            headed = _OUTLINE_EPIC.match(stripped)
            name = headed.group(1) if headed else stripped
            story_line = _STORY.match(name)
            if story_line:
                parent = _parent_epic(model, epic, subs, level)
                story = Story(story_line.group(2).strip(), len(parent.stories) + 1, StoryType.USER)
                actor = story_line.group(1).strip()
                if actor:
                    story.actors = [actor]
                parent.append_story(story)
                scenario = None
                last_step = None
                continue
            if level <= 0:
                epic = Epic(name, len(model.epics) + 1)
                model.append_epic(epic)
                subs = []
                story = None
                scenario = None
                last_step = None
                continue
            if story is not None and level >= 3:
                scenario = Scenario(name, len(story.scenarios) + 1, story.name)
                story.scenarios.append(scenario)
                last_step = None
                continue
            parent = epic
            while len(subs) >= level:
                subs.pop()
            if subs:
                parent = subs[-1]
            if parent is None:
                continue
            child = Epic(name, len(parent.epics) + 1)
            parent.append_epic(child)
            subs.append(child)
            story = None
            scenario = None
            last_step = None
        return model

    def render(self, story_map: StoryModel | None = None, previous: str | None = None) -> str:
        del previous
        return _render_sketch(story_map or self)


def _parent_epic(model: StoryModel, epic: Epic | None, subs: list[Epic], level: int) -> Epic:
    if epic is None:
        epic = Epic("Stories", 1)
        model.append_epic(epic)
    while len(subs) >= max(level, 1):
        subs.pop()
    if subs:
        return subs[-1]
    if not epic.epics:
        child = Epic(epic.name, 1)
        epic.append_epic(child)
        subs.append(child)
        return child
    return epic.epics[-1]


def _add_step(
    story: Story,
    scenario: Scenario | None,
    last_step: Step | None,
    keyword: str,
    text: str,
) -> Step:
    kind = keyword.lower()
    if kind in {"and", "but"} and last_step is not None:
        extra = Step(text=text, step_type=last_step.step_type, sequential_order=len(last_step.ands) + 1, keyword=kind)
        last_step.ands = list(last_step.ands) + [extra]
        return last_step
    step_type = {"given": StepType.GIVEN, "when": StepType.WHEN, "then": StepType.THEN}[kind]
    step = Step(text=text, step_type=step_type, sequential_order=1, keyword=kind)
    if kind == "given" and scenario is None:
        if not story.backgrounds:
            story.backgrounds.append(Background("background", 1))
        story.backgrounds[-1].steps = list(story.backgrounds[-1].steps) + [step]
        return step
    if scenario is None:
        scenario = Scenario(story.name, len(story.scenarios) + 1, story.name)
        story.scenarios.append(scenario)
    step.sequential_order = len(scenario.steps) + 1
    scenario.steps.append(step)
    return step


def _render_sketch(story_map: StoryModel) -> str:
    lines: list[str] = []
    for epic in story_map.epics:
        lines.append(epic.name)
        if epic.estimate:
            lines.append(f"    * {epic.estimate}")
        _render_epic(epic, lines, 1)
    for increment in story_map.increments:
        lines.append(f"~> {increment.name}")
    return "\n".join(lines) + ("\n" if lines else "")


def _render_epic(epic: Epic, lines: list[str], depth: int) -> None:
    pad = "    " * depth
    for child in epic.epics:
        lines.append(f"{pad}{child.name}")
        if child.estimate:
            lines.append(f"{pad}    * {child.estimate}")
        for story in child.stories:
            actor = story.actors[0] if story.actors else ""
            arrow = f"{actor} --> {story.name}" if actor else f"--> {story.name}"
            lines.append(f"{pad}    {arrow}")
            _render_story_body(story, lines, depth + 2)
        _render_epic(child, lines, depth + 1)
    for story in epic.stories:
        actor = story.actors[0] if story.actors else ""
        arrow = f"{actor} --> {story.name}" if actor else f"--> {story.name}"
        lines.append(f"{pad}{arrow}")
        _render_story_body(story, lines, depth + 1)


def _render_story_body(story: Story, lines: list[str], depth: int) -> None:
    pad = "    " * depth
    for background in story.backgrounds:
        for step in background.steps:
            lines.append(f"{pad}given {step.text}")
            for extra in step.ands:
                lines.append(f"{pad}    and {extra.text}")
    for scenario in story.scenarios:
        lines.append(f"{pad}{scenario.name}")
        nested = "    " * (depth + 1)
        for step in scenario.steps:
            lines.append(f"{nested}{step.keyword.lower()} {step.text}")
            for extra in step.ands:
                lines.append(f"{nested}    and {extra.text}")
