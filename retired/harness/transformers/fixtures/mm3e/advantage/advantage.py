"""
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from checks.measurement import Measurement
from checks.trait import Trait

if TYPE_CHECKING:
    from character_construction.hero import Hero


class AttackTradeOff:
    """Moves an amount from one attack or defense stat to the other."""

    def __init__(self, penalty_stat: Trait, bonus_stat: Trait, amount: int) -> None:
        ...

    @property
    def penalty_stat(self) -> Trait:
        ...

    @property
    def bonus_stat(self) -> Trait:
        ...

    @property
    def amount(self) -> int:
        ...


class Luck:
    """Tracks luck uses this session, re-rolls, and refresh."""

    def __init__(self, uses_this_session: int) -> None:
        ...

    @property
    def uses_this_session(self) -> int:
        ...

    def re_roll(self) -> None:
        ...

    def refresh(self) -> None:
        ...


class Advantage(Trait):
    """Purchases an advantage and applies its combat, fortune, or skill effect."""

    def __init__(
        self,
        character: object,
        trait_name: str,
        purchased_rank: int,
        measurement: Measurement,
        category: str,
        rank: int,
        hero: Hero,
    ) -> None:
        ...

    @property
    def category(self) -> str:
        ...

    @property
    def rank(self) -> int:
        ...

    def purchase(self) -> None:
        # -> Hero.spend_on
        ...

    def apply(self) -> None:
        ...
