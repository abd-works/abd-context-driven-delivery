"""Scenario - phase-grouped Given -> When -> Then walk-through."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .background import Background
from .example import Example
from .source_location import SourceLocation
from .step import Step
from .story_node import StoryNode
from .update_report import ChildCollectionPair


class Phase(str, Enum):
    """Which phase a step belongs to (implicit from its list; useful for reporting)."""

    GIVEN = "given"
    WHEN = "when"
    THEN = "then"


@dataclass
class Clause:
    """Legacy value type — use Step nodes in the scenario tree; kept for format channels."""

    text: str
    phase: Phase
    is_continuation: bool = False
    concepts: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    actor: str = ""
    source: Optional[SourceLocation] = None


@dataclass
class Interaction:
    """Legacy when-then grouping — reconstructed from Step nodes when needed."""

    when: List[Clause] = field(default_factory=list)
    then: List[Clause] = field(default_factory=list)


class Scenario(StoryNode):
    """Behaviour walk-through under a story.

    Tree children: Background, Step, Example.
    Legacy ``given`` / ``interactions`` / ``background`` / ``example_rows`` remain
    for markdown and code format channels until those backends render from the tree.
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
        self.backgrounds: List[Background] = []
        self.steps: List[Step] = []
        self.examples: List[Example] = []
        # Legacy fields — synced with the tree via sync helpers.
        self.given: List[Clause] = []
        self.interactions: List[Interaction] = []
        self.is_outline: bool = False
        self.example_rows: List[dict] = []
        self.background: List[Clause] = []
        self.evidence: List[str] = []
        self.source: Optional[SourceLocation] = None

    def update_self(self, source: "Scenario") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.story_name = source.story_name
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
        if not source.backgrounds and not source.steps and not source.examples:
            self.sync_tree_from_legacy()

    def load_background(self, source: Background) -> Background:
        return Background(source.name, source.sequential_order)

    def load_step(self, source: Step) -> Step:
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

    def load_example(self, source: Example) -> Example:
        return Example(source.name, source.sequential_order, dict(source.fields), source.scope)

    def child_collections(self, source: "Scenario") -> List[ChildCollectionPair]:
        return [
            ChildCollectionPair(
                self_children=self.backgrounds,
                source_children=source.backgrounds,
                load=self.load_background,
            ),
            ChildCollectionPair(
                self_children=self.steps,
                source_children=source.steps,
                load=self.load_step,
            ),
            ChildCollectionPair(
                self_children=self.examples,
                source_children=source.examples,
                load=self.load_example,
            ),
        ]

    def sync_tree_from_legacy(self) -> None:
        """Build Background / Step / Example children from legacy clause and row fields."""
        self.backgrounds = []
        self.steps = []
        self.examples = []

        if self.background:
            bg = Background("background", 1)
            for index, clause in enumerate(self.background, start=1):
                bg.steps.append(Step.from_clause(clause, index))
            self.backgrounds = [bg]

        order = 0
        for clause in self.given:
            order += 1
            self.steps.append(Step.from_clause(clause, order))
        for interaction in self.interactions:
            for clause in interaction.when:
                order += 1
                self.steps.append(Step.from_clause(clause, order))
            for clause in interaction.then:
                order += 1
                self.steps.append(Step.from_clause(clause, order))

        for index, row in enumerate(self.example_rows, start=1):
            label = str(row.get("example") or row.get("name") or f"example-{index}")
            self.examples.append(Example(label, index, dict(row)))

    def sync_legacy_from_tree(self) -> None:
        """Rebuild legacy clause fields from tree children (for format renderers)."""
        self.background = []
        self.given = []
        self.interactions = []
        self.example_rows = []

        if self.backgrounds:
            self.background = [step.to_clause() for step in self.backgrounds[0].steps]

        interaction: Interaction | None = None
        for step in self.steps:
            clause = step.to_clause()
            if step.phase == Phase.GIVEN:
                self.given.append(clause)
            elif step.phase == Phase.WHEN:
                interaction = Interaction()
                self.interactions.append(interaction)
                interaction.when.append(clause)
            elif step.phase == Phase.THEN:
                if interaction is None:
                    interaction = Interaction()
                    self.interactions.append(interaction)
                interaction.then.append(clause)

        self.example_rows = [dict(example.fields) for example in self.examples]

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

    @property
    def when_clauses(self) -> List[Clause]:
        return [step.to_clause() for step in self.steps if step.phase == Phase.WHEN]

    @property
    def then_clauses(self) -> List[Clause]:
        return [step.to_clause() for step in self.steps if step.phase == Phase.THEN]

    @property
    def all_clauses(self) -> List[Clause]:
        return [step.to_clause() for step in self.steps]

    @property
    def clause_count(self) -> int:
        return len(self.background) + len(self.steps)
