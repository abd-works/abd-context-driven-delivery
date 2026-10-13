"""DDD graph rule classes."""

from practices.ddd.rules.tactical import FlaccidDataObject, PrivateMethodNaming

RULES: tuple = (PrivateMethodNaming(), FlaccidDataObject())
BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
