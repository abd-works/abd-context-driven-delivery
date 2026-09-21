"""Background — shared Given steps scoped to a story or scenario."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from .story_node import StoryNode
from .update_report import ChildCollectionPair

if TYPE_CHECKING:
    from .step import Step


class Background(StoryNode):
    _semantic_type_name = "Background"

    def __init__(self, name: str = "background", sequential_order: int = 1) -> None:
        super().__init__(name=name, sequential_order=sequential_order)
        self.steps: List["Step"] = []

    def update_self(self, source: "Background") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order

    def create_child_step(self, source: "Step") -> "Step":
        from .step import Step

        return Step(
            text=source.text,
            phase=source.phase,
            sequential_order=source.sequential_order,
            is_continuation=source.is_continuation,
            concepts=list(source.concepts),
            values=list(source.values),
            actor=source.actor,
            source=source.source,
            name=source.name,
        )

    def child_collections(self, source: "Background") -> List[ChildCollectionPair]:
        return [
            ChildCollectionPair(
                self_children=self.steps,
                source_children=source.steps,
                create_child=self.create_child_step,
            )
        ]
