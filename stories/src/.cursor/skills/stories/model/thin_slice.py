"""Increment — one delivery step in the thin-slicing plan.

`Increment` is a `StoryNode` leaf: `child_collections` returns `[]` and all
fields are copied through `update_self`. The `ThinSlice` wrapper that used to
hold a list of increments has been removed — `StoryMap.increments` owns them
directly as reconciled tree children.
"""

from __future__ import annotations

from typing import List, Optional

from .source_location import SourceLocation
from .story_node import StoryNode
from .update_report import ChildCollectionPair


class Increment(StoryNode):
    """One increment in a thin-slicing plan — a StoryNode leaf.

    - `name` — the increment title (e.g. "Move money same-day for one treasurer")
    - `sequential_order` — position within the StoryMap (1-indexed)
    - `outcome` — the marketable outcome sentence
    - `stories` — verb-noun story names (must match story-map names)
    - `slicing_notes` — optional explanation of manual steps / stubs / cuts
    - `decision_prompt` — the follow-up question after this increment ships
    """

    _semantic_type_name = "Increment"

    def __init__(
        self,
        name: str,
        sequential_order: int = 0,
    ) -> None:
        super().__init__(name=name, sequential_order=sequential_order)
        self.outcome: str = ""
        self.slicing_notes: str = ""
        self.stories: List[str] = []
        self.decision_prompt: str = ""
        self.source: Optional[SourceLocation] = None

    def update_self(self, source: "Increment") -> None:  # type: ignore[override]
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.outcome = source.outcome
        self.slicing_notes = source.slicing_notes
        # Value copy — stories is a list of name strings, not object references.
        self.stories = list(source.stories)
        self.decision_prompt = source.decision_prompt
        self.source = source.source

    def child_collections(self, source: "Increment") -> List[ChildCollectionPair]:  # type: ignore[override]
        # WHY: Increment is a leaf — outcome, stories, and prompt are value-copied
        # through update_self, not reconciled as tree children.
        return []

    def snapshot_fields(self) -> dict:
        return {
            "outcome": self.outcome,
            "slicing_notes": self.slicing_notes,
            "stories": list(self.stories),
            "decision_prompt": self.decision_prompt,
        }
