"""Clean Engineering graph rules — schema slugs with executable checks."""

from cdd_guidance.practices.clean_engineering.rules.class_rules import KeepClassesSingleResponsibility
from cdd_guidance.practices.clean_engineering.rules.coupling_rules import (
    DoNotInventParallelObjectModels,
    HideInnerDetails,
    LayerSeparation,
    ShapeClassesAroundResources,
)
from cdd_guidance.practices.clean_engineering.rules.operation_checks import CODE_RULES
from cdd_guidance.practices.clean_engineering.rules.prefer_class_operations import PreferClassOperations
from cdd_guidance.practices.clean_engineering.rules.typed_and_comments import LimitComments, UseTypedSignatures
from cdd_guidance.practices.clean_engineering.rules.limit_operation_parameters import LimitOperationParameters
from cdd_guidance.practices.clean_engineering.rules.module_graph_rules import (
    LanguageModulesOneSection,
    MissingModuleContext,
    ModulesNotModelBlocks,
    NamedSeamAndConstraint,
    PublicSeamOnly,
)
from cdd_guidance.practices.clean_engineering.rules.module_naming_rules import DomainNounsOnly, NoModulePerClass
from cdd_guidance.practices.clean_engineering.rules.no_prototype_swapping import NoPrototypeSwapping
from cdd_guidance.practices.clean_engineering.rules.write_interactions import WriteInteractions
from cdd_guidance.practices.clean_engineering.rules.practice_wide_rules import (
    DeepModule,
    ExtensionsLiveWithTheDomain,
    LowCoupling,
    OneWayDeps,
    SourceParses,
)

RULES: tuple = (
    LimitOperationParameters(),
    NamedSeamAndConstraint(),
    PublicSeamOnly(),
    MissingModuleContext(),
    LanguageModulesOneSection(),
    ModulesNotModelBlocks(),
    PreferClassOperations(),
    KeepClassesSingleResponsibility(),
    UseTypedSignatures(),
    LimitComments(),
    HideInnerDetails(),
    ShapeClassesAroundResources(),
    DoNotInventParallelObjectModels(),
    LayerSeparation(),
    OneWayDeps(),
    SourceParses(),
    LowCoupling(),
    DeepModule(),
    ExtensionsLiveWithTheDomain(),
    DomainNounsOnly(),
    NoModulePerClass(),
    WriteInteractions(),
    NoPrototypeSwapping(),
) + CODE_RULES

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
