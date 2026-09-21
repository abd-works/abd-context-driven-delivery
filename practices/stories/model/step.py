"""Step — one Given / When / Then line in a scenario (promoted from Clause)."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .source_location import SourceLocation
from .story_node import StoryNode
from .update_report import ChildCollectionPair

if TYPE_CHECKING:
    from .scenario import Clause, Phase


class Step(StoryNode):
    _semantic_type_name = "Step"

    def __init__(
        self,
        text: str,
        phase: "Phase",
        sequential_order: int,
        *,
        is_continuation: bool = False,
        concepts: Optional[List[str]] = None,
        values: Optional[List[str]] = None,
        actor: str = "",
        source: Optional[SourceLocation] = None,
        name: str = "",
    ) -> None:
        label = name or (text.strip()[:80] if text.strip() else f"step-{sequential_order}")
        super().__init__(name=label, sequential_order=sequential_order)
        self.text = text
        self.phase = phase
        self.is_continuation = is_continuation
        self.concepts: List[str] = list(concepts) if concepts is not None else []
        self.values: List[str] = list(values) if values is not None else []
        self.actor = actor
        self.source = source

    @classmethod
    def from_clause(cls, clause: "Clause", sequential_order: int) -> "Step":
        from .scenario import Clause as ClauseType

        assert isinstance(clause, ClauseType)
        return cls(
            text=clause.text,
            phase=clause.phase,
            sequential_order=sequential_order,
            is_continuation=clause.is_continuation,
            concepts=list(clause.concepts),
            values=list(clause.values),
            actor=clause.actor,
            source=clause.source,
        )

    def to_clause(self) -> "Clause":
        from .scenario import Clause

        return Clause(
            text=self.text,
            phase=self.phase,
            is_continuation=self.is_continuation,
            concepts=list(self.concepts),
            values=list(self.values),
            actor=self.actor,
            source=self.source,
        )

    def update_self(self, source: "Step") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.text = source.text
        self.phase = source.phase
        self.is_continuation = source.is_continuation
        self.concepts = list(source.concepts)
        self.values = list(source.values)
        self.actor = source.actor
        self.source = source.source

    def child_collections(self, source: "Step") -> List[ChildCollectionPair]:
        return []

    def snapshot_fields(self) -> dict:
        return {
            "text": self.text,
            "phase": self.phase,
            "is_continuation": self.is_continuation,
            "concepts": list(self.concepts),
            "values": list(self.values),
            "actor": self.actor,
        }
