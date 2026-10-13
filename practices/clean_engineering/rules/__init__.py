"""Clean-engineering graph rule classes (ported from historical scanners, model-first)."""

from practices.clean_engineering.rules.keep_operations_small import KeepOperationsSmall
from practices.clean_engineering.rules.limit_operation_parameters import LimitOperationParameters
from practices.clean_engineering.rules.never_swallow_exceptions import NeverSwallowExceptions
from practices.clean_engineering.rules.provide_meaningful_context import ProvideMeaningfulContext
from practices.clean_engineering.rules.simplify_control_flow import SimplifyControlFlow
from practices.clean_engineering.rules.use_exceptions_properly import UseExceptionsProperly
from practices.clean_engineering.rules.use_explicit_dependencies import UseExplicitDependencies

RULES: tuple = (
    LimitOperationParameters(),
    UseExplicitDependencies(),
    KeepOperationsSmall(),
    SimplifyControlFlow(),
    UseExceptionsProperly(),
    NeverSwallowExceptions(),
    ProvideMeaningfulContext(),
)

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
