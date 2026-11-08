"""
Story: Make Attack Check Against Defense (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: make_attack_check_against_defense_test_helper.{tier}.py implements MakeAttackCheckAgainstDefenseHelper.
"""

from __future__ import annotations

from typing import Protocol


class MakeAttackCheckAgainstDefenseHelper(Protocol):
    ...


def create_make_attack_check_against_defense_story(h: "MakeAttackCheckAgainstDefenseHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_close_targets_parry() -> None:
        """SCENARIO: close targets Parry"""
    tests['test_close_targets_parry'] = test_close_targets_parry

    def test_ranged_targets_dodge() -> None:
        """SCENARIO: ranged targets Dodge"""
    tests['test_ranged_targets_dodge'] = test_ranged_targets_dodge

    return tests
