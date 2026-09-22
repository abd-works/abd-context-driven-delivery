"""Stories types on the practice graph — wrap live Stories types."""

from __future__ import annotations

from practices.stories.model.background import Background as SourceBackground
from practices.stories.model.example import Example as SourceExample
from practices.stories.model.nodes import Epic as SourceEpic, Story as SourceStory, SubEpic as SourceSubEpic
from practices.stories.model.scenario import Scenario as SourceScenario
from practices.stories.model.step import Step as SourceStep
from practices.stories.model.story_map import StoryMap as SourceStoryMap

from harness.knowledge_graph.model.graph_node import Node


class Example(SourceExample, Node):
    practice = "stories"
    _semantic_type_name = "Example"


class Step(SourceStep, Node):
    practice = "stories"
    _semantic_type_name = "Step"


class Background(SourceBackground, Node):
    practice = "stories"
    _semantic_type_name = "Background"

    def load_step(self, source: SourceStep) -> Step:
        return _step_from(source)


class Scenario(SourceScenario, Node):
    practice = "stories"
    _semantic_type_name = "Scenario"

    def load_background(self, source: SourceBackground) -> Background:
        return Background(source.name, source.sequential_order)

    def load_step(self, source: SourceStep) -> Step:
        return _step_from(source)

    def load_example(self, source: SourceExample) -> Example:
        return Example(source.name, source.sequential_order, dict(source.fields), source.scope)


class Story(SourceStory, Node):
    practice = "stories"
    _semantic_type_name = "Story"

    def load_background(self, source: SourceBackground) -> Background:
        return Background(source.name, source.sequential_order)

    def load_scenario(self, source: SourceScenario) -> Scenario:
        return Scenario(source.name, source.sequential_order, source.story_name)

    def load_example(self, source: SourceExample) -> Example:
        return Example(source.name, source.sequential_order, dict(source.fields), source.scope)


class SubEpic(SourceSubEpic, Node):
    practice = "stories"
    _semantic_type_name = "SubEpic"

    def load_sub_epic(self, source: SourceSubEpic) -> "SubEpic":
        return SubEpic(source.name, source.sequential_order)

    def load_story(self, source: SourceStory) -> Story:
        return Story(source.name, source.sequential_order, source.story_type)

    def load_example(self, source: SourceExample) -> Example:
        return Example(source.name, source.sequential_order, dict(source.fields), source.scope)


class Epic(SourceEpic, Node):
    practice = "stories"
    _semantic_type_name = "Epic"

    def load_sub_epic(self, source: SourceSubEpic) -> SubEpic:
        return SubEpic(source.name, source.sequential_order)

    def load_example(self, source: SourceExample) -> Example:
        return Example(source.name, source.sequential_order, dict(source.fields), source.scope)


class StoryMap(SourceStoryMap, Node):
    practice = "stories"
    _semantic_type_name = "StoryMap"

    def load_epic(self, source: SourceEpic) -> Epic:
        return Epic(source.name, source.sequential_order)

    def load_example(self, source: SourceExample) -> Example:
        return Example(source.name, source.sequential_order, dict(source.fields), source.scope)


def _step_from(source: SourceStep) -> Step:
    return Step(
        text=source.text,
        phase=source.phase,
        sequential_order=source.sequential_order,
        is_continuation=source.is_continuation,
        keyword=getattr(source, "keyword", "") or "",
        concepts=list(source.concepts),
        values=list(source.values),
        actor=source.actor,
        source=source.source,
        name=source.name,
    )
