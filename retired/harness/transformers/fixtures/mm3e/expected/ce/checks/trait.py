"""
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from .measurement import Measurement

if TYPE_CHECKING:
    from .check import CheckResult, DifficultyClass


class Trait:
    """Supplies the modifier a check uses when someone acts with a named trait."""

    # never add ranks as integers — convert through Measurement then convert back

    def __init__(self, character: object, trait_name: str, purchased_rank: int, measurement: Measurement) -> None:
        ...

    @property
    def character(self) -> object:
        # Character token from a neighbor; this module does not import that neighbor
        ...

    @property
    def trait_name(self) -> str:
        ...

    @property
    def purchased_rank(self) -> int:
        ...

    @property
    def effective_rank(self) -> int:
        # only active conditions apply modifiers
        ...

    def real_world_value(self, type: object) -> object:
        # -> Measurement.lookup
        ...

    def add_rank(self, other: Trait, type: object) -> int:
        # never add ranks as integers
        # -> Measurement.lookup
        # -> Measurement.rank_for
        ...

    def perform_check(self, dc: DifficultyClass) -> CheckResult:
        # -> Measurement.lookup
        # -> Check.resolve
        ...
