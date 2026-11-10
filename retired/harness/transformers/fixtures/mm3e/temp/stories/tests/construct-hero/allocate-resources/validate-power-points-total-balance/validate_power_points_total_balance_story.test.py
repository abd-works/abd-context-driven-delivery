"""
Story: Validate Power Points Total Balance (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: validate_power_points_total_balance_test_helper.{tier}.py implements ValidatePowerPointsTotalBalanceHelper.
"""

from __future__ import annotations

from typing import Protocol


class ValidatePowerPointsTotalBalanceHelper(Protocol):
    ...


def create_validate_power_points_total_balance_story(h: "ValidatePowerPointsTotalBalanceHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_spent_equals_starting_budget() -> None:
        """SCENARIO: spent equals starting budget"""
    tests['test_spent_equals_starting_budget'] = test_spent_equals_starting_budget

    def test_overspend_is_rejected() -> None:
        """SCENARIO: overspend is rejected"""
    tests['test_overspend_is_rejected'] = test_overspend_is_rejected

    return tests
