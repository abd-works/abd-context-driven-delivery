"""
Story: Validate Minimum Complication Requirement (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: validate_minimum_complication_requirement_test_helper.{tier}.py implements ValidateMinimumComplicationRequirementHelper.
"""

from __future__ import annotations

from typing import Protocol


class ValidateMinimumComplicationRequirementHelper(Protocol):
    ...


def create_validate_minimum_complication_requirement_story(h: "ValidateMinimumComplicationRequirementHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_missing_motivation_fails() -> None:
        """SCENARIO: missing motivation fails"""
    tests['test_missing_motivation_fails'] = test_missing_motivation_fails

    return tests
