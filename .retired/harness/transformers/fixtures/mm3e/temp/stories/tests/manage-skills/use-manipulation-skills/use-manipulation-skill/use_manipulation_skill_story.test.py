"""
Story: Use Manipulation Skill (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: use_manipulation_skill_test_helper.{tier}.py implements UseManipulationSkillHelper.
"""

from __future__ import annotations

from typing import Protocol


class UseManipulationSkillHelper(Protocol):
    ...


def create_use_manipulation_skill_story(h: "UseManipulationSkillHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
