"""
Story: Enforce Armor Bonus Non-stacking Rule (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: enforce_armor_bonus_non_stacking_rule_test_helper.{tier}.py implements EnforceArmorBonusNonStackingRuleHelper.
"""

from __future__ import annotations

from typing import Protocol


class EnforceArmorBonusNonStackingRuleHelper(Protocol):
    ...


def create_enforce_armor_bonus_non_stacking_rule_story(h: "EnforceArmorBonusNonStackingRuleHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
