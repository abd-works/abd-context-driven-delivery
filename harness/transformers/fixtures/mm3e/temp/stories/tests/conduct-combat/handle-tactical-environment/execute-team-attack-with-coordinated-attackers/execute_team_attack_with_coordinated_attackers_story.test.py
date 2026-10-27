"""
Story: Execute Team Attack with Coordinated Attackers (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: execute_team_attack_with_coordinated_attackers_test_helper.{tier}.py implements ExecuteTeamAttackWithCoordinatedAttackersHelper.
"""

from __future__ import annotations

from typing import Protocol


class ExecuteTeamAttackWithCoordinatedAttackersHelper(Protocol):
    ...


def create_execute_team_attack_with_coordinated_attackers_story(h: "ExecuteTeamAttackWithCoordinatedAttackersHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
