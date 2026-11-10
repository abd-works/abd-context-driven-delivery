"""
Story: Enforce Skill Modifier Limit (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: enforce_skill_modifier_limit_test_helper.{tier}.py implements EnforceSkillModifierLimitHelper.
"""

from __future__ import annotations

from typing import Protocol


class EnforceSkillModifierLimitHelper(Protocol):
    ...


def create_enforce_skill_modifier_limit_story(h: "EnforceSkillModifierLimitHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_total_modifier_cannot_exceed_pl_plus_ten() -> None:
        """SCENARIO: total modifier cannot exceed pl plus ten"""
    tests['test_total_modifier_cannot_exceed_pl_plus_ten'] = test_total_modifier_cannot_exceed_pl_plus_ten

    return tests
