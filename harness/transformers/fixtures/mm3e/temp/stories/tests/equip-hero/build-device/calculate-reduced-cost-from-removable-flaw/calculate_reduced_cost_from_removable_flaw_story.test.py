"""
Story: Calculate Reduced Cost from Removable Flaw (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: calculate_reduced_cost_from_removable_flaw_test_helper.{tier}.py implements CalculateReducedCostFromRemovableFlawHelper.
"""

from __future__ import annotations

from typing import Protocol


class CalculateReducedCostFromRemovableFlawHelper(Protocol):
    ...


def create_calculate_reduced_cost_from_removable_flaw_story(h: "CalculateReducedCostFromRemovableFlawHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
