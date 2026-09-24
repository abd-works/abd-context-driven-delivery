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

    def value_for(self, field_name: str) -> str:
        return self.fields.get(field_name, "")

    def matches_export(self, export_name: str) -> bool:
        export_lower = (export_name or "").lower()
        name_lower = self.name.lower()
        return export_lower in name_lower or name_lower in export_lower
