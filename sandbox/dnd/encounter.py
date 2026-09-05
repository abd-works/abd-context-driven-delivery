"""Combat encounter — initiative, turns, and basic attack resolution."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from sandbox.dnd.character import Character
from sandbox.dnd.combat import AttackResult, DamageRoll, resolve_attack
from sandbox.dnd.conditions import ConditionSet
from sandbox.dnd.initiative import InitiativeOrder


@dataclass
class Combatant:
    character: Character
    conditions: ConditionSet = field(default_factory=ConditionSet)

    @property
    def can_act(self) -> bool:
        return self.character.is_conscious and not self.conditions.incapacitated


@dataclass
class CombatEncounter:
    combatants: list[Combatant]
    initiative: InitiativeOrder
    turn_index: int = 0
    round_number: int = 1

    @classmethod
    def start(cls, characters: list[Character], *, rng: random.Random | None = None) -> CombatEncounter:
        order = InitiativeOrder.roll_for(characters, rng=rng)
        return cls(
            combatants=[Combatant(character) for character in characters],
            initiative=order,
        )

    @property
    def active_combatant(self) -> Combatant:
        name = self.initiative.current_turn(self.turn_index).name
        for combatant in self.combatants:
            if combatant.character.name == name:
                return combatant
        raise RuntimeError(f"combatant {name!r} missing from encounter")

    def advance_turn(self) -> None:
        self.turn_index += 1
        if self.turn_index > 0 and self.turn_index % len(self.initiative.rolls) == 0:
            self.round_number += 1

    def attack(
        self,
        attacker: Combatant,
        defender: Combatant,
        *,
        damage: DamageRoll,
        attack_bonus: int | None = None,
        rng: random.Random | None = None,
    ) -> AttackResult:
        if not attacker.can_act:
            raise ValueError(f"{attacker.character.name} cannot act")
        return resolve_attack(
            attacker.character,
            defender.character,
            damage=damage,
            attack_bonus=attack_bonus,
            rng=rng,
        )

    def living_combatants(self) -> list[Combatant]:
        return [c for c in self.combatants if c.character.is_conscious]

    def is_over(self) -> bool:
        return len(self.living_combatants()) <= 1
