"""Language-agnostic Clean Engineering graph rules (module/package graph shape)."""

from practices.clean_engineering.rules.limit_operation_parameters import LimitOperationParameters

RULES: tuple = (LimitOperationParameters(),)

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
