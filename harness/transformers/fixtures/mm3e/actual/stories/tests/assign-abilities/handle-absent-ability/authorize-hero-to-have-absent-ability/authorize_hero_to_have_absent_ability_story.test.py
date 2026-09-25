"""
Story: Authorize Hero to Have Absent Ability (scenario fidelity - tier-neutral).
Actor: GM
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: authorize_hero_to_have_absent_ability_test_helper.{tier}.py implements AuthorizeHeroToHaveAbsentAbilityHelper.
"""

from __future__ import annotations

from typing import Protocol


class AuthorizeHeroToHaveAbsentAbilityHelper(Protocol):
    ...


def create_authorize_hero_to_have_absent_ability_story(h: "AuthorizeHeroToHaveAbsentAbilityHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
