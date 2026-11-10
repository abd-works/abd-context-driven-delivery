"""
Story: Apply Inspiration Bonus Ignoring Power Level Cap (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: apply_inspiration_bonus_ignoring_power_level_cap_test_helper.{tier}.py implements ApplyInspirationBonusIgnoringPowerLevelCapHelper.
"""

from __future__ import annotations

from typing import Protocol


class ApplyInspirationBonusIgnoringPowerLevelCapHelper(Protocol):
    ...


def create_apply_inspiration_bonus_ignoring_power_level_cap_story(h: "ApplyInspirationBonusIgnoringPowerLevelCapHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
