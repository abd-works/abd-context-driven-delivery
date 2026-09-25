"""
Story: Record Hero Background Details (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: record_hero_background_details_test_helper.{tier}.py implements RecordHeroBackgroundDetailsHelper.
"""

from __future__ import annotations

from typing import Protocol


class RecordHeroBackgroundDetailsHelper(Protocol):
    ...


def create_record_hero_background_details_story(h: "RecordHeroBackgroundDetailsHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
