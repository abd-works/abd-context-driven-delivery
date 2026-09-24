"""
Story: Declare Favored Environment Bonus Allocation (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: declare_favored_environment_bonus_allocation_test_helper.{tier}.py implements DeclareFavoredEnvironmentBonusAllocationHelper.
"""

from __future__ import annotations

from typing import Protocol


class DeclareFavoredEnvironmentBonusAllocationHelper(Protocol):
    ...


def create_declare_favored_environment_bonus_allocation_story(h: "DeclareFavoredEnvironmentBonusAllocationHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
