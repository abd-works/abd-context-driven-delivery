"""
Story: Resolve Mind Reading Opposed Check Against Will Defense (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: resolve_mind_reading_opposed_check_against_will_defense_test_helper.{tier}.py implements ResolveMindReadingOpposedCheckAgainstWillDefenseHelper.
"""

from __future__ import annotations

from typing import Protocol


class ResolveMindReadingOpposedCheckAgainstWillDefenseHelper(Protocol):
    ...


def create_resolve_mind_reading_opposed_check_against_will_defense_story(h: "ResolveMindReadingOpposedCheckAgainstWillDefenseHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
