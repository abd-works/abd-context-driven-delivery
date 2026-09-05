#!/usr/bin/env python3
"""Runnable walk-through of sandbox/dnd basics (deterministic RNG for demo)."""

from __future__ import annotations

import random

from sandbox.dnd.abilities import Ability, AbilityScores
from sandbox.dnd.character import Character, ClassName, Proficiency
from sandbox.dnd.combat import DamageRoll
from sandbox.dnd.dice import RollMode, roll, roll_expression
from sandbox.dnd.encounter import CombatEncounter
from sandbox.dnd.skills import Skill


def main() -> None:
    rng = random.Random(42)

    print("=== Dice ===")
    outcome = roll(20, modifier=5, mode=RollMode.ADVANTAGE, rng=rng)
    print(f"d20+5 with advantage: rolls={[r.value for r in outcome.rolls]} → {outcome.total}")
    print(f"2d6+3: {roll_expression('2d6+3', rng=rng).total}")

    print("\n=== Ability check ===")
    hero = Character(
        name="Aldric",
        level=3,
        character_class=ClassName.FIGHTER,
        abilities=AbilityScores(strength=16, dexterity=14, constitution=15),
        proficiency=Proficiency(
            saving_throws=frozenset({Ability.STRENGTH, Ability.CONSTITUTION}),
            skills=frozenset({Skill.ATHLETICS, Skill.PERCEPTION}),
        ),
        max_hp=28,
        current_hp=28,
        armor_class=18,
    )
    outcome, success = hero.skill_check(Skill.ATHLETICS, dc=15, rng=rng)
    print(f"Athletics DC 15: {outcome.total} → {'success' if success else 'fail'}")

    print("\n=== Saving throw ===")
    outcome, success = hero.saving_throw(Ability.DEXTERITY, dc=12, rng=rng)
    print(f"DEX save DC 12: {outcome.total} → {'success' if success else 'fail'}")

    print("\n=== Combat ===")
    goblin = Character(
        name="Goblin",
        level=1,
        abilities=AbilityScores(dexterity=14, constitution=10),
        max_hp=7,
        current_hp=7,
        armor_class=15,
    )
    encounter = CombatEncounter.start([hero, goblin], rng=rng)
    order = [r.character.name for r in encounter.initiative.rolls]
    print(f"Initiative: {order}")

    attacker = next(c for c in encounter.combatants if c.character.name == "Aldric")
    defender = next(c for c in encounter.combatants if c.character.name == "Goblin")
    result = encounter.attack(
        attacker,
        defender,
        damage=DamageRoll(1, 8, modifier=3),
        rng=rng,
    )
    print(f"Longsword vs goblin: {result.outcome.value}, damage={result.damage}, goblin HP={goblin.current_hp}")


if __name__ == "__main__":
    main()
