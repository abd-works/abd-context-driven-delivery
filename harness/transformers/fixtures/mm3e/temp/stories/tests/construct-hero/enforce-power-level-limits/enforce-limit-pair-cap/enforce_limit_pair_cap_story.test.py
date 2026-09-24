"""
Story: Enforce Limit Pair Cap (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: enforce_limit_pair_cap_test_helper.{tier}.py implements EnforceLimitPairCapHelper.
"""

from __future__ import annotations

from typing import Protocol


class EnforceLimitPairCapHelper(Protocol):
    ...


def create_enforce_limit_pair_cap_story(h: "EnforceLimitPairCapHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_attack_and_effect_pair() -> None:
        """SCENARIO: attack and effect pair"""
    tests['test_attack_and_effect_pair'] = test_attack_and_effect_pair

    def test_dodge_and_toughness_pair() -> None:
        """SCENARIO: dodge and toughness pair"""
    tests['test_dodge_and_toughness_pair'] = test_dodge_and_toughness_pair

    def test_parry_and_toughness_pair() -> None:
        """SCENARIO: parry and toughness pair"""
    tests['test_parry_and_toughness_pair'] = test_parry_and_toughness_pair

    def test_fortitude_and_will_pair() -> None:
        """SCENARIO: fortitude and will pair"""
    tests['test_fortitude_and_will_pair'] = test_fortitude_and_will_pair

    def test_skill_modifier_cap() -> None:
        """SCENARIO: skill modifier cap"""
    tests['test_skill_modifier_cap'] = test_skill_modifier_cap

    return tests
