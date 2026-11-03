"""CDD web domain access graph rules on the DDD practice — loaded when the cdd_web_domain_access overlay is active."""

from cdd_guidance.patterns.cdd_web_domain_access.practices.ddd.rules.access_rules import (
    AdapterIsGenerated,
    AnnotateWhatTypeScriptReads,
    OneClassPerObject,
    StateLivesBehindTheTool,
)

RULES: tuple = (
    OneClassPerObject(),
    StateLivesBehindTheTool(),
    AdapterIsGenerated(),
    AnnotateWhatTypeScriptReads(),
)

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
