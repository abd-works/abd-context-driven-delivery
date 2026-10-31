"""
Story: Designate Ability Rank Portion as Enhanced (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: designate_ability_rank_portion_as_enhanced_test_helper.{tier}.py implements DesignateAbilityRankPortionAsEnhancedHelper.
"""

from __future__ import annotations

from typing import Protocol


class DesignateAbilityRankPortionAsEnhancedHelper(Protocol):
    ...


def create_designate_ability_rank_portion_as_enhanced_story(h: "DesignateAbilityRankPortionAsEnhancedHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_partial_enhanced_keeps_natural() -> None:
        """SCENARIO: partial enhanced keeps natural"""
    tests['test_partial_enhanced_keeps_natural'] = test_partial_enhanced_keeps_natural

    def test_nullify_removes_only_enhanced() -> None:
        """SCENARIO: nullify removes only enhanced"""
    tests['test_nullify_removes_only_enhanced'] = test_nullify_removes_only_enhanced

    return tests
