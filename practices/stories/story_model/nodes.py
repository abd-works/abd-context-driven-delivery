"""Concrete domain node types: Epic, SubEpic, Story.

`AcceptanceCriteria` has been removed - `Story` now owns `Scenario` children
through `child_collections`, mirroring how `SubEpic` owns stories.

Format backends (Markdown, JSON, DrawIO, Miro, TypeScript, ...) subclass these
and override `create_child_xxx` to return their concrete backend types.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, List

from .story_node import StoryNode
from .update_report import ChildCollectionPair

if TYPE_CHECKING:
    from .scenario import Scenario
    from .test_file import TestCase, TestSuite


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
        # Clean Engineering {Type}ExampleFactory names this epic's helpers import.
        self.example_factories: List[str] = []

    def update_self(self, source: "Epic") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.domain_concepts = list(source.domain_concepts)
        self.example_factories = list(getattr(source, "example_factories", None) or [])
        self.estimate = source.estimate or ""

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
        return {
            "domain_concepts": list(self.domain_concepts),
            "example_factories": list(self.example_factories),
            "estimate": self.estimate,
        }


class SubEpic(StoryNode):
    _semantic_type_name = "SubEpic"

    def __init__(self, name: str, sequential_order: int):
        super().__init__(name, sequential_order)
        self.sub_epics: List[SubEpic] = []
        self.stories: List[Story] = []
        self.domain_concepts: List[str] = []
        # Local CE factories in addition to the owning epic's list.
        self.example_factories: List[str] = []
        self.test_file: str = ""
        # Populated by the workspace loader after load; never reconciled as
        # tree children - copied through update_self as a value list.
        self.test_suites: List["TestSuite"] = []

    @property
    def has_sub_epics(self) -> bool:
        return len(self.sub_epics) > 0

    def update_self(self, source: "SubEpic") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.test_file = source.test_file
        self.domain_concepts = list(source.domain_concepts)
        self.example_factories = list(getattr(source, "example_factories", None) or [])
        self.estimate = source.estimate or ""
        # TestSuites are ValueObjects - copied as values, never tree-reconciled.
        self.test_suites = list(getattr(source, "test_suites", []) or [])

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

    def layout_column_count(self) -> int:
        """Story grid columns - named stories only (estimates are not story cells)."""
        nested = sum(s.layout_column_count() for s in self.sub_epics)
        own = len(self.stories)
        if self.sub_epics:
            return max(nested + own, 1)
        return own

    def diagram_span_columns(self) -> int:
        """DrawIO sub-epic bar width in story-pitch columns (stories + estimate text).

        Own stories and nested sub-epics both consume columns (own stories first,
        then nested children left-to-right). Estimates only widen leaf bars.
        """
        nested = sum(s.diagram_span_columns() for s in self.sub_epics)
        story_cols = len(self.stories)
        if self.sub_epics:
            return max(nested + story_cols, 1)
        estimate = self.estimate.strip()
        if not estimate:
            return max(story_cols, 1)
        if story_cols == 0:
            return max(2, min(8, (len(estimate) + 12) // 18))
        extra = max(1, min(5, (len(estimate) + 15) // 22))
        return story_cols + extra

    def snapshot_fields(self) -> dict:
        return {
            "test_file": self.test_file,
            "domain_concepts": list(self.domain_concepts),
            "example_factories": list(self.example_factories),
            "estimate": self.estimate,
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
        self.users: List[str] = []
        self.domain_terms: List[str] = []
        self.evidence: List[str] = []
        # Scenario children - reconciled as tree children via child_collections.
        self.scenarios: List["Scenario"] = []
        # Populated by the workspace loader after load; never reconciled as
        # tree children - copied through update_self as a value list.
        self.test_cases: List["TestCase"] = []

    def update_self(self, source: "Story") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.story_type = source.story_type
        self.users = list(source.users)
        self.domain_terms = list(getattr(source, "domain_terms", []) or [])
        self.evidence = list(getattr(source, "evidence", []) or [])
        # TestCases are ValueObjects - copied as values, never tree-reconciled.
        self.test_cases = list(getattr(source, "test_cases", []) or [])
        # NOTE: scenarios are NOT copied here - they are reconciled by
        # child_collections / _reconcileCollection so that translate_from
        # produces the correct UpdateReport entries for scenario adds/removes.

    def child_collections(self, source: "Story") -> List[ChildCollectionPair]:
        return [
            ChildCollectionPair(
                self_children=self.scenarios,
                source_children=source.scenarios,
                create_child=self.create_child_scenario,
            )
        ]

    def create_child_scenario(self, source: "Scenario") -> "Scenario":
        from .scenario import Scenario  # lazy import to avoid cycle
        return Scenario(source.name, source.sequential_order, source.story_name)

    def snapshot_fields(self) -> dict:
        return {"story_type": self.story_type, "users": list(self.users)}
