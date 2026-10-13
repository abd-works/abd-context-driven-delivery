"""Story graph rule classes."""

from practices.stories.rules.four_to_nine_children import FourToNineChildren

RULES: tuple = (FourToNineChildren(),)
BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
