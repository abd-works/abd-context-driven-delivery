"""
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from checks.measurement import Measurement
from checks.trait import Trait

if TYPE_CHECKING:
    from ability.ability import Ability
    from checks.check import CheckResult, DifficultyClass
    from character_construction.hero import Hero


class Skill(Trait):
    """Assigns skill ranks on a linked ability and makes the skill check."""

    # skill check is Trait.perform_check — do not fork a second d20 engine

    def __init__(
        self,
        character: object,
        trait_name: str,
        purchased_rank: int,
        measurement: Measurement,
        linked_ability: Ability,
        trained_only: bool,
        hero: Hero,
    ) -> None:
        ...

    @property
    def linked_ability(self) -> Ability:
        ...

    @property
    def trained_only(self) -> bool:
        ...

    def assign_ranks(self, purchased_rank: int) -> None:
        # -> Hero.spend_on
        ...

    def make_check(self, dc: DifficultyClass) -> CheckResult:
        # -> Trait.perform_check
        ...

    def resolve_untrained(self) -> None:
        ...
