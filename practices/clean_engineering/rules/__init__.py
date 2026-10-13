"""Clean Engineering graph rules — code rules read the unified Operation model (all code channels)."""

from practices.clean_engineering.model.rules_shared.operation_checks import CODE_RULES
from practices.clean_engineering.rules.limit_operation_parameters import LimitOperationParameters

RULES: tuple = (LimitOperationParameters(),) + CODE_RULES

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
