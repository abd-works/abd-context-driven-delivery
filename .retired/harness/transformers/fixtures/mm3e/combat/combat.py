"""
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ability.ability import Ability, Defense
    from checks.check import CheckResult, DifficultyClass, GradedCheckResult
    from checks.condition import ImposedConditions
    from checks.trait import Trait


class Turn:
    """Holds the standard, move, free, and reaction slots of one turn."""

    def __init__(
        self,
        standard_action: bool,
        move_action: bool,
        free_action: bool,
        reaction: bool,
    ) -> None:
        ...

    @property
    def standard_action(self) -> bool:
        ...

    @property
    def move_action(self) -> bool:
        ...

    @property
    def free_action(self) -> bool:
        ...

    @property
    def reaction(self) -> bool:
        ...


class ActionRound:
    """Orders turns and rolls initiative."""

    def __init__(self, turn_order: list[Turn]) -> None:
        ...

    @property
    def turn_order(self) -> list[Turn]:
        ...

    def roll_initiative(self) -> None:
        # -> Ability.effective_rank
        ...


class Attack:
    """Resolves an attack check against a parry or dodge class and confirms a critical."""

    # attack check is a Check against Parry or Dodge class

    def __init__(self, attack_bonus: Trait, defense_class: DifficultyClass) -> None:
        ...

    @property
    def attack_bonus(self) -> Trait:
        ...

    @property
    def defense_class(self) -> DifficultyClass:
        ...

    def resolve(self) -> CheckResult:
        # -> Trait.perform_check
        ...

    def confirm_critical(self) -> bool:
        ...


class Damage:
    """Applies damage degrees from a graded Toughness resistance."""

    # damage is a graded Toughness resistance

    def __init__(self, toughness_resistance: Defense) -> None:
        ...

    @property
    def toughness_resistance(self) -> Defense:
        ...

    def apply_degree(self) -> None:
        # -> Defense.perform_check
        # -> ImposedConditions.apply
        ...


class HeroPoint:
    """Spends a hero point."""

    def spend(self) -> None:
        ...


class ExtraEffort:
    """Declares an extra-effort benefit and applies fatigue."""

    def declare_benefit(self) -> None:
        ...

    def apply_fatigue(self) -> None:
        # -> ImposedConditions.apply
        ...
