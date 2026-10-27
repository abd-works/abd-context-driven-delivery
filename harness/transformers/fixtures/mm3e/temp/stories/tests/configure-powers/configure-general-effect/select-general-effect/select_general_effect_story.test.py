"""
Story: Select General Effect (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: select_general_effect_test_helper.{tier}.py implements SelectGeneralEffectHelper.
"""

from __future__ import annotations

from typing import Protocol


class SelectGeneralEffectHelper(Protocol):
    ...


def create_select_general_effect_story(h: "SelectGeneralEffectHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
