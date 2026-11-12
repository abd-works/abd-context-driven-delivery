"""OSS Portal graph rules on the Stories practice — loaded when the oss_portal_domain_driven overlay is active."""

from cdd_guidance.patterns.lern_domain_driven.practices.stories.rules.shared_story_rules import (
    NoExpectInGiven,
    OutlineEntriesLoopOverExamples,
)
from cdd_guidance.patterns.oss_portal_domain_driven.practices.stories.rules.oss_story_rules import (
    JourneyTestPerRelease,
    ServiceTierRunsARealDatabase,
)

RULES: tuple = (
    NoExpectInGiven(),
    OutlineEntriesLoopOverExamples(),
    ServiceTierRunsARealDatabase(),
    JourneyTestPerRelease(),
)

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
