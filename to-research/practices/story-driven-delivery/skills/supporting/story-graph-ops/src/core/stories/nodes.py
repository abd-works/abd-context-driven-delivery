"""Concrete domain node types: Epic, SubEpic, Story, AcceptanceCriteria.

Format backends (Markdown, JSON, DrawIO, Miro, TypeScript, ...) subclass these and
override create_child_xxx to return their concrete backend types.
"""

from __future__ import annotations

from enum import Enum
from typing import List

from .story_node import StoryNode
from .update_report import ChildCollectionPair


class StoryType(str, Enum):
    USER = "user"
    SYSTEM = "system"
    TECHNICAL = "technical"


class Epic(StoryNode):
    _semantic_type_name = "Epic"

    def __init__(self, name: str, sequential_order: int):
        super().__init__(name, sequential_order)
        self.sub_epics: List[SubEpic] = []
        self.domain_concepts: List[str] = []

    def update_self(self, source: "Epic") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.domain_concepts = list(source.domain_concepts)

    def child_collections(self, source: "Epic") -> List[ChildCollectionPair]:
        return [
            ChildCollectionPair(
                self_children=self.sub_epics,
                source_children=source.sub_epics,
                create_child=self.create_child_sub_epic,
            )
        ]

    def create_child_sub_epic(self, source: "SubEpic") -> "SubEpic":
        return SubEpic(source.name, source.sequential_order)

    def snapshot_fields(self) -> dict:
        return {"domain_concepts": list(self.domain_concepts)}


class SubEpic(StoryNode):
    _semantic_type_name = "SubEpic"

    def __init__(self, name: str, sequential_order: int):
        super().__init__(name, sequential_order)
        self.sub_epics: List[SubEpic] = []
        self.stories: List[Story] = []
        self.domain_concepts: List[str] = []
        self.test_file: str = ""

    @property
    def has_sub_epics(self) -> bool:
        return len(self.sub_epics) > 0

    def update_self(self, source: "SubEpic") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.test_file = source.test_file
        self.domain_concepts = list(source.domain_concepts)

    def child_collections(self, source: "SubEpic") -> List[ChildCollectionPair]:
        # WHY: sub-epics reconciled before stories so depth is known before story
        # rows are positioned in diagram backends.
        return [
            ChildCollectionPair(
                self_children=self.sub_epics,
                source_children=source.sub_epics,
                create_child=self.create_child_sub_epic,
            ),
            ChildCollectionPair(
                self_children=self.stories,
                source_children=source.stories,
                create_child=self.create_child_story,
            ),
        ]

    def create_child_sub_epic(self, source: "SubEpic") -> "SubEpic":
        return SubEpic(source.name, source.sequential_order)

    def create_child_story(self, source: "Story") -> "Story":
        return Story(source.name, source.sequential_order, source.story_type)

    def all_stories_recursive(self) -> List["Story"]:
        result: List[Story] = []
        for sub in self.sub_epics:
            result.extend(sub.all_stories_recursive())
        result.extend(self.stories)
        return result

    def snapshot_fields(self) -> dict:
        return {
            "test_file": self.test_file,
            "domain_concepts": list(self.domain_concepts),
        }


class Story(StoryNode):
    _semantic_type_name = "Story"

    def __init__(
        self,
        name: str,
        sequential_order: int,
        story_type: StoryType = StoryType.USER,
    ):
        super().__init__(name, sequential_order)
        self.story_type = story_type
        self.acceptance_criteria: List[AcceptanceCriteria] = []
        self.users: List[str] = []

    def update_self(self, source: "Story") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.story_type = source.story_type
        self.users = list(source.users)

    def child_collections(self, source: "Story") -> List[ChildCollectionPair]:
        return [
            ChildCollectionPair(
                self_children=self.acceptance_criteria,
                source_children=source.acceptance_criteria,
                create_child=self.create_child_acceptance_criteria,
            )
        ]

    def create_child_acceptance_criteria(
        self, source: "AcceptanceCriteria"
    ) -> "AcceptanceCriteria":
        return AcceptanceCriteria(source.name, source.sequential_order, source.text)

    def snapshot_fields(self) -> dict:
        return {"story_type": self.story_type, "users": list(self.users)}


class AcceptanceCriteria(StoryNode):
    _semantic_type_name = "AcceptanceCriteria"

    def __init__(self, name: str, sequential_order: int, text: str = ""):
        super().__init__(name, sequential_order)
        self.text = text

    def update_self(self, source: "AcceptanceCriteria") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.text = source.text

    def child_collections(
        self, source: "AcceptanceCriteria"
    ) -> List[ChildCollectionPair]:
        return []

    def snapshot_fields(self) -> dict:
        return {"text": self.text}
