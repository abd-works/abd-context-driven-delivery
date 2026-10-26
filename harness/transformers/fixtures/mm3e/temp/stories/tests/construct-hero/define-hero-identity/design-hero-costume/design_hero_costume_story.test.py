"""
Story: Design Hero Costume (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: design_hero_costume_test_helper.{tier}.py implements DesignHeroCostumeHelper.
"""

from __future__ import annotations

from typing import Protocol


class DesignHeroCostumeHelper(Protocol):
    ...


def create_design_hero_costume_story(h: "DesignHeroCostumeHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
