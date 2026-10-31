"""
Story: Select Vehicle Size Category (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: select_vehicle_size_category_test_helper.{tier}.py implements SelectVehicleSizeCategoryHelper.
"""

from __future__ import annotations

from typing import Protocol


class SelectVehicleSizeCategoryHelper(Protocol):
    ...


def create_select_vehicle_size_category_story(h: "SelectVehicleSizeCategoryHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
