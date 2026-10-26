"""
Story: Complete Construction Check (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: complete_construction_check_test_helper.{tier}.py implements CompleteConstructionCheckHelper.
"""

from __future__ import annotations

from typing import Protocol


class CompleteConstructionCheckHelper(Protocol):
    ...


def create_complete_construction_check_story(h: "CompleteConstructionCheckHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
