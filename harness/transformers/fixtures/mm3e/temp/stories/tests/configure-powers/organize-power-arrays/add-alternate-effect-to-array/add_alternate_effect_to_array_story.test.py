"""
Story: Add Alternate Effect to Array (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: add_alternate_effect_to_array_test_helper.{tier}.py implements AddAlternateEffectToArrayHelper.
"""

from __future__ import annotations

from typing import Protocol


class AddAlternateEffectToArrayHelper(Protocol):
    ...


def create_add_alternate_effect_to_array_story(h: "AddAlternateEffectToArrayHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
