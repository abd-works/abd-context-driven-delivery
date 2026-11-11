"""LERN graph rules on the Stories practice — loaded when the lern_domain_driven overlay is active."""

from cdd_guidance.patterns.lern_domain_driven.practices.stories.rules.front_end_rules import UserStoriesHaveAFrontEnd
from cdd_guidance.patterns.lern_domain_driven.practices.stories.rules.shared_story_rules import (
    DomainOperationsInlineInSteps,
    NoExpectInGiven,
    OutlineEntriesLoopOverExamples,
    TierBoundRepositoryAccessor,
)

RULES: tuple = (
    TierBoundRepositoryAccessor(),
    NoExpectInGiven(),
    DomainOperationsInlineInSteps(),
    OutlineEntriesLoopOverExamples(),
    UserStoriesHaveAFrontEnd(),
)

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
