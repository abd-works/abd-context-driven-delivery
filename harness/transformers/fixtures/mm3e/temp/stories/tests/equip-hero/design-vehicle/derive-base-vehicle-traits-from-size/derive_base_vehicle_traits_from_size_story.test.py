"""
Story: Derive Base Vehicle Traits from Size (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: derive_base_vehicle_traits_from_size_test_helper.{tier}.py implements DeriveBaseVehicleTraitsFromSizeHelper.
"""

from __future__ import annotations

from typing import Protocol


class DeriveBaseVehicleTraitsFromSizeHelper(Protocol):
    ...


def create_derive_base_vehicle_traits_from_size_story(h: "DeriveBaseVehicleTraitsFromSizeHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
