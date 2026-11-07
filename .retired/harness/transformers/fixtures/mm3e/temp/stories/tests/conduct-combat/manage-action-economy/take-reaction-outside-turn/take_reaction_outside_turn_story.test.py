"""
Story: Take Reaction Outside Turn (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: take_reaction_outside_turn_test_helper.{tier}.py implements TakeReactionOutsideTurnHelper.
"""

from __future__ import annotations

from typing import Protocol


class TakeReactionOutsideTurnHelper(Protocol):
    ...


def create_take_reaction_outside_turn_story(h: "TakeReactionOutsideTurnHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
