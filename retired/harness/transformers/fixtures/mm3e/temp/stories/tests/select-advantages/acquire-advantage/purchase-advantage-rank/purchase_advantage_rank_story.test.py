"""
Story: Purchase Advantage Rank (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: purchase_advantage_rank_test_helper.{tier}.py implements PurchaseAdvantageRankHelper.
"""

from __future__ import annotations

from typing import Protocol


class PurchaseAdvantageRankHelper(Protocol):
    ...


def create_purchase_advantage_rank_story(h: "PurchaseAdvantageRankHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_ranked_advantage_costs_one_per_rank() -> None:
        """SCENARIO: ranked advantage costs one per rank"""
    tests['test_ranked_advantage_costs_one_per_rank'] = test_ranked_advantage_costs_one_per_rank

    def test_non_ranked_is_once_at_rank_1() -> None:
        """SCENARIO: non-ranked is once at rank 1"""
    tests['test_non_ranked_is_once_at_rank_1'] = test_non_ranked_is_once_at_rank_1

    return tests
