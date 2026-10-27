"""
Story: Spend Hero Point (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: spend_hero_point_test_helper.{tier}.py implements SpendHeroPointHelper.
"""

from __future__ import annotations

from typing import Protocol


class SpendHeroPointHelper(Protocol):
    ...


def create_spend_hero_point_story(h: "SpendHeroPointHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_re_roll_treats_1_10_as_11() -> None:
        """SCENARIO: re-roll treats 1-10 as 11"""
    tests['test_re_roll_treats_1_10_as_11'] = test_re_roll_treats_1_10_as_11

    def test_recover_a_condition_immediately() -> None:
        """SCENARIO: recover a condition immediately"""
    tests['test_recover_a_condition_immediately'] = test_recover_a_condition_immediately

    def test_heroic_feat() -> None:
        """SCENARIO: heroic feat"""
    tests['test_heroic_feat'] = test_heroic_feat

    def test_edit_scene_or_instant_counter() -> None:
        """SCENARIO: edit scene or instant counter"""
    tests['test_edit_scene_or_instant_counter'] = test_edit_scene_or_instant_counter

    return tests
