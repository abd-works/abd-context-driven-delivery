"""
Story: Select Control Effect (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: select_control_effect_test_helper.{tier}.py implements SelectControlEffectHelper.
"""

from __future__ import annotations

from typing import Protocol


class SelectControlEffectHelper(Protocol):
    ...


def create_select_control_effect_story(h: "SelectControlEffectHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
