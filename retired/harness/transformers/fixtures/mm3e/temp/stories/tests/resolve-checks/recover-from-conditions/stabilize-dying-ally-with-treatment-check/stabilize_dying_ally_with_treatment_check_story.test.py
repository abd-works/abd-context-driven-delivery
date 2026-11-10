"""
Story: Stabilize Dying Ally with Treatment Check (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: stabilize_dying_ally_with_treatment_check_test_helper.{tier}.py implements StabilizeDyingAllyWithTreatmentCheckHelper.
"""

from __future__ import annotations

from typing import Protocol


class StabilizeDyingAllyWithTreatmentCheckHelper(Protocol):
    ...


def create_stabilize_dying_ally_with_treatment_check_story(h: "StabilizeDyingAllyWithTreatmentCheckHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_treatment_check_can_stabilize_the_ally() -> None:
        """SCENARIO: treatment check can stabilize the ally"""
    tests['test_treatment_check_can_stabilize_the_ally'] = test_treatment_check_can_stabilize_the_ally

    return tests
