"""
Story: Add Wielder Strength to Melee Damage (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: add_wielder_strength_to_melee_damage_test_helper.{tier}.py implements AddWielderStrengthToMeleeDamageHelper.
"""

from __future__ import annotations

from typing import Protocol


class AddWielderStrengthToMeleeDamageHelper(Protocol):
    ...


def create_add_wielder_strength_to_melee_damage_story(h: "AddWielderStrengthToMeleeDamageHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
