"""
Story: Resolve Comparison Check Without Roll (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: resolve_comparison_check_without_roll_test_helper.{tier}.py implements ResolveComparisonCheckWithoutRollHelper.
"""

from __future__ import annotations

from typing import Protocol


class ResolveComparisonCheckWithoutRollHelper(Protocol):
    ...


def create_resolve_comparison_check_without_roll_story(h: "ResolveComparisonCheckWithoutRollHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_higher_rank_wins_without_a_die() -> None:
        """SCENARIO: higher rank wins without a die"""
    tests['test_higher_rank_wins_without_a_die'] = test_higher_rank_wins_without_a_die

    def test_equal_ranks_report_a_tie() -> None:
        """SCENARIO: equal ranks report a tie"""
    tests['test_equal_ranks_report_a_tie'] = test_equal_ranks_report_a_tie

    return tests
