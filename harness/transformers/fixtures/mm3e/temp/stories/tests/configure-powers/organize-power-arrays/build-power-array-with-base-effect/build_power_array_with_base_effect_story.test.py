"""
Story: Build Power Array with Base Effect (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: build_power_array_with_base_effect_test_helper.{tier}.py implements BuildPowerArrayWithBaseEffectHelper.
"""

from __future__ import annotations

from typing import Protocol


class BuildPowerArrayWithBaseEffectHelper(Protocol):
    ...


def create_build_power_array_with_base_effect_story(h: "BuildPowerArrayWithBaseEffectHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
