"""
Story: Allocate Equipment Points to Gear (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: allocate_equipment_points_to_gear_test_helper.{tier}.py implements AllocateEquipmentPointsToGearHelper.
"""

from __future__ import annotations

from typing import Protocol


class AllocateEquipmentPointsToGearHelper(Protocol):
    ...


def create_allocate_equipment_points_to_gear_story(h: "AllocateEquipmentPointsToGearHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
