"""
Story: Inspire Allies with Hero Point (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: inspire_allies_with_hero_point_test_helper.{tier}.py implements InspireAlliesWithHeroPointHelper.
"""

from __future__ import annotations

from typing import Protocol


class InspireAlliesWithHeroPointHelper(Protocol):
    ...


def create_inspire_allies_with_hero_point_story(h: "InspireAlliesWithHeroPointHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
