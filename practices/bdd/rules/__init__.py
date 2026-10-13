"""BDD graph rule classes."""

from practices.bdd.rules.spec_rules import SPEC_RULES

RULES: tuple = SPEC_RULES
BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
