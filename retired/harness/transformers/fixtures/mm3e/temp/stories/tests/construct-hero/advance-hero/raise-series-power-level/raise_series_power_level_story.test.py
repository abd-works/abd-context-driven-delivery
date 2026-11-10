"""
Story: Raise Series Power Level (scenario fidelity - tier-neutral).
Actor: GM
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: raise_series_power_level_test_helper.{tier}.py implements RaiseSeriesPowerLevelHelper.
"""

from __future__ import annotations

from typing import Protocol


class RaiseSeriesPowerLevelHelper(Protocol):
    ...


def create_raise_series_power_level_story(h: "RaiseSeriesPowerLevelHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
