"""Knowledge-graph channel for the Stories model."""

from __future__ import annotations

from pathlib import Path

from harness.knowledge_graph.model.knowledge_graph_node import KnowledgeGraphNode
from practices.stories.model.json.nodes import JsonStoryModel
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
    def __init__(self, source=None) -> None:
        StoryModel.__init__(self, source)

    def save(self) -> str:
        return JsonStoryModel().render(self)

    def load(self, path) -> "KnowledgeGraphStoryModel":
        text = Path(path).read_text(encoding="utf-8") if Path(path).is_file() else ""
        if not text:
            folder = Path(path)
            candidate = folder / "story-map.kg" if folder.is_dir() else Path(path)
            if candidate.is_file():
                text = candidate.read_text(encoding="utf-8")
        if not text:
            return self
        return type(self)(JsonStoryModel().parse(text))

    def parse(self, text: str) -> "KnowledgeGraphStoryModel":
        return type(self)(JsonStoryModel().parse(text))

    def render(self, canonical=None, previous: str | None = None) -> str:
        del previous
        return (canonical or self).save()


class KnowledgeGraphIncrement(Increment, KnowledgeGraphNode):
    def __init__(self, source, story_class=None, **kwargs) -> None:
        Increment.__init__(self, source)


class KnowledgeGraphEpic(Epic, KnowledgeGraphNode):
    storyType = None

    def __init__(self, source, story_class=None, **kwargs) -> None:
        Epic.__init__(self, source, story_class=story_class or KnowledgeGraphStory)


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
KnowledgeGraphStory.scenarioType = KnowledgeGraphScenario
