"""
Story: Declare Extra Effort for Combat Benefit (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: declare_extra_effort_for_combat_benefit_test_helper.{tier}.py implements DeclareExtraEffortForCombatBenefitHelper.
"""

from __future__ import annotations

from typing import Protocol


class DeclareExtraEffortForCombatBenefitHelper(Protocol):
    ...


def create_declare_extra_effort_for_combat_benefit_story(h: "DeclareExtraEffortForCombatBenefitHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
