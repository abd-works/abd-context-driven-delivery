"""
Story: Exchange Standard Action for Additional Move Action (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: exchange_standard_action_for_additional_move_action_test_helper.{tier}.py implements ExchangeStandardActionForAdditionalMoveActionHelper.
"""

from __future__ import annotations

from typing import Protocol


class ExchangeStandardActionForAdditionalMoveActionHelper(Protocol):
    ...


def create_exchange_standard_action_for_additional_move_action_story(h: "ExchangeStandardActionForAdditionalMoveActionHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
