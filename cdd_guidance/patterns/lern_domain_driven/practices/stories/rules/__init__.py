"""LERN graph rules on the Stories practice — loaded when the lern_domain_driven overlay is active."""

from cdd_guidance.patterns.lern_domain_driven.practices.stories.rules.shared_story_rules import (
    NoExpectInGiven,
    TierBoundRepositoryAccessor,
)

RULES: tuple = (
    TierBoundRepositoryAccessor(),
    NoExpectInGiven(),
)

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
