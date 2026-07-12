"""Scenario — phase-grouped Given → When → Then walk-through.

Canonical shape derives from the reference testing architecture:

  Scenario = { name, given: Clause[], interactions: [{ when: Clause[], then: Clause[] }] }

`Scenario` is a `StoryNode` leaf: `child_collections` returns `[]` and all
fields are copied through `update_self`, not reconciled as tree children.

The first clause of each phase is unprefixed (`Given a User…`, `When they …`,
`Then it …`). Continuation clauses carry their own `And ` / `But ` prefix in
the text — that string is the same key used later by the tier-class runner
to dispatch step implementations, so preserving it verbatim matters.

Phase membership is IMPLICIT in which list a clause lives in — no more
`kind` enum. Scanners that used to check `step.kind == WHEN` now iterate
`scenario.when_clauses` (or filter via a helper property).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .source_location import SourceLocation
from .story_node import StoryNode
from .update_report import ChildCollectionPair


class Phase(str, Enum):
    """Which phase a clause belongs to (implicit from its list; useful for reporting)."""

    GIVEN = "given"
    WHEN = "when"
    THEN = "then"


@dataclass
class Clause:
    """One step string in a scenario.

    - `text` — the verbatim step string (with any `And ` / `But ` continuation
       prefix intact; empty first-of-phase clauses have no prefix)
    - `is_continuation` — true when `text` starts with `And ` / `But `
    - `phase` — cached membership (given/when/then) so `all_clauses` can be
       walked without losing phase context
    - `concepts` — bold-marked concept names (**X**) extracted from `text`
    - `values` — italic-marked values (*v*) extracted from `text`
    - `actor` — first bold concept treated as an actor (heuristic; empty if unclear)
    """

    text: str
    phase: Phase
    is_continuation: bool = False
    concepts: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    actor: str = ""
    source: Optional[SourceLocation] = None


@dataclass
class Interaction:
    """A when-then block — one action, one observed set of outcomes.

    A scenario usually has exactly one interaction; multi-interaction scenarios
    model chains where a follow-up when only makes sense after the previous
    then has been observed. Most rules treat multiple interactions as a smell
    to flag for review.
    """

    when: List[Clause] = field(default_factory=list)
    then: List[Clause] = field(default_factory=list)


class Scenario(StoryNode):
    """A behaviour walk-through under a story — promoted to StoryNode leaf.

    `child_collections` returns `[]`; all fields are copied through
    `update_self`. The reconciliation loop never recurses into scenario
    children — scenarios are always value-copied, not reconciled.

    Fields:
    - `name` — the scenario title (verb-noun, outcome-oriented)
    - `sequential_order` — position within the parent story (1-indexed)
    - `story_name` — parent story name (empty if not resolvable)
    - `given` — setup clauses
    - `interactions` — one or more when-then blocks
    - `is_outline` — true when this is a Scenario Outline backed by example rows
    - `example_rows` — rows of the outline's examples table
    - `background` — clauses applied before the scenario runs
    - `evidence` — free-text lines tying the scenario back to sources
    """

    _semantic_type_name = "Scenario"

    def __init__(
        self,
        name: str,
        sequential_order: int = 0,
        story_name: str = "",
    ) -> None:
        super().__init__(name=name, sequential_order=sequential_order)
        self.story_name: str = story_name
        self.given: List[Clause] = []
        self.interactions: List[Interaction] = []
        self.is_outline: bool = False
        self.example_rows: List[dict] = []
        self.background: List[Clause] = []
        self.evidence: List[str] = []
        self.source: Optional[SourceLocation] = None

    def update_self(self, source: "Scenario") -> None:  # type: ignore[override]
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.story_name = source.story_name
        # Deep-copy lists so mutations to the source do not affect the target.
        self.given = list(source.given)
        self.interactions = [
            Interaction(when=list(i.when), then=list(i.then))
            for i in source.interactions
        ]
        self.is_outline = source.is_outline
        self.example_rows = list(source.example_rows)
        self.background = list(source.background)
        self.evidence = list(source.evidence)
        self.source = source.source

    def child_collections(self, source: "Scenario") -> List[ChildCollectionPair]:  # type: ignore[override]
        # WHY: Scenario is a leaf — clauses and interactions are value-copied
        # through update_self, not reconciled as tree children.
        return []

    def snapshot_fields(self) -> dict:
        return {
            "story_name": self.story_name,
            "given": list(self.given),
            "interactions": list(self.interactions),
            "is_outline": self.is_outline,
            "example_rows": list(self.example_rows),
            "background": list(self.background),
            "evidence": list(self.evidence),
        }

    # ── convenience properties ──────────────────────────────────────────────

    @property
    def when_clauses(self) -> List[Clause]:
        return [c for i in self.interactions for c in i.when]

    @property
    def then_clauses(self) -> List[Clause]:
        return [c for i in self.interactions for c in i.then]

    @property
    def all_clauses(self) -> List[Clause]:
        clauses: List[Clause] = list(self.given)
        for interaction in self.interactions:
            clauses.extend(interaction.when)
            clauses.extend(interaction.then)
        return clauses

    @property
    def clause_count(self) -> int:
        return len(self.given) + sum(len(i.when) + len(i.then) for i in self.interactions)
