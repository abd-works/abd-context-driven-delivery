"""
Story: Derive Base Defense Rank from Ability (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: derive_base_defense_rank_from_ability_test_helper.{tier}.py implements DeriveBaseDefenseRankFromAbilityHelper.
"""

from __future__ import annotations

from typing import Protocol


class DeriveBaseDefenseRankFromAbilityHelper(Protocol):
    ...


def create_derive_base_defense_rank_from_ability_story(h: "DeriveBaseDefenseRankFromAbilityHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
