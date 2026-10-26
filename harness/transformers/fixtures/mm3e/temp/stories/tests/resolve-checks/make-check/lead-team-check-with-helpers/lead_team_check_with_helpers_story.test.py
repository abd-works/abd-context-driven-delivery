"""
Story: Lead Team Check with Helpers (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: lead_team_check_with_helpers_test_helper.{tier}.py implements LeadTeamCheckWithHelpersHelper.
"""

from __future__ import annotations

from typing import Protocol


class LeadTeamCheckWithHelpersHelper(Protocol):
    ...


def create_lead_team_check_with_helpers_story(h: "LeadTeamCheckWithHelpersHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_helpers_check_dc_10_then_modify_the_leader() -> None:
        """SCENARIO: helpers check dc 10 then modify the leader"""
    tests['test_helpers_check_dc_10_then_modify_the_leader'] = test_helpers_check_dc_10_then_modify_the_leader

    def test_one_or_two_helper_successes_grant_plus_two() -> None:
        """SCENARIO: one or two helper successes grant plus two"""
    tests['test_one_or_two_helper_successes_grant_plus_two'] = test_one_or_two_helper_successes_grant_plus_two

    def test_three_helper_successes_grant_plus_five() -> None:
        """SCENARIO: three helper successes grant plus five"""
    tests['test_three_helper_successes_grant_plus_five'] = test_three_helper_successes_grant_plus_five

    def test_helper_failure_may_impose_minus_two() -> None:
        """SCENARIO: helper failure may impose minus two"""
    tests['test_helper_failure_may_impose_minus_two'] = test_helper_failure_may_impose_minus_two

    return tests
