"""
Story: Acquire Equipment Advantage Ranks (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: acquire_equipment_advantage_ranks_test_helper.{tier}.py implements AcquireEquipmentAdvantageRanksHelper.
"""

from __future__ import annotations

from typing import Protocol


class AcquireEquipmentAdvantageRanksHelper(Protocol):
    ...


def create_acquire_equipment_advantage_ranks_story(h: "AcquireEquipmentAdvantageRanksHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_rank_1_grants_five_equipment_points() -> None:
        """SCENARIO: rank 1 grants five equipment points"""
    tests['test_rank_1_grants_five_equipment_points'] = test_rank_1_grants_five_equipment_points

    def test_zero_ranks_grant_no_points() -> None:
        """SCENARIO: zero ranks grant no points"""
    tests['test_zero_ranks_grant_no_points'] = test_zero_ranks_grant_no_points

    return tests
