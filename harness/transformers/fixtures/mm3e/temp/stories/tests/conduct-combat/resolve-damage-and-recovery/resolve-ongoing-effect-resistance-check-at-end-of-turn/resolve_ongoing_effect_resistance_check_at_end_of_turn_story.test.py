"""
Story: Resolve Ongoing Effect Resistance Check at End of Turn (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: resolve_ongoing_effect_resistance_check_at_end_of_turn_test_helper.{tier}.py implements ResolveOngoingEffectResistanceCheckAtEndOfTurnHelper.
"""

from __future__ import annotations

from typing import Protocol


class ResolveOngoingEffectResistanceCheckAtEndOfTurnHelper(Protocol):
    ...


def create_resolve_ongoing_effect_resistance_check_at_end_of_turn_story(h: "ResolveOngoingEffectResistanceCheckAtEndOfTurnHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
