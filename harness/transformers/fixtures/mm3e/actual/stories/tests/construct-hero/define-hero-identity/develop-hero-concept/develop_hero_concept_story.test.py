"""
Story: Develop Hero Concept (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: develop_hero_concept_test_helper.{tier}.py implements DevelopHeroConceptHelper.
"""

from __future__ import annotations

from typing import Protocol


class DevelopHeroConceptHelper(Protocol):
    ...


def create_develop_hero_concept_story(h: "DevelopHeroConceptHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_concept_is_recorded() -> None:
        """SCENARIO: concept is recorded"""
    tests['test_concept_is_recorded'] = test_concept_is_recorded

    return tests
