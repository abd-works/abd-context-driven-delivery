"""
Story: Apply Debilitated Ability Condition Effects (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: apply_debilitated_ability_condition_effects_test_helper.{tier}.py implements ApplyDebilitatedAbilityConditionEffectsHelper.
"""

from __future__ import annotations

from typing import Protocol


class ApplyDebilitatedAbilityConditionEffectsHelper(Protocol):
    ...


def create_apply_debilitated_ability_condition_effects_story(h: "ApplyDebilitatedAbilityConditionEffectsHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_str_agl_or_dex_collapse() -> None:
        """SCENARIO: str agl or dex collapse"""
    tests['test_str_agl_or_dex_collapse'] = test_str_agl_or_dex_collapse

    def test_stamina_dying_plus_extra_fortitude_penalty() -> None:
        """SCENARIO: stamina dying plus extra fortitude penalty"""
    tests['test_stamina_dying_plus_extra_fortitude_penalty'] = test_stamina_dying_plus_extra_fortitude_penalty

    def test_fighting_dazed_plus_defenseless() -> None:
        """SCENARIO: fighting dazed plus defenseless"""
    tests['test_fighting_dazed_plus_defenseless'] = test_fighting_dazed_plus_defenseless

    def test_int_awe_or_pre_unaware() -> None:
        """SCENARIO: int awe or pre unaware"""
    tests['test_int_awe_or_pre_unaware'] = test_int_awe_or_pre_unaware

    return tests
