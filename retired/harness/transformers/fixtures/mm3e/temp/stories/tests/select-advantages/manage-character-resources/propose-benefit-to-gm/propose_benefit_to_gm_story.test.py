"""
Story: Propose Benefit to GM (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: propose_benefit_to_gm_test_helper.{tier}.py implements ProposeBenefitToGmHelper.
"""

from __future__ import annotations

from typing import Protocol


class ProposeBenefitToGmHelper(Protocol):
    ...


def create_propose_benefit_to_gm_story(h: "ProposeBenefitToGmHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
