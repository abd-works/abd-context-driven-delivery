"""
"""
from __future__ import annotations

from power.power import Array, Power


class Equipment:
    """Spends equipment points on items without stacking the same-type equipment bonus."""

    # equipment bonus does not stack with same-type equipment bonus
    # Protection from a device is not equipment bonus

    def __init__(self, equipment_points: int, items: list[object]) -> None:
        ...

    @property
    def equipment_points(self) -> int:
        ...

    @property
    def items(self) -> list[object]:
        ...

    def pay_for(self, item: object) -> None:
        ...


class Device(Power):
    """A power worn or carried as a removable device."""

    def __init__(
        self,
        descriptors: list[str],
        array: Array | None,
        cost: int,
        removable: bool,
        easily_removable: bool,
        indestructible: bool,
    ) -> None:
        ...

    @property
    def removable(self) -> bool:
        ...

    @property
    def easily_removable(self) -> bool:
        ...

    @property
    def indestructible(self) -> bool:
        ...


class Vehicle:
    """A vehicle with size traits and features."""

    def __init__(self, size: str, features: list[str]) -> None:
        ...

    @property
    def size(self) -> str:
        ...

    @property
    def features(self) -> list[str]:
        ...


class Headquarters:
    """A headquarters with size traits and features."""

    def __init__(self, size: str, features: list[str]) -> None:
        ...

    @property
    def size(self) -> str:
        ...

    @property
    def features(self) -> list[str]:
        ...


class Construct:
    """A construct with an ability profile that can be issued an order."""

    def __init__(self, ability_profile: object) -> None:
        ...

    @property
    def ability_profile(self) -> object:
        ...

    def issue_order(self) -> None:
        ...
