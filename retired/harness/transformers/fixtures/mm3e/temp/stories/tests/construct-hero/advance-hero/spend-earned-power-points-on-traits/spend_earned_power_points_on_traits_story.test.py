"""
Story: Spend Earned Power Points on Traits (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: spend_earned_power_points_on_traits_test_helper.{tier}.py implements SpendEarnedPowerPointsOnTraitsHelper.
"""

from __future__ import annotations

from typing import Protocol


class SpendEarnedPowerPointsOnTraitsHelper(Protocol):
    ...


def create_spend_earned_power_points_on_traits_story(h: "SpendEarnedPowerPointsOnTraitsHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
