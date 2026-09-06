"""Conditions — common combat conditions and their mechanical hooks."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from sandbox.dnd.dice import RollMode


class Condition(str, Enum):
    BLINDED = "blinded"
    CHARMED = "charmed"
    DEAFENED = "deafened"
    FRIGHTENED = "frightened"
    GRAPPLED = "grappled"
    INCAPACITATED = "incapacitated"
    INVISIBLE = "invisible"
    PARALYZED = "paralyzed"
    PETRIFIED = "petrified"
    POISONED = "poisoned"
    PRONE = "prone"
    RESTRAINED = "restrained"
    STUNNED = "stunned"
    UNCONSCIOUS = "unconscious"
    EXHAUSTION = "exhaustion"


@dataclass
class ConditionSet:
    active: set[Condition] = field(default_factory=set)

    def add(self, condition: Condition) -> None:
        self.active.add(condition)

    def remove(self, condition: Condition) -> None:
        self.active.discard(condition)

    def has(self, condition: Condition) -> bool:
        return condition in self.active

    @property
    def incapacitated(self) -> bool:
        return bool(
            self.active
            & {
                Condition.INCAPACITATED,
                Condition.PARALYZED,
                Condition.PETRIFIED,
                Condition.STUNNED,
                Condition.UNCONSCIOUS,
            }
        )

    @property
    def auto_fail_strength_dex_saves(self) -> bool:
        return Condition.PARALYZED in self.active or Condition.PETRIFIED in self.active

    @property
    def grants_advantage_to_attacks(self) -> bool:
        return bool(
            self.active
            & {
                Condition.BLINDED,
                Condition.PARALYZED,
                Condition.PETRIFIED,
                Condition.PRONE,
                Condition.RESTRAINED,
                Condition.STUNNED,
                Condition.UNCONSCIOUS,
            }
        )

    @property
    def grants_disadvantage_on_attacks(self) -> bool:
        if Condition.INVISIBLE in self.active:
            return False
        return Condition.POISONED in self.active or Condition.FRIGHTENED in self.active

    @property
    def attack_roll_mode_modifier(self) -> RollMode | None:
        """Attacks against this creature — advantage if prone (melee), restrained, etc."""
        if self.grants_advantage_to_attacks:
            return RollMode.ADVANTAGE
        return None

    def saving_throw_mode(self, ability_name: str) -> RollMode:
        if self.auto_fail_strength_dex_saves and ability_name in {"strength", "dexterity"}:
            return RollMode.DISADVANTAGE
        if Condition.STUNNED in self.active:
            return RollMode.DISADVANTAGE
        return RollMode.NORMAL
