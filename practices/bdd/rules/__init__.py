"""BDD graph rule classes."""

from practices.bdd.rules.observable_behavior import ObservableBehavior

RULES: tuple = (ObservableBehavior(),)
BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
