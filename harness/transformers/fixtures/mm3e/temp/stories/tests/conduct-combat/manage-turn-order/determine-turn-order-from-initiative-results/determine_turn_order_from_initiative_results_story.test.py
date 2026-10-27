"""
Story: Determine Turn Order from Initiative Results (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: determine_turn_order_from_initiative_results_test_helper.{tier}.py implements DetermineTurnOrderFromInitiativeResultsHelper.
"""

from __future__ import annotations

from typing import Protocol


class DetermineTurnOrderFromInitiativeResultsHelper(Protocol):
    ...


def create_determine_turn_order_from_initiative_results_story(h: "DetermineTurnOrderFromInitiativeResultsHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    def test_delay_or_ready_updates_only_that_participant() -> None:
        """SCENARIO: delay or ready updates only that participant"""
    tests['test_delay_or_ready_updates_only_that_participant'] = test_delay_or_ready_updates_only_that_participant

    return tests
