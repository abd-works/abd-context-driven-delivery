"""Player characters and NPCs — HP, AC, proficiency, saves, and checks."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum

from sandbox.dnd.abilities import Ability, AbilityScores
from sandbox.dnd.dice import RollMode, RollOutcome, roll
from sandbox.dnd.skills import Skill, skill_modifier


class ClassName(str, Enum):
    BARBARIAN = "barbarian"
    BARD = "bard"
    CLERIC = "cleric"
    DRUID = "druid"
    FIGHTER = "fighter"
    MONK = "monk"
    PALADIN = "paladin"
    RANGER = "ranger"
    ROGUE = "rogue"
    SORCERER = "sorcerer"
    WARLOCK = "warlock"
    WIZARD = "wizard"


@dataclass(frozen=True)
class Proficiency:
    saving_throws: frozenset[Ability] = frozenset()
    skills: frozenset[Skill] = frozenset()
    expertise: frozenset[Skill] = frozenset()


def proficiency_bonus(level: int) -> int:
    if level < 1 or level > 20:
        raise ValueError("level must be 1–20")
    return 2 + (level - 1) // 4


@dataclass
class Character:
    name: str
    level: int = 1
    character_class: ClassName = ClassName.FIGHTER
    abilities: AbilityScores = field(default_factory=AbilityScores)
    proficiency: Proficiency = field(default_factory=Proficiency)
    max_hp: int = 10
    current_hp: int = 10
    armor_class: int = 10
    temporary_hp: int = 0

    def __post_init__(self) -> None:
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
        if self.current_hp < 0:
            raise ValueError("current_hp cannot be negative")

    @property
    def prof_bonus(self) -> int:
        return proficiency_bonus(self.level)

    @property
    def is_conscious(self) -> bool:
        return self.current_hp > 0

    @property
    def is_stable_at_zero(self) -> bool:
        return self.current_hp == 0

    def ability_check(
        self,
        ability: Ability,
        dc: int,
        *,
        mode: RollMode = RollMode.NORMAL,
        rng: random.Random | None = None,
    ) -> tuple[RollOutcome, bool]:
        modifier = self.abilities.modifier(ability)
        outcome = roll(20, modifier=modifier, mode=mode, rng=rng)
        return outcome, outcome.total >= dc

    def skill_check(
        self,
        skill: Skill,
        dc: int,
        *,
        mode: RollMode = RollMode.NORMAL,
        rng: random.Random | None = None,
    ) -> tuple[RollOutcome, bool]:
        proficient = skill in self.proficiency.skills
        expert = skill in self.proficiency.expertise
        modifier = skill_modifier(
            skill,
            self.abilities,
            proficiency_bonus=self.prof_bonus,
            proficient=proficient,
            expertise=expert,
        )
        outcome = roll(20, modifier=modifier, mode=mode, rng=rng)
        return outcome, outcome.total >= dc

    def saving_throw(
        self,
        ability: Ability,
        dc: int,
        *,
        mode: RollMode = RollMode.NORMAL,
        rng: random.Random | None = None,
    ) -> tuple[RollOutcome, bool]:
        modifier = self.abilities.modifier(ability)
        if ability in self.proficiency.saving_throws:
            modifier += self.prof_bonus
        outcome = roll(20, modifier=modifier, mode=mode, rng=rng)
        return outcome, outcome.total >= dc

    def apply_damage(self, amount: int) -> int:
        """Apply damage; temp HP absorbs first. Returns overflow damage absorbed by temp HP."""
        if amount < 0:
            raise ValueError("damage must be non-negative")
        remaining = amount
        if self.temporary_hp > 0:
            absorbed = min(self.temporary_hp, remaining)
            self.temporary_hp -= absorbed
            remaining -= absorbed
        self.current_hp = max(0, self.current_hp - remaining)
        return amount

    def heal(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("heal amount must be non-negative")
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def add_temporary_hp(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("temporary hp must be non-negative")
        self.temporary_hp = max(self.temporary_hp, amount)
