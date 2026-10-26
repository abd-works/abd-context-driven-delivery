"""
Story: Jury-Rig Device by Spending Hero Point (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: jury_rig_device_by_spending_hero_point_test_helper.{tier}.py implements JuryRigDeviceBySpendingHeroPointHelper.
"""

from __future__ import annotations

from typing import Protocol


class JuryRigDeviceBySpendingHeroPointHelper(Protocol):
    ...


def create_jury_rig_device_by_spending_hero_point_story(h: "JuryRigDeviceBySpendingHeroPointHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
