"""
Story: Derive Starting Power Points from Power Level (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: derive_starting_power_points_from_power_level_test_helper.{tier}.py implements DeriveStartingPowerPointsFromPowerLevelHelper.
"""

from __future__ import annotations

from typing import Protocol


class DeriveStartingPowerPointsFromPowerLevelHelper(Protocol):
    ...


def create_derive_starting_power_points_from_power_level_story(h: "DeriveStartingPowerPointsFromPowerLevelHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_table_default_is_pl_times_fifteen() -> None:
        """SCENARIO: table default is pl times fifteen"""
    tests['test_table_default_is_pl_times_fifteen'] = test_table_default_is_pl_times_fifteen

    def test_gm_adjustment_changes_budget_not_pl() -> None:
        """SCENARIO: gm adjustment changes budget not pl"""
    tests['test_gm_adjustment_changes_budget_not_pl'] = test_gm_adjustment_changes_budget_not_pl

    return tests
