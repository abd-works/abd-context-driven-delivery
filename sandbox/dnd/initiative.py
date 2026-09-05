"""Initiative — turn order at the start of combat."""

from __future__ import annotations

import random
from dataclasses import dataclass

from sandbox.dnd.abilities import Ability
from sandbox.dnd.character import Character
from sandbox.dnd.dice import RollOutcome, roll


@dataclass(frozen=True)
class InitiativeRoll:
    character: Character
    outcome: RollOutcome

    @property
    def total(self) -> int:
        return self.outcome.total


@dataclass
class InitiativeOrder:
    rolls: list[InitiativeRoll]

    @classmethod
    def roll_for(cls, characters: list[Character], *, rng: random.Random | None = None) -> InitiativeOrder:
        entries = []
        for character in characters:
            modifier = character.abilities.modifier(Ability.DEXTERITY)
            outcome = roll(20, modifier=modifier, rng=rng)
            entries.append(InitiativeRoll(character, outcome))
        entries.sort(key=lambda entry: entry.total, reverse=True)
        return cls(entries)

    def __iter__(self):
        return iter(self.rolls)

    def current_turn(self, round_index: int) -> Character:
        if not self.rolls:
            raise ValueError("no combatants")
        return self.rolls[round_index % len(self.rolls)].character
