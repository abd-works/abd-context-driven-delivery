"""
Story: Persist Advantage Selections on Character Sheet (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: persist_advantage_selections_on_character_sheet_test_helper.{tier}.py implements PersistAdvantageSelectionsOnCharacterSheetHelper.
"""

from __future__ import annotations

from typing import Protocol


class PersistAdvantageSelectionsOnCharacterSheetHelper(Protocol):
    ...


def create_persist_advantage_selections_on_character_sheet_story(h: "PersistAdvantageSelectionsOnCharacterSheetHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
