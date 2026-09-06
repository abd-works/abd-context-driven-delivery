"""Dice rolling — single die, pools, advantage/disadvantage, NdX+Y expressions."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from enum import Enum


class RollMode(str, Enum):
    NORMAL = "normal"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"


@dataclass(frozen=True)
class DieRoll:
    sides: int
    value: int

    def __post_init__(self) -> None:
        if self.sides < 1:
            raise ValueError("sides must be at least 1")
        if not 1 <= self.value <= self.sides:
            raise ValueError(f"value {self.value} out of range for d{self.sides}")


@dataclass(frozen=True)
class RollOutcome:
    rolls: tuple[DieRoll, ...]
    modifier: int
    mode: RollMode

    @property
    def selected(self) -> DieRoll:
        if not self.rolls:
            raise ValueError("no rolls")
        if self.mode is RollMode.ADVANTAGE:
            return max(self.rolls, key=lambda r: r.value)
        if self.mode is RollMode.DISADVANTAGE:
            return min(self.rolls, key=lambda r: r.value)
        return self.rolls[0]

    @property
    def total(self) -> int:
        return self.selected.value + self.modifier

    @property
    def natural_20(self) -> bool:
        return self.selected.sides == 20 and self.selected.value == 20

    @property
    def natural_1(self) -> bool:
        return self.selected.sides == 20 and self.selected.value == 1


_EXPRESSION = re.compile(
    r"^\s*(?:(?P<count>\d+)d(?P<sides>\d+)|d(?P<sides_only>\d+))"
    r"(?:(?P<sign>[+-])(?P<mod>\d+))?\s*$",
    re.IGNORECASE,
)


def roll(
    sides: int,
    *,
    count: int = 1,
    modifier: int = 0,
    mode: RollMode = RollMode.NORMAL,
    rng: random.Random | None = None,
) -> RollOutcome:
    """Roll ``count`` dice with ``sides`` faces, applying advantage/disadvantage on d20 checks."""
    if sides < 1:
        raise ValueError("sides must be at least 1")
    if count < 1:
        raise ValueError("count must be at least 1")

    source = rng or random
    d20_modes = {RollMode.ADVANTAGE, RollMode.DISADVANTAGE}
    if sides == 20 and mode in d20_modes:
        rolls = tuple(DieRoll(20, source.randint(1, 20)) for _ in range(2))
    else:
        rolls = tuple(DieRoll(sides, source.randint(1, sides)) for _ in range(count))

    return RollOutcome(rolls=rolls, modifier=modifier, mode=mode)


def roll_expression(expression: str, *, rng: random.Random | None = None) -> RollOutcome:
    """Parse and roll a simple expression like ``2d6+3``, ``d20``, or ``1d8-1``."""
    match = _EXPRESSION.match(expression)
    if not match:
        raise ValueError(f"unsupported expression: {expression!r}")

    count = int(match.group("count") or 1)
    sides = int(match.group("sides") or match.group("sides_only"))
    modifier = 0
    if match.group("mod"):
        sign = 1 if match.group("sign") == "+" else -1
        modifier = sign * int(match.group("mod"))

    return roll(sides, count=count, modifier=modifier, rng=rng)


def roll_pool(
    sides: int,
    count: int,
    *,
    keep: str = "sum",
    modifier: int = 0,
    rng: random.Random | None = None,
) -> int:
    """Roll many dice and keep highest, lowest, or sum (e.g. fireball 8d6)."""
    outcome = roll(sides, count=count, modifier=0, rng=rng)
    values = [die.value for die in outcome.rolls]
    if keep == "highest":
        base = max(values)
    elif keep == "lowest":
        base = min(values)
    elif keep == "sum":
        base = sum(values)
    else:
        raise ValueError("keep must be 'sum', 'highest', or 'lowest'")
    return base + modifier
