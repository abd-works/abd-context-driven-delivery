"""BDD graph rule classes."""

from cdd_guidance.practices.bdd.rules.spec_rules import SPEC_RULES

RULES: tuple = SPEC_RULES
BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
