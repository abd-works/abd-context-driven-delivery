"""
Story: Choose Complication (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: choose_complication_test_helper.{tier}.py implements ChooseComplicationHelper.
"""

from __future__ import annotations

from typing import Protocol


class ChooseComplicationHelper(Protocol):
    ...


def create_choose_complication_story(h: "ChooseComplicationHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_player_defines_narrative_detail() -> None:
        """SCENARIO: player defines narrative detail"""
    tests['test_player_defines_narrative_detail'] = test_player_defines_narrative_detail

    return tests
