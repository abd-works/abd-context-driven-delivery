"""Resolve StoryModel nodes for graph rule checks."""

from __future__ import annotations

from cdd_guidance.practices.stories.model.story_model import Scenario, Step, StoryModel


def iter_scenarios(model: StoryModel):
    for epic in model.epics:
        yield from _epic_scenarios(epic)


def _epic_scenarios(epic):
    for story in epic.stories:
        for scenario in story.scenarios:
            yield story, scenario
    for child in epic.epics:
        yield from _epic_scenarios(child)


def scenario_named(model: StoryModel, name: str) -> Scenario | None:
    for _story, scenario in iter_scenarios(model):
        if scenario.name == name:
            return scenario
    return None


def scenario_for_graph_node(node, context) -> Scenario | None:
    model = context.story_model()
    if model is None or node.type != "Scenario":
        return None
    return scenario_named(model, node.name)


def step_from_model(scenario: Scenario, node, context) -> Step | None:
    text = context.step_text(node)
    keyword = context.step_keyword(node)
    for step in scenario.steps:
        if _step_matches(step, text, keyword):
            return step
        for child in step.ands:
            if _step_matches(child, text, keyword):
                return child
    return None


def _step_matches(step: Step, text: str, keyword: str) -> bool:
    if text and step.text.strip() == text.strip():
        return True
    if keyword and step.keyword.casefold() == keyword.casefold():
        if not text:
            return True
        return text.strip() in step.text
    return False


def example_count(scenario: Scenario) -> int:
    examples = getattr(scenario, "examples", None)
    if examples is None:
        return 0
    try:
        return len(examples)
    except TypeError:
        return 0
