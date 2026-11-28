"""AcmeDomainDriven: a pattern one project keeps in its own repository, in place of the LERN pattern CDD ships."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset

from cdd_guidance.patterns.pattern import Pattern


@agent_toolset
class AcmeDomainDriven(Pattern):
    """Aggregates that save themselves: no repository classes, an instance save and delete on the root."""
