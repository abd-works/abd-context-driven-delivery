"""
Story: Roll Fortitude Check to Stabilize While Dying (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: roll_fortitude_check_to_stabilize_while_dying_test_helper.{tier}.py implements RollFortitudeCheckToStabilizeWhileDyingHelper.
"""

from __future__ import annotations

from typing import Protocol


class RollFortitudeCheckToStabilizeWhileDyingHelper(Protocol):
    ...


def create_roll_fortitude_check_to_stabilize_while_dying_story(h: "RollFortitudeCheckToStabilizeWhileDyingHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_each_round_requires_fortitude_dc_15() -> None:
        """SCENARIO: each round requires fortitude dc 15"""
    tests['test_each_round_requires_fortitude_dc_15'] = test_each_round_requires_fortitude_dc_15

    def test_two_degrees_of_success_stabilize() -> None:
        """SCENARIO: two degrees of success stabilize"""
    tests['test_two_degrees_of_success_stabilize'] = test_two_degrees_of_success_stabilize

    def test_three_total_degrees_of_failure_is_death() -> None:
        """SCENARIO: three total degrees of failure is death"""
    tests['test_three_total_degrees_of_failure_is_death'] = test_three_total_degrees_of_failure_is_death

    def test_natural_20_accelerates_stabilization() -> None:
        """SCENARIO: natural 20 accelerates stabilization"""
    tests['test_natural_20_accelerates_stabilization'] = test_natural_20_accelerates_stabilization

    return tests
