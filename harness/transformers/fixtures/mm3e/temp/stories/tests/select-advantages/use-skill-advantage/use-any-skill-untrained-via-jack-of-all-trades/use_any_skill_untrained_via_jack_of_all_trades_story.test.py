"""
Story: Use Any Skill Untrained via Jack of All Trades (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: use_any_skill_untrained_via_jack_of_all_trades_test_helper.{tier}.py implements UseAnySkillUntrainedViaJackOfAllTradesHelper.
"""

from __future__ import annotations

from typing import Protocol


class UseAnySkillUntrainedViaJackOfAllTradesHelper(Protocol):
    ...


def create_use_any_skill_untrained_via_jack_of_all_trades_story(h: "UseAnySkillUntrainedViaJackOfAllTradesHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
