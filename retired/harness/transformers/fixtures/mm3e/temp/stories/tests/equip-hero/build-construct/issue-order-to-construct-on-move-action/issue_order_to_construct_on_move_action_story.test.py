"""
Story: Issue Order to Construct on Move Action (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: issue_order_to_construct_on_move_action_test_helper.{tier}.py implements IssueOrderToConstructOnMoveActionHelper.
"""

from __future__ import annotations

from typing import Protocol


class IssueOrderToConstructOnMoveActionHelper(Protocol):
    ...


def create_issue_order_to_construct_on_move_action_story(h: "IssueOrderToConstructOnMoveActionHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
