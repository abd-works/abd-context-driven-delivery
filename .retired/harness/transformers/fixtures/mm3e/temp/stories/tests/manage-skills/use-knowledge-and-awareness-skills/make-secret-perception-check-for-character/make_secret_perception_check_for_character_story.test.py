"""
Story: Make Secret Perception Check for Character (scenario fidelity - tier-neutral).
Actor: GM
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: make_secret_perception_check_for_character_test_helper.{tier}.py implements MakeSecretPerceptionCheckForCharacterHelper.
"""

from __future__ import annotations

from typing import Protocol


class MakeSecretPerceptionCheckForCharacterHelper(Protocol):
    ...


def create_make_secret_perception_check_for_character_story(h: "MakeSecretPerceptionCheckForCharacterHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
