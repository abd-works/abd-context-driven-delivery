"""
Story: Execute Charge Attack with Penalty (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: execute_charge_attack_with_penalty_test_helper.{tier}.py implements ExecuteChargeAttackWithPenaltyHelper.
"""

from __future__ import annotations

from typing import Protocol


class ExecuteChargeAttackWithPenaltyHelper(Protocol):
    ...


def create_execute_charge_attack_with_penalty_story(h: "ExecuteChargeAttackWithPenaltyHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
