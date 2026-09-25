"""
Story: Enforce Equipment Bonus Non-stacking (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: enforce_equipment_bonus_non_stacking_test_helper.{tier}.py implements EnforceEquipmentBonusNonStackingHelper.
"""

from __future__ import annotations

from typing import Protocol


class EnforceEquipmentBonusNonStackingHelper(Protocol):
    ...


def create_enforce_equipment_bonus_non_stacking_story(h: "EnforceEquipmentBonusNonStackingHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
