"""
Story: Adjust Attack and Defense Values by Trade-Off Amount (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: adjust_attack_and_defense_values_by_trade_off_amount_test_helper.{tier}.py implements AdjustAttackAndDefenseValuesByTradeOffAmountHelper.
"""

from __future__ import annotations

from typing import Protocol


class AdjustAttackAndDefenseValuesByTradeOffAmountHelper(Protocol):
    ...


def create_adjust_attack_and_defense_values_by_trade_off_amount_story(h: "AdjustAttackAndDefenseValuesByTradeOffAmountHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
