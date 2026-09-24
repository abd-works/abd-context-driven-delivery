"""
Story: Add Ranged Combat Rank to Attack Check (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: add_ranged_combat_rank_to_attack_check_test_helper.{tier}.py implements AddRangedCombatRankToAttackCheckHelper.
"""

from __future__ import annotations

from typing import Protocol


class AddRangedCombatRankToAttackCheckHelper(Protocol):
    ...


def create_add_ranged_combat_rank_to_attack_check_story(h: "AddRangedCombatRankToAttackCheckHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
