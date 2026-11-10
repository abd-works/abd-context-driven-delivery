"""
Story: Apply Condition to Character (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: apply_condition_to_character_test_helper.{tier}.py implements ApplyConditionToCharacterHelper.
"""

from __future__ import annotations

from typing import Protocol


class ApplyConditionToCharacterHelper(Protocol):
    ...


def create_apply_condition_to_character_story(h: "ApplyConditionToCharacterHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_basic_condition_applies_its_game_modifier_while_active() -> None:
        """SCENARIO: basic condition applies its game modifier while active"""
    tests['test_basic_condition_applies_its_game_modifier_while_active'] = test_basic_condition_applies_its_game_modifier_while_active

    def test_combined_condition_applies_constituents() -> None:
        """SCENARIO: combined condition applies constituents"""
    tests['test_combined_condition_applies_constituents'] = test_combined_condition_applies_constituents

    def test_multiple_active_conditions_stack() -> None:
        """SCENARIO: multiple active conditions stack"""
    tests['test_multiple_active_conditions_stack'] = test_multiple_active_conditions_stack

    def test_dazed_limits_the_turn_to_free_plus_one_standard() -> None:
        """SCENARIO: dazed limits the turn to free plus one standard"""
    tests['test_dazed_limits_the_turn_to_free_plus_one_standard'] = test_dazed_limits_the_turn_to_free_plus_one_standard

    def test_vulnerable_halves_active_defenses_rounding_up() -> None:
        """SCENARIO: vulnerable halves active defenses rounding up"""
    tests['test_vulnerable_halves_active_defenses_rounding_up'] = test_vulnerable_halves_active_defenses_rounding_up

    return tests
