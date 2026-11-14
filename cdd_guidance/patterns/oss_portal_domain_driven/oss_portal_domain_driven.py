"""OssPortalDomainDriven generator - implementation fidelity for the Government of Bermuda OSS Portal architecture:
Angular SSR with a Node Backend-for-Frontend, Apigee X, and Cloud Run services that each own a Cloud SQL database,
laid out one folder per aggregate as the LERN pattern does. Every decision cites the OSS Portal Handover Pack v1.0."""

from __future__ import annotations

from functools import cached_property

from harness.agent_tools.agent_tools import agent_toolset

from cdd_guidance.patterns.domain_driven_stack.domain_driven_stack import DomainDrivenStack
from cdd_guidance.patterns.oss_portal_domain_driven.graph_overlay import OssPortalOverlay


@agent_toolset
class OssPortalDomainDriven(DomainDrivenStack):
    """The OSS Portal stack: Angular SSR and a Node Backend-for-Frontend, Apigee X, and Cloud Run services on Cloud SQL,
    in TypeScript, organized by aggregate."""

    pattern = "oss_portal_domain_driven"

    @cached_property
    def graph_overlay(self) -> OssPortalOverlay:
        """What this pattern gives the knowledge graph on top of the practices: each service with its proxy and
        migrations, each aggregate's tier files, the story test files, and the rules on them. Made once and kept."""
        return OssPortalOverlay(self)
