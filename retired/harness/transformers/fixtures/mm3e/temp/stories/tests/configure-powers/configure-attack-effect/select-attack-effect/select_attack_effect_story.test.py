"""
Story: Select Attack Effect (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: select_attack_effect_test_helper.{tier}.py implements SelectAttackEffectHelper.
"""

from __future__ import annotations

from typing import Protocol


class SelectAttackEffectHelper(Protocol):
    ...


def create_select_attack_effect_story(h: "SelectAttackEffectHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_affliction_requires_three_conditions_in_degree_order() -> None:
        """SCENARIO: affliction requires three conditions in degree order"""
    tests['test_affliction_requires_three_conditions_in_degree_order'] = test_affliction_requires_three_conditions_in_degree_order

    def test_blast_is_damage_plus_ranged() -> None:
        """SCENARIO: blast is damage plus ranged"""
    tests['test_blast_is_damage_plus_ranged'] = test_blast_is_damage_plus_ranged

    return tests
