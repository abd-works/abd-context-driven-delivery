"""
Story: Choose Motivation Complication (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: choose_motivation_complication_test_helper.{tier}.py implements ChooseMotivationComplicationHelper.
"""

from __future__ import annotations

from typing import Protocol


class ChooseMotivationComplicationHelper(Protocol):
    ...


def create_choose_motivation_complication_story(h: "ChooseMotivationComplicationHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_motivation_is_required() -> None:
        """SCENARIO: motivation is required"""
    tests['test_motivation_is_required'] = test_motivation_is_required

    return tests
