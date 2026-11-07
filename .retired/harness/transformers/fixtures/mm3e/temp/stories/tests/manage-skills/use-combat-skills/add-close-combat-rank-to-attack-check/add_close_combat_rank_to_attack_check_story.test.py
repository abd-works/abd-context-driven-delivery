"""
Story: Add Close Combat Rank to Attack Check (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: add_close_combat_rank_to_attack_check_test_helper.{tier}.py implements AddCloseCombatRankToAttackCheckHelper.
"""

from __future__ import annotations

from typing import Protocol


class AddCloseCombatRankToAttackCheckHelper(Protocol):
    ...


def create_add_close_combat_rank_to_attack_check_story(h: "AddCloseCombatRankToAttackCheckHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
