"""
Story: Switch Active Effect in Array as Free Action (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: switch_active_effect_in_array_as_free_action_test_helper.{tier}.py implements SwitchActiveEffectInArrayAsFreeActionHelper.
"""

from __future__ import annotations

from typing import Protocol


class SwitchActiveEffectInArrayAsFreeActionHelper(Protocol):
    ...


def create_switch_active_effect_in_array_as_free_action_story(h: "SwitchActiveEffectInArrayAsFreeActionHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
