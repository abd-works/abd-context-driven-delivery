"""Ability scores and modifiers — the six D&D abilities."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Ability(str, Enum):
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"


def ability_modifier(score: int) -> int:
    """Standard 5e modifier: (score - 10) // 2."""
    if score < 1:
        raise ValueError("ability score must be at least 1")
    return (score - 10) // 2


@dataclass
class AbilityScores:
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    def score(self, ability: Ability) -> int:
        return getattr(self, ability.value)

    def modifier(self, ability: Ability) -> int:
        return ability_modifier(self.score(ability))
