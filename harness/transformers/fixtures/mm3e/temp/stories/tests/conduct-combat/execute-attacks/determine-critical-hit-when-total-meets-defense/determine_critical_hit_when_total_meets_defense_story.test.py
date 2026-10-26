"""
Story: Determine Critical Hit When Total Meets Defense (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: determine_critical_hit_when_total_meets_defense_test_helper.{tier}.py implements DetermineCriticalHitWhenTotalMeetsDefenseHelper.
"""

from __future__ import annotations

from typing import Protocol


class DetermineCriticalHitWhenTotalMeetsDefenseHelper(Protocol):
    ...


def create_determine_critical_hit_when_total_meets_defense_story(h: "DetermineCriticalHitWhenTotalMeetsDefenseHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
