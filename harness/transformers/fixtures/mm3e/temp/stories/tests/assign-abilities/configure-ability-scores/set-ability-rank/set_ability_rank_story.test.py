"""
Story: Set Ability Rank (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: set_ability_rank_test_helper.{tier}.py implements SetAbilityRankHelper.
"""

from __future__ import annotations

from typing import Protocol


class SetAbilityRankHelper(Protocol):
    ...


def create_set_ability_rank_story(h: "SetAbilityRankHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_raise_costs_two_points() -> None:
        """SCENARIO: raise costs two points"""
    tests['test_raise_costs_two_points'] = test_raise_costs_two_points

    def test_reduce_below_zero_refunds_two_per_rank() -> None:
        """SCENARIO: reduce below zero refunds two per rank"""
    tests['test_reduce_below_zero_refunds_two_per_rank'] = test_reduce_below_zero_refunds_two_per_rank

    def test_voluntary_floor_is_minus_five() -> None:
        """SCENARIO: voluntary floor is minus five"""
    tests['test_voluntary_floor_is_minus_five'] = test_voluntary_floor_is_minus_five

    def test_below_minus_five_is_rejected() -> None:
        """SCENARIO: below minus five is rejected"""
    tests['test_below_minus_five_is_rejected'] = test_below_minus_five_is_rejected

    return tests
