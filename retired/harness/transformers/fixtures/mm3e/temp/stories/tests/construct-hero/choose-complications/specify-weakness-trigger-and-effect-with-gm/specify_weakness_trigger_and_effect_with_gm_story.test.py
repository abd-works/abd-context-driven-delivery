"""
Story: Specify Weakness Trigger and Effect with GM (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: specify_weakness_trigger_and_effect_with_gm_test_helper.{tier}.py implements SpecifyWeaknessTriggerAndEffectWithGmHelper.
"""

from __future__ import annotations

from typing import Protocol


class SpecifyWeaknessTriggerAndEffectWithGmHelper(Protocol):
    ...


def create_specify_weakness_trigger_and_effect_with_gm_story(h: "SpecifyWeaknessTriggerAndEffectWithGmHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
