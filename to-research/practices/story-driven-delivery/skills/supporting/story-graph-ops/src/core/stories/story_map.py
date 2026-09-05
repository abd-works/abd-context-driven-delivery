"""StoryMap — root container that holds Epics and delegates translation to them."""

from __future__ import annotations

from typing import List

from .nodes import Epic
from .story_node import StoryNode
from .update_report import ChildCollectionPair, UpdateReport


class StoryMap(StoryNode):
    _semantic_type_name = "StoryMap"

    def __init__(self) -> None:
        super().__init__(name="StoryMap", sequential_order=0)
        self.epics: List[Epic] = []

    def append_epic(self, epic: Epic) -> None:
        self.epics.append(epic)
        self._renumber_epics()

    def remove_epic(self, epic_name: str) -> Epic:
        for i, epic in enumerate(self.epics):
            if epic.name == epic_name:
                removed = self.epics.pop(i)
                self._renumber_epics()
                return removed
        raise KeyError(f"Epic {epic_name!r} not found")

    def reorder_epics(self, new_name_order: List[str]) -> None:
        by_name = {epic.name: epic for epic in self.epics}
        if set(by_name) != set(new_name_order):
            raise ValueError("new_name_order must be a permutation of existing Epic names")
        self.epics = [by_name[name] for name in new_name_order]
        self._renumber_epics()

    def find_epic(self, name: str) -> Epic:
        for epic in self.epics:
            if epic.name == name:
                return epic
        raise KeyError(f"Epic {name!r} not found")

    def update_self(self, source: "StoryMap") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order

    def child_collections(self, source: "StoryMap") -> List[ChildCollectionPair]:
        return [
            ChildCollectionPair(
                self_children=self.epics,
                source_children=source.epics,
                create_child=self.create_child_epic,
            )
        ]

    def create_child_epic(self, source: Epic) -> Epic:
        return Epic(source.name, source.sequential_order)

    def _renumber_epics(self) -> None:
        for i, epic in enumerate(self.epics, start=1):
            epic.sequential_order = i

    def snapshot_fields(self) -> dict:
        return {}
