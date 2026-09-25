"""
Story: Approve Completed Hero for Play (scenario fidelity - tier-neutral).
Actor: GM
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: approve_completed_hero_for_play_test_helper.{tier}.py implements ApproveCompletedHeroForPlayHelper.
"""

from __future__ import annotations

from typing import Protocol


class ApproveCompletedHeroForPlayHelper(Protocol):
    ...


def create_approve_completed_hero_for_play_story(h: "ApproveCompletedHeroForPlayHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
