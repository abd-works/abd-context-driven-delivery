"""UX graph rule classes."""

from cdd_guidance.practices.ux.rules.screen_rules import ScreenNamesUseDomainTerms, ScreenStoryBudget

RULES: tuple = (ScreenStoryBudget(), ScreenNamesUseDomainTerms())
BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
