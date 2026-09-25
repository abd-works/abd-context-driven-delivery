"""
Story: Take Move Action on Turn (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: take_move_action_on_turn_test_helper.{tier}.py implements TakeMoveActionOnTurnHelper.
"""

from __future__ import annotations

from typing import Protocol


class TakeMoveActionOnTurnHelper(Protocol):
    ...


def create_take_move_action_on_turn_story(h: "TakeMoveActionOnTurnHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
