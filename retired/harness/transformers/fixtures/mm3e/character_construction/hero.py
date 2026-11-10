"""
"""
from __future__ import annotations

from checks.trait import Trait


class PowerLevel:
    """Caps every player hero in the series and derives the starting power points budget."""

    def __init__(self, starting_power_points: int) -> None:
        ...

    @property
    def starting_power_points(self) -> int:
        ...


class Complication:
    """Records a narrative hook the hero must live with, including its type and trigger."""

    def __init__(self, type: str, trigger: str) -> None:
        ...

    @property
    def type(self) -> str:
        ...

    @property
    def trigger(self) -> str:
        ...


class TradeOff:
    """Moves ranks from one side of a limit pair to the other without changing the pair sum."""

    def __init__(self, pair: object, amount: int) -> None:
        ...

    @property
    def pair(self) -> object:
        ...

    @property
    def amount(self) -> int:
        ...


class Hero:
    """Spends power points on traits and enforces power level limit pairs for one hero."""

    # this module owns PP currency and PL caps; Ability, Skill, Advantage, and Power do not invent a second budget

    def __init__(self, power_level: PowerLevel, power_points: int) -> None:
        ...

    @property
    def power_level(self) -> PowerLevel:
        ...

    @property
    def power_points(self) -> int:
        ...

    @property
    def complications(self) -> list[Complication]:
        ...

    def spend_on(self, trait: Trait) -> None:
        ...

    def validate_balance(self) -> None:
        ...

    def enforce_limit_pair(self) -> None:
        ...
