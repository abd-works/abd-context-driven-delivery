"""BDD node types — specialise the Stories StoryNode base."""

from __future__ import annotations

from typing import List

from practices.stories.model.story_node import StoryNode
from practices.stories.model.update_report import ChildCollectionPair


class Description(StoryNode):
    _semantic_type_name = "Description"

    def __init__(self, name: str, sequential_order: int = 1) -> None:
        super().__init__(name=name, sequential_order=sequential_order)
        self.contexts: List["Context"] = []

    def update_self(self, source: StoryNode) -> None:
        assert isinstance(source, Description)
        self.name = source.name
        self.sequential_order = source.sequential_order

    def create_child_context(self, source: "Context") -> "Context":
        return Context(source.name, source.sequential_order)

    def child_collections(self, source: StoryNode) -> List[ChildCollectionPair]:
        assert isinstance(source, Description)
        return [
            ChildCollectionPair(
                self_children=self.contexts,
                source_children=source.contexts,
                create_child=self.create_child_context,
            )
        ]


class Context(StoryNode):
    _semantic_type_name = "Context"

    def __init__(self, name: str, sequential_order: int = 1) -> None:
        super().__init__(name=name, sequential_order=sequential_order)
        self.observations: List["Observation"] = []
        self.contexts: List["Context"] = []

    def update_self(self, source: StoryNode) -> None:
        assert isinstance(source, Context)
        self.name = source.name
        self.sequential_order = source.sequential_order

    def create_child_observation(self, source: "Observation") -> "Observation":
        return Observation(source.name, source.sequential_order)

    def create_child_context(self, source: "Context") -> "Context":
        return Context(source.name, source.sequential_order)

    def child_collections(self, source: StoryNode) -> List[ChildCollectionPair]:
        assert isinstance(source, Context)
        return [
            ChildCollectionPair(
                self_children=self.observations,
                source_children=source.observations,
                create_child=self.create_child_observation,
            ),
            ChildCollectionPair(
                self_children=self.contexts,
                source_children=source.contexts,
                create_child=self.create_child_context,
            ),
        ]


class Observation(StoryNode):
    _semantic_type_name = "Observation"

    def __init__(self, name: str, sequential_order: int = 1) -> None:
        super().__init__(name=name, sequential_order=sequential_order)

    def update_self(self, source: StoryNode) -> None:
        assert isinstance(source, Observation)
        self.name = source.name
        self.sequential_order = source.sequential_order

    def child_collections(self, source: StoryNode) -> List[ChildCollectionPair]:
        return []
