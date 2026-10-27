"""
Story: Purchase General Gear (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: purchase_general_gear_test_helper.{tier}.py implements PurchaseGeneralGearHelper.
"""

from __future__ import annotations

from typing import Protocol


class PurchaseGeneralGearHelper(Protocol):
    ...


def create_purchase_general_gear_story(h: "PurchaseGeneralGearHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
