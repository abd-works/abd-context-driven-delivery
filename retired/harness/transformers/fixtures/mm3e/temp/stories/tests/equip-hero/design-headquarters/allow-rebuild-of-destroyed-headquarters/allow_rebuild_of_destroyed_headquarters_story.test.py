"""
Story: Allow Rebuild of Destroyed Headquarters (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: allow_rebuild_of_destroyed_headquarters_test_helper.{tier}.py implements AllowRebuildOfDestroyedHeadquartersHelper.
"""

from __future__ import annotations

from typing import Protocol


class AllowRebuildOfDestroyedHeadquartersHelper(Protocol):
    ...


def create_allow_rebuild_of_destroyed_headquarters_story(h: "AllowRebuildOfDestroyedHeadquartersHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
