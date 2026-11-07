"""
Story: Apply Favored Environment Circumstance Bonus (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: apply_favored_environment_circumstance_bonus_test_helper.{tier}.py implements ApplyFavoredEnvironmentCircumstanceBonusHelper.
"""

from __future__ import annotations

from typing import Protocol


class ApplyFavoredEnvironmentCircumstanceBonusHelper(Protocol):
    ...


def create_apply_favored_environment_circumstance_bonus_story(h: "ApplyFavoredEnvironmentCircumstanceBonusHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
