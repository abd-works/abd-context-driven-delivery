"""Knowledge-graph channel for the Stories model."""

from __future__ import annotations

from harness.knowledge_graph.model.knowledge_graph_node import KnowledgeGraphNode
from practices.stories.model.story_model import (
    Background,
    Epic,
    Example,
    Increment,
    Scenario,
    Step,
    Story,
    StoryModel,
)


class KnowledgeGraphStoryModel(StoryModel, KnowledgeGraphNode):
    epicType = None
    incrementType = None

    def __init__(self, source=None) -> None:
        StoryModel.__init__(self, source)

    def save(self) -> str:
        return ""

    def load(self, path) -> "KnowledgeGraphStoryModel":
        return self

    def parse(self, text: str) -> "KnowledgeGraphStoryModel":
        return self

    def render(self, canonical=None, previous: str | None = None) -> str:
        del previous
        return (canonical or self).save()


class KnowledgeGraphIncrement(Increment, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Increment.__init__(self, source)


class KnowledgeGraphEpic(Epic, KnowledgeGraphNode):
    storyType = None

    def __init__(self, source) -> None:
        Epic.__init__(self, source)


class KnowledgeGraphStory(Story, KnowledgeGraphNode):
    scenarioType = None

    def __init__(self, source) -> None:
        Story.__init__(self, source)


class KnowledgeGraphScenario(Scenario, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Scenario.__init__(self, source)


class KnowledgeGraphBackground(Background, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Background.__init__(self, source)


class KnowledgeGraphStep(Step, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Step.__init__(self, source)


class KnowledgeGraphExample(Example, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Example.__init__(self, source.name, source.value, source.sequential_order, source.scope)


KnowledgeGraphStoryModel.epic_type = KnowledgeGraphEpic
KnowledgeGraphStoryModel.story_type = KnowledgeGraphStory
KnowledgeGraphStoryModel.increment_type = KnowledgeGraphIncrement
KnowledgeGraphEpic.storyType = KnowledgeGraphStory
