"""
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from checks.trait import Trait

if TYPE_CHECKING:
    from character_construction.hero import Hero


class Ability(Trait):
    """Sets one of the eight ability ranks and cascades the traits that depend on it."""

    # voluntary rank never below -5; below -5 is debilitated from an effect
    # absent is not rank -5

    def __init__(
        self,
        character: object,
        trait_name: str,
        purchased_rank: int,
        measurement: object,
        hero: Hero,
    ) -> None:
        ...

    @property
    def natural_rank(self) -> int:
        ...

    @property
    def enhanced_rank(self) -> int:
        ...

    def set_rank(self, purchased_rank: int) -> None:
        # -> Hero.spend_on
        ...

    def cascade_dependents(self) -> None:
        ...

    def apply_absent_restrictions(self) -> None:
        ...

    def apply_debilitated(self) -> None:
        ...


class Defense(Trait):
    """Derives a defense rank from a source ability and tracks ranks bought above that base."""

    # Toughness cannot be bought above Stamina base

    def __init__(
        self,
        character: object,
        trait_name: str,
        purchased_rank: int,
        measurement: object,
        source_ability: Ability,
    ) -> None:
        ...

    @property
    def source_ability(self) -> Ability:
        ...

    @property
    def purchased_above_base(self) -> int:
        ...

    def derive_base(self) -> int:
        # -> Ability.purchased_rank
        ...
