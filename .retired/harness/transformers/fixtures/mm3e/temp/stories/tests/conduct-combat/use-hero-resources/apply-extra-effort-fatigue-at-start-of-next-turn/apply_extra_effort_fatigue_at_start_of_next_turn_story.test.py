"""
Story: Apply Extra Effort Fatigue at Start of Next Turn (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: apply_extra_effort_fatigue_at_start_of_next_turn_test_helper.{tier}.py implements ApplyExtraEffortFatigueAtStartOfNextTurnHelper.
"""

from __future__ import annotations

from typing import Protocol


class ApplyExtraEffortFatigueAtStartOfNextTurnHelper(Protocol):
    ...


def create_apply_extra_effort_fatigue_at_start_of_next_turn_story(h: "ApplyExtraEffortFatigueAtStartOfNextTurnHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
