"""
Story: Take Free Action During Turn (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: take_free_action_during_turn_test_helper.{tier}.py implements TakeFreeActionDuringTurnHelper.
"""

from __future__ import annotations

from typing import Protocol


class TakeFreeActionDuringTurnHelper(Protocol):
    ...


def create_take_free_action_during_turn_story(h: "TakeFreeActionDuringTurnHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
