"""
Story: Recover from Damage in Conflict (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: recover_from_damage_in_conflict_test_helper.{tier}.py implements RecoverFromDamageInConflictHelper.
"""

from __future__ import annotations

from typing import Protocol


class RecoverFromDamageInConflictHelper(Protocol):
    ...


def create_recover_from_damage_in_conflict_story(h: "RecoverFromDamageInConflictHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
