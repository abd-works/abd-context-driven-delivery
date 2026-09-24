"""
Story: Remove Condition When Source Effect Ends (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: remove_condition_when_source_effect_ends_test_helper.{tier}.py implements RemoveConditionWhenSourceEffectEndsHelper.
"""

from __future__ import annotations

from typing import Protocol


class RemoveConditionWhenSourceEffectEndsHelper(Protocol):
    ...


def create_remove_condition_when_source_effect_ends_story(h: "RemoveConditionWhenSourceEffectEndsHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_source_end_removes_that_source_only() -> None:
        """SCENARIO: source end removes that source only"""
    tests['test_source_end_removes_that_source_only'] = test_source_end_removes_that_source_only

    def test_lesser_from_another_still_active_source_becomes_active() -> None:
        """SCENARIO: lesser from another still-active source becomes active"""
    tests['test_lesser_from_another_still_active_source_becomes_active'] = test_lesser_from_another_still_active_source_becomes_active

    def test_lesser_does_not_return_when_its_source_also_ended() -> None:
        """SCENARIO: lesser does not return when its source also ended"""
    tests['test_lesser_does_not_return_when_its_source_also_ended'] = test_lesser_does_not_return_when_its_source_also_ended

    return tests
