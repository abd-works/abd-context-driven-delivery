"""Clean Engineering graph rules — schema slugs with executable checks."""

from practices.clean_engineering.model.rules_shared.class_rules import KeepClassesSingleResponsibility
from practices.clean_engineering.model.rules_shared.operation_checks import CODE_RULES
from practices.clean_engineering.model.rules_shared.prefer_class_operations import PreferClassOperations
from practices.clean_engineering.model.rules_shared.typed_and_comments import LimitComments, UseTypedSignatures
from practices.clean_engineering.rules.limit_operation_parameters import LimitOperationParameters
from practices.clean_engineering.rules.module_graph_rules import NamedSeamAndConstraint, PublicSeamOnly

RULES: tuple = (
    LimitOperationParameters(),
    NamedSeamAndConstraint(),
    PublicSeamOnly(),
    PreferClassOperations(),
    KeepClassesSingleResponsibility(),
    UseTypedSignatures(),
    LimitComments(),
) + CODE_RULES

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
