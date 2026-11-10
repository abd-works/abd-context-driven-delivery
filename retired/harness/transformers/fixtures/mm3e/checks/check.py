"""
"""
from __future__ import annotations

from .condition import Condition
from .trait import Trait


class DifficultyClass:
    """Names the number a check must meet or beat."""

    def __init__(self, value: int) -> None:
        ...

    @property
    def value(self) -> int:
        ...


class CheckResult:
    """Reports whether a resolved check met its difficulty class, and by how much."""

    @property
    def roll_total(self) -> int:
        ...

    @property
    def dc(self) -> DifficultyClass:
        ...

    @property
    def is_success(self) -> bool:
        ...

    @property
    def margin(self) -> int:
        ...

    @property
    def is_critical(self) -> bool:
        ...


class GradedCheckResult(CheckResult):
    """Grades a check result by degree of success or failure."""

    # always cap degree at 4
    # after grading, a natural 20 increases degree by one

    @property
    def degree(self) -> int:
        ...

    @property
    def resulting_condition(self) -> Condition | None:
        ...


class Check:
    """Resolves d20 plus modifier against a difficulty class."""

    # this module owns d20 + modifier vs DC; other modules ask Trait.perform_check

    def __init__(self, trait: Trait, dc: DifficultyClass) -> None:
        ...

    @property
    def trait(self) -> Trait:
        ...

    @property
    def dc(self) -> DifficultyClass:
        ...

    @property
    def circumstance_modifier(self) -> int:
        ...

    def resolve(self) -> CheckResult:
        # -> Trait.effective_rank
        ...

    def resolve_graded(self) -> GradedCheckResult:
        # -> Trait.effective_rank
        ...


class OpposedCheck(Check):
    """Resolves two traits against each other, or a trait against a passive difficulty class."""

    def __init__(self, trait: Trait, dc: DifficultyClass, opponent: Trait, is_passive: bool) -> None:
        ...

    @property
    def opponent(self) -> Trait:
        ...

    @property
    def is_passive(self) -> bool:
        ...

    def resolve(self) -> CheckResult:
        # -> Trait.effective_rank
        # -> Trait.perform_check
        ...


class RoutineCheck(Check):
    """Substitutes ten for the die when a routine check is allowed."""

    # never mark a routine check as critical

    def resolve(self) -> CheckResult:
        # -> Trait.effective_rank
        ...


class TeamCheck(Check):
    """Lets helpers modify the leader's check; only the leader's result decides the outcome."""

    def __init__(self, trait: Trait, dc: DifficultyClass, helpers: list[Trait]) -> None:
        ...

    @property
    def helpers(self) -> list[Trait]:
        ...

    def resolve(self) -> CheckResult:
        # -> Trait.perform_check
        ...
