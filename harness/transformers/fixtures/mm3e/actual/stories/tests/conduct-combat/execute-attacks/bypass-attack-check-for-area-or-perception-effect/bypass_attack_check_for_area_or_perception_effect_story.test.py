"""
Story: Bypass Attack Check for Area or Perception Effect (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: bypass_attack_check_for_area_or_perception_effect_test_helper.{tier}.py implements BypassAttackCheckForAreaOrPerceptionEffectHelper.
"""

from __future__ import annotations

from typing import Protocol


class BypassAttackCheckForAreaOrPerceptionEffectHelper(Protocol):
    ...


def create_bypass_attack_check_for_area_or_perception_effect_story(h: "BypassAttackCheckForAreaOrPerceptionEffectHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
