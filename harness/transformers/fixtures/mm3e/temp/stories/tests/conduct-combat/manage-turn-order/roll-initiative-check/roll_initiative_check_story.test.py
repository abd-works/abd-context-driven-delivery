"""
Story: Roll Initiative Check (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: roll_initiative_check_test_helper.{tier}.py implements RollInitiativeCheckHelper.
"""

from __future__ import annotations

from typing import Protocol


class RollInitiativeCheckHelper(Protocol):
    ...


def create_roll_initiative_check_story(h: "RollInitiativeCheckHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
