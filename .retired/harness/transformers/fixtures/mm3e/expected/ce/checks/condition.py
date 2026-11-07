"""
"""
from __future__ import annotations


class Condition:
    """Names a game modifier and the more severe conditions that supersede it."""

    def __init__(self, name: str, game_modifier: int) -> None:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def game_modifier(self) -> int:
        ...

    @property
    def supersedes(self) -> list[Condition]:
        ...

    @property
    def superseded_by(self) -> list[Condition]:
        ...

    @property
    def constituents(self) -> list[Condition]:
        ...


class ImposedCondition:
    """A condition applied from a source, active or parked until a blocker ends."""

    # only active conditions apply modifiers

    def __init__(self, condition: Condition, source: object, active: bool) -> None:
        ...

    @property
    def condition(self) -> Condition:
        ...

    @property
    def source(self) -> object:
        ...

    @property
    def active(self) -> bool:
        ...


class ImposedConditions:
    """Applies, supersedes, and removes conditions on a character by source."""

    # same-source supersession removes the lesser; a different-source lesser stays parked inactive
    # only active conditions apply modifiers

    def apply(self, condition: Condition, source: object) -> ImposedCondition:
        ...

    def supersede(self) -> None:
        ...

    def remove_when_source_ends(self, source: object) -> None:
        ...

    @property
    def active_conditions(self) -> list[ImposedCondition]:
        ...
