"""Example — named fixture row expressing domain data for a scenario outline."""

from __future__ import annotations

from typing import Dict, List

from .story_node import StoryNode
from .update_report import ChildCollectionPair


class Example(StoryNode):
    _semantic_type_name = "Example"

    def __init__(
        self,
        name: str,
        sequential_order: int,
        fields: Dict[str, str] | None = None,
        scope: str = "scenario",
    ) -> None:
        super().__init__(name=name, sequential_order=sequential_order)
        self.fields: Dict[str, str] = dict(fields) if fields is not None else {}
        self.scope = scope

    def update_self(self, source: "Example") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.fields = dict(source.fields)
        self.scope = source.scope

    def child_collections(self, source: "Example") -> List[ChildCollectionPair]:
        return []
