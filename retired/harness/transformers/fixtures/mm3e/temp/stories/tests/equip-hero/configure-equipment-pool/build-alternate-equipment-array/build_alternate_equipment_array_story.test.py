"""
Story: Build Alternate Equipment Array (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: build_alternate_equipment_array_test_helper.{tier}.py implements BuildAlternateEquipmentArrayHelper.
"""

from __future__ import annotations

from typing import Protocol


class BuildAlternateEquipmentArrayHelper(Protocol):
    ...


def create_build_alternate_equipment_array_story(h: "BuildAlternateEquipmentArrayHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
