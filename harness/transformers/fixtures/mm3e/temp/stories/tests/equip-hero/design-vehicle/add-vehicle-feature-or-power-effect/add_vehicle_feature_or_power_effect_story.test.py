"""
Story: Add Vehicle Feature or Power Effect (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: add_vehicle_feature_or_power_effect_test_helper.{tier}.py implements AddVehicleFeatureOrPowerEffectHelper.
"""

from __future__ import annotations

from typing import Protocol


class AddVehicleFeatureOrPowerEffectHelper(Protocol):
    ...


def create_add_vehicle_feature_or_power_effect_story(h: "AddVehicleFeatureOrPowerEffectHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
