"""
Story: Roll Resistance Check Against Ongoing Effect to Remove Conditions (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: roll_resistance_check_against_ongoing_effect_to_remove_conditions_test_helper.{tier}.py implements RollResistanceCheckAgainstOngoingEffectToRemoveConditionsHelper.
"""

from __future__ import annotations

from typing import Protocol


class RollResistanceCheckAgainstOngoingEffectToRemoveConditionsHelper(Protocol):
    ...


def create_roll_resistance_check_against_ongoing_effect_to_remove_conditions_story(h: "RollResistanceCheckAgainstOngoingEffectToRemoveConditionsHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_success_ends_the_effect_and_clears_its_conditions() -> None:
        """SCENARIO: success ends the effect and clears its conditions"""
    tests['test_success_ends_the_effect_and_clears_its_conditions'] = test_success_ends_the_effect_and_clears_its_conditions

    def test_failure_leaves_the_effect_and_its_conditions() -> None:
        """SCENARIO: failure leaves the effect and its conditions"""
    tests['test_failure_leaves_the_effect_and_its_conditions'] = test_failure_leaves_the_effect_and_its_conditions

    def test_extra_degrees_of_failure_may_add_conditions() -> None:
        """SCENARIO: extra degrees of failure may add conditions"""
    tests['test_extra_degrees_of_failure_may_add_conditions'] = test_extra_degrees_of_failure_may_add_conditions

    return tests
