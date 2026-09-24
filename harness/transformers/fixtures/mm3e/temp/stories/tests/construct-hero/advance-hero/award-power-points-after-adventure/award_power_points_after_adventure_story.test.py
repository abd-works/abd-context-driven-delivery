"""
Story: Award Power Points after Adventure (scenario fidelity - tier-neutral).
Actor: GM
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: award_power_points_after_adventure_test_helper.{tier}.py implements AwardPowerPointsAfterAdventureHelper.
"""

from __future__ import annotations

from typing import Protocol


class AwardPowerPointsAfterAdventureHelper(Protocol):
    ...


def create_award_power_points_after_adventure_story(h: "AwardPowerPointsAfterAdventureHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
