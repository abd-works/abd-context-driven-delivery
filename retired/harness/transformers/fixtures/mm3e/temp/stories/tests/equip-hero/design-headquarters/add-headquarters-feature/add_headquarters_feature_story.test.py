"""
Story: Add Headquarters Feature (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: add_headquarters_feature_test_helper.{tier}.py implements AddHeadquartersFeatureHelper.
"""

from __future__ import annotations

from typing import Protocol


class AddHeadquartersFeatureHelper(Protocol):
    ...


def create_add_headquarters_feature_story(h: "AddHeadquartersFeatureHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
