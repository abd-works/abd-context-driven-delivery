"""
Story: Evolve Complication over Series (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: evolve_complication_over_series_test_helper.{tier}.py implements EvolveComplicationOverSeriesHelper.
"""

from __future__ import annotations

from typing import Protocol


class EvolveComplicationOverSeriesHelper(Protocol):
    ...


def create_evolve_complication_over_series_story(h: "EvolveComplicationOverSeriesHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
