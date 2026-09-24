"""
Story: Remove Ally Condition via Leadership (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: remove_ally_condition_via_leadership_test_helper.{tier}.py implements RemoveAllyConditionViaLeadershipHelper.
"""

from __future__ import annotations

from typing import Protocol


class RemoveAllyConditionViaLeadershipHelper(Protocol):
    ...


def create_remove_ally_condition_via_leadership_story(h: "RemoveAllyConditionViaLeadershipHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
