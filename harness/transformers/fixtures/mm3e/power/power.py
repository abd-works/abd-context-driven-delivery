"""
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from checks.measurement import Measurement
from checks.trait import Trait

if TYPE_CHECKING:
    from character_construction.hero import Hero
    from checks.check import CheckResult


class Extra:
    """A per-rank extra that raises an effect's cost."""

    def __init__(self, per_rank: bool) -> None:
        ...

    @property
    def per_rank(self) -> bool:
        ...


class Flaw:
    """A per-rank or removable flaw that lowers an effect's cost."""

    def __init__(self, per_rank: bool, removable: bool) -> None:
        ...

    @property
    def per_rank(self) -> bool:
        ...

    @property
    def removable(self) -> bool:
        ...


class Effect(Trait):
    """A power effect whose rank is a trait rank, resolved through checks."""

    # after flaws, at least 1 PP per rank (or fractional ranks) and at least 1 PP total
    # resistance DC is 10 + effect rank in checks

    def __init__(
        self,
        character: object,
        trait_name: str,
        purchased_rank: int,
        measurement: Measurement,
        action: str,
        range: str,
        duration: str,
        base_cost_per_rank: int,
        hero: Hero,
    ) -> None:
        ...

    @property
    def action(self) -> str:
        ...

    @property
    def range(self) -> str:
        ...

    @property
    def duration(self) -> str:
        ...

    @property
    def base_cost_per_rank(self) -> int:
        ...

    def resolve(self) -> CheckResult:
        # -> Trait.perform_check
        ...


class Array:
    """Holds a base effect and alternates; non-dynamic arrays are mutually exclusive."""

    # non-dynamic array effects are mutually exclusive

    def __init__(self, base_effect: Effect, alternates: list[Effect], dynamic: bool) -> None:
        ...

    @property
    def base_effect(self) -> Effect:
        ...

    @property
    def alternates(self) -> list[Effect]:
        ...

    @property
    def dynamic(self) -> bool:
        ...

    def switch_active(self) -> None:
        ...

    def reallocate(self) -> None:
        ...


class Power:
    """Selects effects, descriptors, and an array, and reports effect cost."""

    # cost = (base + extras − flaws) × rank + flat

    def __init__(self, descriptors: list[str], array: Array | None, cost: int) -> None:
        ...

    @property
    def descriptors(self) -> list[str]:
        ...

    @property
    def array(self) -> Array | None:
        ...

    @property
    def cost(self) -> int:
        ...
