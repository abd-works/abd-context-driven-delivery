"""
Story: Apply Ranked Attack Bonus to Close or Ranged Attack Check (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: apply_ranked_attack_bonus_to_close_or_ranged_attack_check_test_helper.{tier}.py implements ApplyRankedAttackBonusToCloseOrRangedAttackCheckHelper.
"""

from __future__ import annotations

from typing import Protocol


class ApplyRankedAttackBonusToCloseOrRangedAttackCheckHelper(Protocol):
    ...


def create_apply_ranked_attack_bonus_to_close_or_ranged_attack_check_story(h: "ApplyRankedAttackBonusToCloseOrRangedAttackCheckHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
