"""
Story: Perform Routine Check (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: perform_routine_check_test_helper.{tier}.py implements PerformRoutineCheckHelper.
"""

from __future__ import annotations

from typing import Protocol


class PerformRoutineCheckHelper(Protocol):
    ...


def create_perform_routine_check_story(h: "PerformRoutineCheckHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_routine_substitutes_ten_for_the_die() -> None:
        """SCENARIO: routine substitutes ten for the die"""
    tests['test_routine_substitutes_ten_for_the_die'] = test_routine_substitutes_ten_for_the_die

    def test_insufficient_routine_total_lets_the_player_roll() -> None:
        """SCENARIO: insufficient routine total lets the player roll"""
    tests['test_insufficient_routine_total_lets_the_player_roll'] = test_insufficient_routine_total_lets_the_player_roll

    def test_plus_ten_against_dc_20_succeeds_without_rolling() -> None:
        """SCENARIO: plus ten against dc 20 succeeds without rolling"""
    tests['test_plus_ten_against_dc_20_succeeds_without_rolling'] = test_plus_ten_against_dc_20_succeeds_without_rolling

    return tests
