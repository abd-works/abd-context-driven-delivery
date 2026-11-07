"""
Story: Make Skill Check (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: make_skill_check_test_helper.{tier}.py implements MakeSkillCheckHelper.
"""

from __future__ import annotations

from typing import Protocol


class MakeSkillCheckHelper(Protocol):
    ...


def create_make_skill_check_story(h: "MakeSkillCheckHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_success_when_total_meets_dc() -> None:
        """SCENARIO: success when total meets dc"""
    tests['test_success_when_total_meets_dc'] = test_success_when_total_meets_dc

    def test_trained_only_at_rank_zero_fails_without_a_roll() -> None:
        """SCENARIO: trained only at rank zero fails without a roll"""
    tests['test_trained_only_at_rank_zero_fails_without_a_roll'] = test_trained_only_at_rank_zero_fails_without_a_roll

    return tests
