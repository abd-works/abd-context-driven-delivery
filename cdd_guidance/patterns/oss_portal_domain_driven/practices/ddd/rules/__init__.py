"""OSS Portal graph rules on the DDD practice — loaded when the oss_portal_domain_driven overlay is active."""

from cdd_guidance.patterns.oss_portal_domain_driven.practices.ddd.rules.oss_tier_rules import (
    BffDecidesNextPage,
    BrowserCallsOnlyTheBff,
    ExpandAndContractMigrations,
    MaintainLayerPurity,
    NoCrossServiceTables,
    NoPersonalDataInLogs,
    OneProxyPerService,
    PublishEventsFromTheOwningService,
    RepositoryOwnsAggregateLifecycle,
    SanitisedErrorsOnly,
    SecretsFromSecretManager,
    StandardPolicyChain,
    TokensStayOnTheServer,
    VersionBreakingChanges,
    ViewsRenderOnly,
)

RULES: tuple = (
    BrowserCallsOnlyTheBff(),
    TokensStayOnTheServer(),
    ViewsRenderOnly(),
    MaintainLayerPurity(),
    BffDecidesNextPage(),
    RepositoryOwnsAggregateLifecycle(),
    NoCrossServiceTables(),
    SanitisedErrorsOnly(),
    PublishEventsFromTheOwningService(),
    SecretsFromSecretManager(),
    NoPersonalDataInLogs(),
    OneProxyPerService(),
    VersionBreakingChanges(),
    StandardPolicyChain(),
    ExpandAndContractMigrations(),
)

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
