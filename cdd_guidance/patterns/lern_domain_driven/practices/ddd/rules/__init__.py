"""LERN graph rules on the DDD practice — loaded when the lern_domain_driven overlay is active."""

from cdd_guidance.patterns.lern_domain_driven.practices.ddd.rules.lern_tier_rules import (
    NodeRepositoryParsesOnRead,
    OneHomeForWebPaths,
    PostedBodyParsedInNode,
    ResetEveryRepository,
    ThrowHttpExceptions,
)

RULES: tuple = (
    NodeRepositoryParsesOnRead(),
    PostedBodyParsedInNode(),
    ThrowHttpExceptions(),
    OneHomeForWebPaths(),
    ResetEveryRepository(),
)

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
