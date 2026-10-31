"""
Story: Execute Slam Attack During Charge (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: execute_slam_attack_during_charge_test_helper.{tier}.py implements ExecuteSlamAttackDuringChargeHelper.
"""

from __future__ import annotations

from typing import Protocol


class ExecuteSlamAttackDuringChargeHelper(Protocol):
    ...


def create_execute_slam_attack_during_charge_story(h: "ExecuteSlamAttackDuringChargeHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
