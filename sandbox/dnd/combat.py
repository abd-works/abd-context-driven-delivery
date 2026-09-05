"""Combat — attacks, damage, and critical hits."""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

from sandbox.dnd.abilities import Ability
from sandbox.dnd.character import Character
from sandbox.dnd.dice import RollMode, RollOutcome, roll, roll_pool


class AttackOutcome(str, Enum):
    CRITICAL_HIT = "critical_hit"
    HIT = "hit"
    MISS = "miss"


@dataclass(frozen=True)
class AttackResult:
    outcome: AttackOutcome
    attack_roll: RollOutcome
    damage: int = 0


@dataclass(frozen=True)
class DamageRoll:
    dice_count: int
    die_sides: int
    modifier: int = 0

    def roll(self, *, critical: bool = False, rng: random.Random | None = None) -> int:
        count = self.dice_count * (2 if critical else 1)
        return roll_pool(self.die_sides, count, keep="sum", modifier=self.modifier, rng=rng)


def resolve_attack(
    attacker: Character,
    target: Character,
    *,
    damage: DamageRoll,
    attack_bonus: int | None = None,
    attack_ability: Ability = Ability.STRENGTH,
    mode: RollMode = RollMode.NORMAL,
    rng: random.Random | None = None,
) -> AttackResult:
    """Resolve an attack against AC — natural 1 misses, natural 20 doubles damage dice."""
    bonus = attack_bonus
    if bonus is None:
        bonus = attacker.abilities.modifier(attack_ability) + attacker.prof_bonus

    attack_roll = roll(20, modifier=bonus, mode=mode, rng=rng)

    if attack_roll.natural_1:
        return AttackResult(AttackOutcome.MISS, attack_roll)

    critical = attack_roll.natural_20
    hit = critical or attack_roll.total >= target.armor_class
    if not hit:
        return AttackResult(AttackOutcome.MISS, attack_roll)

    damage_total = damage.roll(critical=critical, rng=rng)
    target.apply_damage(damage_total)
    outcome = AttackOutcome.CRITICAL_HIT if critical else AttackOutcome.HIT
    return AttackResult(outcome, attack_roll, damage=damage_total)
