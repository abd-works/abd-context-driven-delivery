"""
Story: Set Default Action Range Duration for Effect Type (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: set_default_action_range_duration_for_effect_type_test_helper.{tier}.py implements SetDefaultActionRangeDurationForEffectTypeHelper.
"""

from __future__ import annotations

from typing import Protocol


class SetDefaultActionRangeDurationForEffectTypeHelper(Protocol):
    ...


def create_set_default_action_range_duration_for_effect_type_story(h: "SetDefaultActionRangeDurationForEffectTypeHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
