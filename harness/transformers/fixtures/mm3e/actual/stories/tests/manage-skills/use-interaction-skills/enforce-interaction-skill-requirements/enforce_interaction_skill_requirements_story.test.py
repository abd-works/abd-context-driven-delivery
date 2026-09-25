"""
Story: Enforce Interaction Skill Requirements (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: enforce_interaction_skill_requirements_test_helper.{tier}.py implements EnforceInteractionSkillRequirementsHelper.
"""

from __future__ import annotations

from typing import Protocol


class EnforceInteractionSkillRequirementsHelper(Protocol):
    ...


def create_enforce_interaction_skill_requirements_story(h: "EnforceInteractionSkillRequirementsHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_unaware_or_non_comprehending_subject() -> None:
        """SCENARIO: unaware or non-comprehending subject"""
    tests['test_unaware_or_non_comprehending_subject'] = test_unaware_or_non_comprehending_subject

    def test_intellect_minus_five() -> None:
        """SCENARIO: intellect minus five"""
    tests['test_intellect_minus_five'] = test_intellect_minus_five

    def test_subject_lacking_mental_abilities() -> None:
        """SCENARIO: subject lacking mental abilities"""
    tests['test_subject_lacking_mental_abilities'] = test_subject_lacking_mental_abilities

    def test_immunity_to_interaction() -> None:
        """SCENARIO: immunity to interaction"""
    tests['test_immunity_to_interaction'] = test_immunity_to_interaction

    return tests
