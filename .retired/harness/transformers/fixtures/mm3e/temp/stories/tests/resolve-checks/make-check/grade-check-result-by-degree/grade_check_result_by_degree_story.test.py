"""
Story: Grade Check Result by Degree (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: grade_check_result_by_degree_test_helper.{tier}.py implements GradeCheckResultByDegreeHelper.
"""

from __future__ import annotations

from typing import Protocol


class GradeCheckResultByDegreeHelper(Protocol):
    ...


def create_grade_check_result_by_degree_story(h: "GradeCheckResultByDegreeHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_success_grades_one_degree_plus_one_per_full_five_of_margin() -> None:
        """SCENARIO: success grades one degree plus one per full five of margin"""
    tests['test_success_grades_one_degree_plus_one_per_full_five_of_margin'] = test_success_grades_one_degree_plus_one_per_full_five_of_margin

    def test_failure_grades_one_degree_plus_one_per_full_five_below() -> None:
        """SCENARIO: failure grades one degree plus one per full five below"""
    tests['test_failure_grades_one_degree_plus_one_per_full_five_below'] = test_failure_grades_one_degree_plus_one_per_full_five_below

    def test_four_degrees_of_success_is_the_maximum() -> None:
        """SCENARIO: four degrees of success is the maximum"""
    tests['test_four_degrees_of_success_is_the_maximum'] = test_four_degrees_of_success_is_the_maximum

    def test_four_degrees_of_failure_is_the_maximum() -> None:
        """SCENARIO: four degrees of failure is the maximum"""
    tests['test_four_degrees_of_failure_is_the_maximum'] = test_four_degrees_of_failure_is_the_maximum

    def test_natural_20_can_flip_one_degree_of_failure_to_success() -> None:
        """SCENARIO: natural 20 can flip one degree of failure to success"""
    tests['test_natural_20_can_flip_one_degree_of_failure_to_success'] = test_natural_20_can_flip_one_degree_of_failure_to_success

    return tests
