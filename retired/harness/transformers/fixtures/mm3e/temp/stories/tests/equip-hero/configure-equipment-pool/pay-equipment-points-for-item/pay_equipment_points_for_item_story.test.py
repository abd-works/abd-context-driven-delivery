"""
Story: Pay Equipment Points for Item (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: pay_equipment_points_for_item_test_helper.{tier}.py implements PayEquipmentPointsForItemHelper.
"""

from __future__ import annotations

from typing import Protocol


class PayEquipmentPointsForItemHelper(Protocol):
    ...


def create_pay_equipment_points_for_item_story(h: "PayEquipmentPointsForItemHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
