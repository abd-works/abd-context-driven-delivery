"""
Story: Execute Disarm Attempt (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: execute_disarm_attempt_test_helper.{tier}.py implements ExecuteDisarmAttemptHelper.
"""

from __future__ import annotations

from typing import Protocol


class ExecuteDisarmAttemptHelper(Protocol):
    ...


def create_execute_disarm_attempt_story(h: "ExecuteDisarmAttemptHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
