"""
Story: Set Series Power Level (scenario fidelity - tier-neutral).
Actor: GM
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: set_series_power_level_test_helper.{tier}.py implements SetSeriesPowerLevelHelper.
"""

from __future__ import annotations

from typing import Protocol


class SetSeriesPowerLevelHelper(Protocol):
    ...


def create_set_series_power_level_story(h: "SetSeriesPowerLevelHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_series_pl_caps_every_player_hero() -> None:
        """SCENARIO: series pl caps every player hero"""
    tests['test_series_pl_caps_every_player_hero'] = test_series_pl_caps_every_player_hero

    def test_missing_pl_blocks_construction() -> None:
        """SCENARIO: missing pl blocks construction"""
    tests['test_missing_pl_blocks_construction'] = test_missing_pl_blocks_construction

    return tests
