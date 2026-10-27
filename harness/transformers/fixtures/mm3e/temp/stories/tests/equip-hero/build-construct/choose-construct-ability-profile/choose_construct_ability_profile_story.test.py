"""
Story: Choose Construct Ability Profile (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: choose_construct_ability_profile_test_helper.{tier}.py implements ChooseConstructAbilityProfileHelper.
"""

from __future__ import annotations

from typing import Protocol


class ChooseConstructAbilityProfileHelper(Protocol):
    ...


def create_choose_construct_ability_profile_story(h: "ChooseConstructAbilityProfileHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
