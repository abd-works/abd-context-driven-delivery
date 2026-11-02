"""LERN graph rules on the BDD practice — loaded when the lern_domain_driven overlay is active."""

from cdd_guidance.patterns.lern_domain_driven.practices.bdd.rules.shared_behavior_rules import (
    E2eRunsTheWholeStack,
    ServerTierCallsTheRealThing,
    SharedBehaviorStaysTierFree,
    TierRunsSharedBehavior,
)

RULES: tuple = (
    SharedBehaviorStaysTierFree(),
    TierRunsSharedBehavior(),
    ServerTierCallsTheRealThing(),
    E2eRunsTheWholeStack(),
)

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
