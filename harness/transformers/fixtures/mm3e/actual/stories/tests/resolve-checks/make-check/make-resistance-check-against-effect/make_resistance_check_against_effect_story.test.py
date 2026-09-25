"""
Story: Make Resistance Check Against Effect (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: make_resistance_check_against_effect_test_helper.{tier}.py implements MakeResistanceCheckAgainstEffectHelper.
"""

from __future__ import annotations

from typing import Protocol


class MakeResistanceCheckAgainstEffectHelper(Protocol):
    ...


def create_make_resistance_check_against_effect_story(h: "MakeResistanceCheckAgainstEffectHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_resistance_uses_ten_plus_effect_rank_as_dc() -> None:
        """SCENARIO: resistance uses ten plus effect rank as dc"""
    tests['test_resistance_uses_ten_plus_effect_rank_as_dc'] = test_resistance_uses_ten_plus_effect_rank_as_dc

    def test_success_applies_no_condition_from_this_effect() -> None:
        """SCENARIO: success applies no condition from this effect"""
    tests['test_success_applies_no_condition_from_this_effect'] = test_success_applies_no_condition_from_this_effect

    def test_failure_maps_degree_to_the_effect_condition_set() -> None:
        """SCENARIO: failure maps degree to the effect condition set"""
    tests['test_failure_maps_degree_to_the_effect_condition_set'] = test_failure_maps_degree_to_the_effect_condition_set

    def test_same_source_more_severe_removes_the_lesser() -> None:
        """SCENARIO: same source more severe removes the lesser"""
    tests['test_same_source_more_severe_removes_the_lesser'] = test_same_source_more_severe_removes_the_lesser

    def test_same_source_lesser_leaves_the_more_severe_unchanged() -> None:
        """SCENARIO: same source lesser leaves the more severe unchanged"""
    tests['test_same_source_lesser_leaves_the_more_severe_unchanged'] = test_same_source_lesser_leaves_the_more_severe_unchanged

    def test_different_source_lesser_is_parked_inactive() -> None:
        """SCENARIO: different source lesser is parked inactive"""
    tests['test_different_source_lesser_is_parked_inactive'] = test_different_source_lesser_is_parked_inactive

    return tests
