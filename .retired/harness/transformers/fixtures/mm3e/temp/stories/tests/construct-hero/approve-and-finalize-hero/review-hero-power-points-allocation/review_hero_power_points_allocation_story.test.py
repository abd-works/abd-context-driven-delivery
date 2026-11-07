"""
Story: Review Hero Power Points Allocation (scenario fidelity - tier-neutral).
Actor: GM
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: review_hero_power_points_allocation_test_helper.{tier}.py implements ReviewHeroPowerPointsAllocationHelper.
"""

from __future__ import annotations

from typing import Protocol


class ReviewHeroPowerPointsAllocationHelper(Protocol):
    ...


def create_review_hero_power_points_allocation_story(h: "ReviewHeroPowerPointsAllocationHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
