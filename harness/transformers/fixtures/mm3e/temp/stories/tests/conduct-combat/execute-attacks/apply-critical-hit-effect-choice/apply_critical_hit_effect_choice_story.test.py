"""
Story: Apply Critical Hit Effect Choice (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: apply_critical_hit_effect_choice_test_helper.{tier}.py implements ApplyCriticalHitEffectChoiceHelper.
"""

from __future__ import annotations

from typing import Protocol


class ApplyCriticalHitEffectChoiceHelper(Protocol):
    ...


def create_apply_critical_hit_effect_choice_story(h: "ApplyCriticalHitEffectChoiceHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
