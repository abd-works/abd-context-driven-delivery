"""
Story: Delay Turn to Later Initiative Position (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: delay_turn_to_later_initiative_position_test_helper.{tier}.py implements DelayTurnToLaterInitiativePositionHelper.
"""

from __future__ import annotations

from typing import Protocol


class DelayTurnToLaterInitiativePositionHelper(Protocol):
    ...


def create_delay_turn_to_later_initiative_position_story(h: "DelayTurnToLaterInitiativePositionHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
