"""
Story: Use Invention for One Scene (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: use_invention_for_one_scene_test_helper.{tier}.py implements UseInventionForOneSceneHelper.
"""

from __future__ import annotations

from typing import Protocol


class UseInventionForOneSceneHelper(Protocol):
    ...


def create_use_invention_for_one_scene_story(h: "UseInventionForOneSceneHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
