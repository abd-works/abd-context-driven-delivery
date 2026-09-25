"""
Story: Apply Circumstance Modifier to Skill Check (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: apply_circumstance_modifier_to_skill_check_test_helper.{tier}.py implements ApplyCircumstanceModifierToSkillCheckHelper.
"""

from __future__ import annotations

from typing import Protocol


class ApplyCircumstanceModifierToSkillCheckHelper(Protocol):
    ...


def create_apply_circumstance_modifier_to_skill_check_story(h: "ApplyCircumstanceModifierToSkillCheckHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
