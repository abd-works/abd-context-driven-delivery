"""
Story: Apply Trade-Off within Limit Pair (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: apply_trade_off_within_limit_pair_test_helper.{tier}.py implements ApplyTradeOffWithinLimitPairHelper.
"""

from __future__ import annotations

from typing import Protocol


class ApplyTradeOffWithinLimitPairHelper(Protocol):
    ...


def create_apply_trade_off_within_limit_pair_story(h: "ApplyTradeOffWithinLimitPairHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_trade_off_keeps_the_pair_sum() -> None:
        """SCENARIO: trade-off keeps the pair sum"""
    tests['test_trade_off_keeps_the_pair_sum'] = test_trade_off_keeps_the_pair_sum

    return tests
