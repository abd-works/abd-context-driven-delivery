"""
Story: Use Interaction Skill Against Target (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: use_interaction_skill_against_target_test_helper.{tier}.py implements UseInteractionSkillAgainstTargetHelper.
"""

from __future__ import annotations

from typing import Protocol


class UseInteractionSkillAgainstTargetHelper(Protocol):
    ...


def create_use_interaction_skill_against_target_story(h: "UseInteractionSkillAgainstTargetHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_deception_intimidation_persuasion_or_insight() -> None:
        """SCENARIO: deception intimidation persuasion or insight"""
    tests['test_deception_intimidation_persuasion_or_insight'] = test_deception_intimidation_persuasion_or_insight

    return tests
