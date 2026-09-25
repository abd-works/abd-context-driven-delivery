"""
Story: Make Trait Check (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: make_trait_check_test_helper.{tier}.py implements MakeTraitCheckHelper.
"""

from __future__ import annotations

from typing import Protocol


class MakeTraitCheckHelper(Protocol):
    ...


def create_make_trait_check_story(h: "MakeTraitCheckHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_check_succeeds_when_roll_total_meets_dc() -> None:
        """SCENARIO: check succeeds when roll total meets dc"""
    tests['test_check_succeeds_when_roll_total_meets_dc'] = test_check_succeeds_when_roll_total_meets_dc

    def test_check_fails_when_roll_total_is_below_dc() -> None:
        """SCENARIO: check fails when roll total is below dc"""
    tests['test_check_fails_when_roll_total_is_below_dc'] = test_check_fails_when_roll_total_is_below_dc

    def test_circumstance_modifiers_add_to_roll_total() -> None:
        """SCENARIO: circumstance modifiers add to roll total"""
    tests['test_circumstance_modifiers_add_to_roll_total'] = test_circumstance_modifiers_add_to_roll_total

    def test_missing_tools_impose_minus_five() -> None:
        """SCENARIO: missing tools impose minus five"""
    tests['test_missing_tools_impose_minus_five'] = test_missing_tools_impose_minus_five

    def test_makeshift_tools_reduce_the_penalty_to_minus_two() -> None:
        """SCENARIO: makeshift tools reduce the penalty to minus two"""
    tests['test_makeshift_tools_reduce_the_penalty_to_minus_two'] = test_makeshift_tools_reduce_the_penalty_to_minus_two

    def test_natural_20_upgrades_degree_after_grading() -> None:
        """SCENARIO: natural 20 upgrades degree after grading"""
    tests['test_natural_20_upgrades_degree_after_grading'] = test_natural_20_upgrades_degree_after_grading

    return tests
