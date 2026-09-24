"""Concrete domain node types: Epic, SubEpic, Story.

`AcceptanceCriteria` has been removed - `Story` now owns `Scenario` children
through `child_collections`, mirroring how `SubEpic` owns stories.

Format backends (Markdown, JSON, DrawIO, Miro, TypeScript, ...) subclass these
and override `load_xxx` to return their concrete backend types.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import TYPE_CHECKING, Iterable, List

from .story_node import StoryNode
from .update_report import ChildCollectionPair

if TYPE_CHECKING:
    from .background import Background
    from .example import Example
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
        self.examples: List["Example"] = []
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
                load=self.load_sub_epic,
            ),
            ChildCollectionPair(
                self_children=self.examples,
                source_children=getattr(source, "examples", []),
                load=self.load_example,
            ),
        ]

    def load_sub_epic(self, source: "SubEpic") -> "SubEpic":
        return SubEpic(source.name, source.sequential_order)

    def load_example(self, source: "Example") -> "Example":
        from .example import Example

        return Example(source.name, source.sequential_order, dict(source.fields), source.scope)

    def snapshot_fields(self) -> dict:
        return {
            "domain_concepts": list(self.domain_concepts),
            "example_factories": list(self.example_factories),
            "estimate": self.estimate,
        }

    def normalize_factory_name(self, name: str) -> str:
        raw = (name or "").strip()
        if not raw:
            return ""
        if raw.endswith("ExampleFactory"):
            return raw
        return f"{raw}ExampleFactory"

    def collected_example_factories(self) -> List[str]:
        self._factory_names: list[str] = []
        self._factory_seen: set[str] = set()
        self._factory_pattern = re.compile(r"^[A-Z][A-Za-z0-9]*ExampleFactory$")
        self._add_factory_names(self)
        self._walk_factory_subs(self.sub_epics)
        return self._factory_names

    def _add_factory_names(self, node: object) -> None:
        for raw in getattr(node, "example_factories", None) or []:
            self._remember_factory(raw)
        for concept in getattr(node, "domain_concepts", None) or []:
            if str(concept).endswith("ExampleFactory"):
                self._remember_factory(str(concept))

    def _remember_factory(self, raw: str) -> None:
        name = self.normalize_factory_name(raw)
        if not name or name in self._factory_seen or not self._factory_pattern.match(name):
            return
        self._factory_seen.add(name)
        self._factory_names.append(name)

    def _walk_factory_subs(self, subs: Iterable["SubEpic"]) -> None:
        for sub in subs or []:
            self._add_factory_names(sub)
            self._walk_factory_subs(getattr(sub, "sub_epics", None) or [])


class SubEpic(StoryNode):
    _semantic_type_name = "SubEpic"

    def __init__(self, name: str, sequential_order: int):
        super().__init__(name, sequential_order)
        self.sub_epics: List[SubEpic] = []
        self.stories: List[Story] = []
        self.examples: List["Example"] = []
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
                load=self.load_sub_epic,
            ),
            ChildCollectionPair(
                self_children=self.stories,
                source_children=source.stories,
                load=self.load_story,
            ),
            ChildCollectionPair(
                self_children=self.examples,
                source_children=getattr(source, "examples", []),
                load=self.load_example,
            ),
        ]

    def load_sub_epic(self, source: "SubEpic") -> "SubEpic":
        return SubEpic(source.name, source.sequential_order)

    def load_story(self, source: "Story") -> "Story":
        return Story(source.name, source.sequential_order, source.story_type)

    def load_example(self, source: "Example") -> "Example":
        from .example import Example

        return Example(source.name, source.sequential_order, dict(source.fields), source.scope)

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
        # Background, scenario, and example children — reconciled as tree children.
        # Background belongs to the Story (same as Scenario). Nesting scenarios
        # inside background() in TypeScript is only an execution convenience.
        self.backgrounds: List["Background"] = []
        self.scenarios: List["Scenario"] = []
        self.examples: List["Example"] = []
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
                self_children=self.backgrounds,
                source_children=getattr(source, "backgrounds", []),
                load=self.load_background,
            ),
            ChildCollectionPair(
                self_children=self.scenarios,
                source_children=source.scenarios,
                load=self.load_scenario,
            ),
            ChildCollectionPair(
                self_children=self.examples,
                source_children=getattr(source, "examples", []),
                load=self.load_example,
            ),
        ]

    def load_background(self, source: "Background") -> "Background":
        from .background import Background

        return Background(source.name, source.sequential_order)

    def load_scenario(self, source: "Scenario") -> "Scenario":
        from .scenario import Scenario  # lazy import to avoid cycle
        return Scenario(source.name, source.sequential_order, source.story_name)

    def load_example(self, source: "Example") -> "Example":
        from .example import Example

        return Example(source.name, source.sequential_order, dict(source.fields), source.scope)

    def snapshot_fields(self) -> dict:
        return {"story_type": self.story_type, "users": list(self.users)}
