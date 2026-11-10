"""
Story: Apply Initiative Bonus from Improved Initiative (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: apply_initiative_bonus_from_improved_initiative_test_helper.{tier}.py implements ApplyInitiativeBonusFromImprovedInitiativeHelper.
"""

from __future__ import annotations

from typing import Protocol


class ApplyInitiativeBonusFromImprovedInitiativeHelper(Protocol):
    ...


def create_apply_initiative_bonus_from_improved_initiative_story(h: "ApplyInitiativeBonusFromImprovedInitiativeHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
