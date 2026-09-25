"""
Story: Apply Absent Ability Capability Restrictions (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: apply_absent_ability_capability_restrictions_test_helper.{tier}.py implements ApplyAbsentAbilityCapabilityRestrictionsHelper.
"""

from __future__ import annotations

from typing import Protocol


class ApplyAbsentAbilityCapabilityRestrictionsHelper(Protocol):
    ...


def create_apply_absent_ability_capability_restrictions_story(h: "ApplyAbsentAbilityCapabilityRestrictionsHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_no_strength_cannot_exert_force() -> None:
        """SCENARIO: no strength cannot exert force"""
    tests['test_no_strength_cannot_exert_force'] = test_no_strength_cannot_exert_force

    def test_no_stamina_treats_damage_as_an_object() -> None:
        """SCENARIO: no stamina treats damage as an object"""
    tests['test_no_stamina_treats_damage_as_an_object'] = test_no_stamina_treats_damage_as_an_object

    def test_absence_is_not_rank_minus_five() -> None:
        """SCENARIO: absence is not rank minus five"""
    tests['test_absence_is_not_rank_minus_five'] = test_absence_is_not_rank_minus_five

    return tests
