"""
Story: Aim for Attack Bonus (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: aim_for_attack_bonus_test_helper.{tier}.py implements AimForAttackBonusHelper.
"""

from __future__ import annotations

from typing import Protocol


class AimForAttackBonusHelper(Protocol):
    ...


def create_aim_for_attack_bonus_story(h: "AimForAttackBonusHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
