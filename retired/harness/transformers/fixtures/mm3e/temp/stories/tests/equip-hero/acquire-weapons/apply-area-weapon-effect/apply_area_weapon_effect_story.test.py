"""
Story: Apply Area Weapon Effect (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: apply_area_weapon_effect_test_helper.{tier}.py implements ApplyAreaWeaponEffectHelper.
"""

from __future__ import annotations

from typing import Protocol


class ApplyAreaWeaponEffectHelper(Protocol):
    ...


def create_apply_area_weapon_effect_story(h: "ApplyAreaWeaponEffectHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
