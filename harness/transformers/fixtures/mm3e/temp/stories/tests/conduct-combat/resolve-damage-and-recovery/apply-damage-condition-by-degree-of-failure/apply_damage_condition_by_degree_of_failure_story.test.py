"""
Story: Apply Damage Condition by Degree of Failure (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: apply_damage_condition_by_degree_of_failure_test_helper.{tier}.py implements ApplyDamageConditionByDegreeOfFailureHelper.
"""

from __future__ import annotations

from typing import Protocol


class ApplyDamageConditionByDegreeOfFailureHelper(Protocol):
    ...


def create_apply_damage_condition_by_degree_of_failure_story(h: "ApplyDamageConditionByDegreeOfFailureHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_one_degree_is_a_cumulative_toughness_penalty() -> None:
        """SCENARIO: one degree is a cumulative Toughness penalty"""
    tests['test_one_degree_is_a_cumulative_toughness_penalty'] = test_one_degree_is_a_cumulative_toughness_penalty

    def test_two_degrees_is_dazed_plus_penalty() -> None:
        """SCENARIO: two degrees is dazed plus penalty"""
    tests['test_two_degrees_is_dazed_plus_penalty'] = test_two_degrees_is_dazed_plus_penalty

    def test_three_degrees_is_staggered_plus_penalty() -> None:
        """SCENARIO: three degrees is staggered plus penalty"""
    tests['test_three_degrees_is_staggered_plus_penalty'] = test_three_degrees_is_staggered_plus_penalty

    def test_four_degrees_is_incapacitated() -> None:
        """SCENARIO: four degrees is incapacitated"""
    tests['test_four_degrees_is_incapacitated'] = test_four_degrees_is_incapacitated

    def test_minion_any_failure() -> None:
        """SCENARIO: minion any failure"""
    tests['test_minion_any_failure'] = test_minion_any_failure

    return tests
