"""
Story: Build Utility Belt Array (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: build_utility_belt_array_test_helper.{tier}.py implements BuildUtilityBeltArrayHelper.
"""

from __future__ import annotations

from typing import Protocol


class BuildUtilityBeltArrayHelper(Protocol):
    ...


def create_build_utility_belt_array_story(h: "BuildUtilityBeltArrayHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
