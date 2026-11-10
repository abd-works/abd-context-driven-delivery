"""
Story: Remove Powers When Device Taken Away (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: remove_powers_when_device_taken_away_test_helper.{tier}.py implements RemovePowersWhenDeviceTakenAwayHelper.
"""

from __future__ import annotations

from typing import Protocol


class RemovePowersWhenDeviceTakenAwayHelper(Protocol):
    ...


def create_remove_powers_when_device_taken_away_story(h: "RemovePowersWhenDeviceTakenAwayHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
