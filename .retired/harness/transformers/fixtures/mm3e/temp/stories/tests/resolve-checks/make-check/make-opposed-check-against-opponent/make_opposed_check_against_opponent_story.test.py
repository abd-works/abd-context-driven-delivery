"""
Story: Make Opposed Check Against Opponent (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: make_opposed_check_against_opponent_test_helper.{tier}.py implements MakeOpposedCheckAgainstOpponentHelper.
"""

from __future__ import annotations

from typing import Protocol


class MakeOpposedCheckAgainstOpponentHelper(Protocol):
    ...


def create_make_opposed_check_against_opponent_story(h: "MakeOpposedCheckAgainstOpponentHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_higher_roll_total_wins() -> None:
        """SCENARIO: higher roll total wins"""
    tests['test_higher_roll_total_wins'] = test_higher_roll_total_wins

    def test_tie_goes_to_higher_trait_bonus() -> None:
        """SCENARIO: tie goes to higher trait bonus"""
    tests['test_tie_goes_to_higher_trait_bonus'] = test_tie_goes_to_higher_trait_bonus

    def test_equal_totals_and_bonuses_use_tie_break_d20() -> None:
        """SCENARIO: equal totals and bonuses use tie-break d20"""
    tests['test_equal_totals_and_bonuses_use_tie_break_d20'] = test_equal_totals_and_bonuses_use_tie_break_d20

    def test_passive_opposition_sets_dc_to_opponent_modifier_plus_ten() -> None:
        """SCENARIO: passive opposition sets dc to opponent modifier plus ten"""
    tests['test_passive_opposition_sets_dc_to_opponent_modifier_plus_ten'] = test_passive_opposition_sets_dc_to_opponent_modifier_plus_ten

    return tests
