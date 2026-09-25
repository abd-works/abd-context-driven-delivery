"""
Story: Apply Healing Check and Remove Damage Condition from Most Severe (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: apply_healing_check_and_remove_damage_condition_from_most_severe_test_helper.{tier}.py implements ApplyHealingCheckAndRemoveDamageConditionFromMostSevereHelper.
"""

from __future__ import annotations

from typing import Protocol


class ApplyHealingCheckAndRemoveDamageConditionFromMostSevereHelper(Protocol):
    ...


def create_apply_healing_check_and_remove_damage_condition_from_most_severe_story(h: "ApplyHealingCheckAndRemoveDamageConditionFromMostSevereHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
