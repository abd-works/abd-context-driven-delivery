"""
Story: Spend Power Points on Trait Ranks (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: spend_power_points_on_trait_ranks_test_helper.{tier}.py implements SpendPowerPointsOnTraitRanksHelper.
"""

from __future__ import annotations

from typing import Protocol


class SpendPowerPointsOnTraitRanksHelper(Protocol):
    ...


def create_spend_power_points_on_trait_ranks_story(h: "SpendPowerPointsOnTraitRanksHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_ability_ranks_cost_two_each() -> None:
        """SCENARIO: ability ranks cost two each"""
    tests['test_ability_ranks_cost_two_each'] = test_ability_ranks_cost_two_each

    def test_defense_ranks_cost_one_above_ability_base() -> None:
        """SCENARIO: defense ranks cost one above ability base"""
    tests['test_defense_ranks_cost_one_above_ability_base'] = test_defense_ranks_cost_one_above_ability_base

    def test_skill_ranks_cost_one_per_two_ranks() -> None:
        """SCENARIO: skill ranks cost one per two ranks"""
    tests['test_skill_ranks_cost_one_per_two_ranks'] = test_skill_ranks_cost_one_per_two_ranks

    def test_advantages_cost_one_per_rank() -> None:
        """SCENARIO: advantages cost one per rank"""
    tests['test_advantages_cost_one_per_rank'] = test_advantages_cost_one_per_rank

    def test_powers_use_the_effect_cost_formula() -> None:
        """SCENARIO: powers use the effect cost formula"""
    tests['test_powers_use_the_effect_cost_formula'] = test_powers_use_the_effect_cost_formula

    def test_insufficient_points_reject_the_spend() -> None:
        """SCENARIO: insufficient points reject the spend"""
    tests['test_insufficient_points_reject_the_spend'] = test_insufficient_points_reject_the_spend

    return tests
