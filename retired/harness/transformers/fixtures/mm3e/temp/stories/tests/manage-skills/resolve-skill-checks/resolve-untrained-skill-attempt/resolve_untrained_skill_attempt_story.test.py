"""
Story: Resolve Untrained Skill Attempt (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: resolve_untrained_skill_attempt_test_helper.{tier}.py implements ResolveUntrainedSkillAttemptHelper.
"""

from __future__ import annotations

from typing import Protocol


class ResolveUntrainedSkillAttemptHelper(Protocol):
    ...


def create_resolve_untrained_skill_attempt_story(h: "ResolveUntrainedSkillAttemptHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_untrained_allowed_uses_ability_only() -> None:
        """SCENARIO: untrained allowed uses ability only"""
    tests['test_untrained_allowed_uses_ability_only'] = test_untrained_allowed_uses_ability_only

    def test_trained_only_auto_fails() -> None:
        """SCENARIO: trained only auto-fails"""
    tests['test_trained_only_auto_fails'] = test_trained_only_auto_fails

    return tests
