"""CDD access graph rules on the DDD practice — loaded when the cdd_access overlay is active."""

from cdd_guidance.patterns.cdd_access.practices.ddd.rules.access_rules import (
    AdapterIsGenerated,
    AnnotateWhatTypeScriptReads,
    ConnectionOnlyCarries,
    NodeExtendsTheAdapter,
    OneClassPerObject,
    RoutesAskTheObject,
    StateLivesBehindTheTool,
    TextThatIsNotJsonIsAFailure,
)

RULES: tuple = (
    RoutesAskTheObject(),
    OneClassPerObject(),
    NodeExtendsTheAdapter(),
    StateLivesBehindTheTool(),
    ConnectionOnlyCarries(),
    TextThatIsNotJsonIsAFailure(),
    AdapterIsGenerated(),
    AnnotateWhatTypeScriptReads(),
)

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
