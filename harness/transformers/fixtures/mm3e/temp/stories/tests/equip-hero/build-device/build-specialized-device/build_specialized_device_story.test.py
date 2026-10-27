"""
Story: Build Specialized Device (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: build_specialized_device_test_helper.{tier}.py implements BuildSpecializedDeviceHelper.
"""

from __future__ import annotations

from typing import Protocol


class BuildSpecializedDeviceHelper(Protocol):
    ...


def create_build_specialized_device_story(h: "BuildSpecializedDeviceHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
