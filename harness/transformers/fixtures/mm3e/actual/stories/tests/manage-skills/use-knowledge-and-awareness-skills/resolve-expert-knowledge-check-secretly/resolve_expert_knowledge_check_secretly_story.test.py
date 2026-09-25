"""
Story: Resolve Expert Knowledge Check Secretly (scenario fidelity - tier-neutral).
Actor: GM
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: resolve_expert_knowledge_check_secretly_test_helper.{tier}.py implements ResolveExpertKnowledgeCheckSecretlyHelper.
"""

from __future__ import annotations

from typing import Protocol


class ResolveExpertKnowledgeCheckSecretlyHelper(Protocol):
    ...


def create_resolve_expert_knowledge_check_secretly_story(h: "ResolveExpertKnowledgeCheckSecretlyHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
