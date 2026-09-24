"""
Story: Supersede Condition in Chain (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: supersede_condition_in_chain_test_helper.{tier}.py implements SupersedeConditionInChainHelper.
"""

from __future__ import annotations

from typing import Protocol


class SupersedeConditionInChainHelper(Protocol):
    ...


def create_supersede_condition_in_chain_story(h: "SupersedeConditionInChainHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_more_severe_from_same_chain_overrides_the_lesser() -> None:
        """SCENARIO: more severe from same chain overrides the lesser"""
    tests['test_more_severe_from_same_chain_overrides_the_lesser'] = test_more_severe_from_same_chain_overrides_the_lesser

    def test_dazed_then_stunned() -> None:
        """SCENARIO: dazed then stunned"""
    tests['test_dazed_then_stunned'] = test_dazed_then_stunned

    def test_impaired_then_disabled() -> None:
        """SCENARIO: impaired then disabled"""
    tests['test_impaired_then_disabled'] = test_impaired_then_disabled

    def test_vulnerable_then_defenseless() -> None:
        """SCENARIO: vulnerable then defenseless"""
    tests['test_vulnerable_then_defenseless'] = test_vulnerable_then_defenseless

    def test_hindered_then_immobile() -> None:
        """SCENARIO: hindered then immobile"""
    tests['test_hindered_then_immobile'] = test_hindered_then_immobile

    def test_compelled_then_controlled() -> None:
        """SCENARIO: compelled then controlled"""
    tests['test_compelled_then_controlled'] = test_compelled_then_controlled

    return tests
