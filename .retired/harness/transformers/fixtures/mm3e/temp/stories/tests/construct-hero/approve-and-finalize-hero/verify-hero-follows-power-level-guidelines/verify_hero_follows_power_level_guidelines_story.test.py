"""
Story: Verify Hero Follows Power Level Guidelines (scenario fidelity - tier-neutral).
Actor: GM
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: verify_hero_follows_power_level_guidelines_test_helper.{tier}.py implements VerifyHeroFollowsPowerLevelGuidelinesHelper.
"""

from __future__ import annotations

from typing import Protocol


class VerifyHeroFollowsPowerLevelGuidelinesHelper(Protocol):
    ...


def create_verify_hero_follows_power_level_guidelines_story(h: "VerifyHeroFollowsPowerLevelGuidelinesHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
