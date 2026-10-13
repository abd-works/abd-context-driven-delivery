"""Python code-channel graph rules."""

from practices.clean_engineering.model.rules_shared.operation_checks import CODE_RULES

RULES: tuple = CODE_RULES
BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
