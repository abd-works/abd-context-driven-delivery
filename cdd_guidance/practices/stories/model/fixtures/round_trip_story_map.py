"""A story map that uses every part a format adapter has to carry, and the outline its round trip is compared by.

The map has a Story held directly by its top-level epic, a nested epic, user, system, and technical stories, a
story background with steps, and a scenario with Given, When, and Then steps and an And under the Given.
"""

from __future__ import annotations

from typing import Any, List

from cdd_guidance.practices.stories.model.story_model import (
    Background,
    Epic,
    Scenario,
    Step,
    StepType,
    Story,
    StoryModel,
    StoryType,
)


def round_trip_story_map(story_map: StoryModel | None = None) -> StoryModel:
    """The fixture map, built into *story_map* (a format's own model) or a plain StoryModel."""
    story_map = story_map if story_map is not None else StoryModel()
    pay = Epic("Pay Bills", 1)
    story_map.append_epic(pay)
    pay.append_story(_story("Review Statement", StoryType.USER, "Customer"))
    enter = Epic("Enter Payment", 1)
    pay.append_epic(enter)
    submit = _story("Submit Payment", StoryType.USER, "Customer")
    submit.backgrounds.append(_background())
    submit.scenarios.append(_scenario())
    enter.append_story(submit)
    enter.append_story(_story("Post Payment To Ledger", StoryType.SYSTEM, "Ledger"))
    reconcile = Epic("Reconcile Ledger", 2)
    pay.append_epic(reconcile)
    reconcile.append_story(_story("Rebuild Ledger Index", StoryType.TECHNICAL, "Batch"))
    return story_map


def outline(story_map: StoryModel, *, with_scenarios: bool = True) -> List[Any]:
    """Each epic as (name, its stories, its epics); each story as (name, kind, actors[, backgrounds, scenarios])."""
    return [_epic_outline(epic, with_scenarios) for epic in story_map.epics]


def _epic_outline(epic: Epic, with_scenarios: bool) -> tuple:
    stories = [_story_outline(story, with_scenarios) for story in epic.stories]
    return (epic.name, stories, [_epic_outline(child, with_scenarios) for child in epic.epics])


def _story_outline(story: Story, with_scenarios: bool) -> tuple:
    kind = getattr(story.story_type, "value", story.story_type)
    head = (story.name, kind, list(story.actors))
    if not with_scenarios:
        return head
    backgrounds = [_steps_outline(background.steps) for background in story.backgrounds]
    scenarios = [(scenario.name, _steps_outline(scenario.steps)) for scenario in story.scenarios]
    return head + (backgrounds, scenarios)


def _steps_outline(steps: List[Step]) -> List[tuple]:
    return [(step.keyword, step.text, [(extra.keyword, extra.text) for extra in step.ands]) for step in steps]


def _story(name: str, kind: StoryType, actor: str) -> Story:
    story = Story(name, 1, kind)
    story.actors = [actor]
    return story


def _background() -> Background:
    background = Background("background", 1)
    background.steps = [Step("an open account", StepType.GIVEN, 1, keyword="Given")]
    return background


def _scenario() -> Scenario:
    scenario = Scenario("pays a bill that is due", 1)
    given = Step("a bill is due", StepType.GIVEN, 1, keyword="Given")
    given.ands = [Step("the balance covers it", StepType.GIVEN, 1, keyword="And")]
    scenario.steps = [
        given,
        Step("the customer submits payment", StepType.WHEN, 2, keyword="When"),
        Step("the bill is paid", StepType.THEN, 3, keyword="Then"),
    ]
    return scenario
