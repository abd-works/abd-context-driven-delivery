"""
Story: Assign Skill Ranks (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: assign_skill_ranks_test_helper.{tier}.py implements AssignSkillRanksHelper.
"""

from __future__ import annotations

from typing import Protocol


class AssignSkillRanksHelper(Protocol):
    ...


def create_assign_skill_ranks_story(h: "AssignSkillRanksHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_two_ranks_per_power_point() -> None:
        """SCENARIO: two ranks per power point"""
    tests['test_two_ranks_per_power_point'] = test_two_ranks_per_power_point

    return tests
