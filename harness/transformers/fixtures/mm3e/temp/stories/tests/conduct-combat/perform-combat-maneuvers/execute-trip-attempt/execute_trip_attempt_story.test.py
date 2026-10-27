"""
Story: Execute Trip Attempt (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: execute_trip_attempt_test_helper.{tier}.py implements ExecuteTripAttemptHelper.
"""

from __future__ import annotations

from typing import Protocol


class ExecuteTripAttemptHelper(Protocol):
    ...


def create_execute_trip_attempt_story(h: "ExecuteTripAttemptHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
