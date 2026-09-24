"""
Story: Attack or Smash Object (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: attack_or_smash_object_test_helper.{tier}.py implements AttackOrSmashObjectHelper.
"""

from __future__ import annotations

from typing import Protocol


class AttackOrSmashObjectHelper(Protocol):
    ...


def create_attack_or_smash_object_story(h: "AttackOrSmashObjectHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
