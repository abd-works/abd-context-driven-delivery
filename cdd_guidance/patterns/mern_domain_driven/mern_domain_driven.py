"""MernDomainDriven generator - implementation fidelity for a domain-module-organized
MERN stack (MongoDB / Express / React / Node) on an already-designed vertical slice."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset

from cdd_guidance.patterns.domain_driven_stack.domain_driven_stack import DomainDrivenStack


@agent_toolset
class MernDomainDriven(DomainDrivenStack):
    """The MERN stack: MongoDB, Express, React, and Node, in TypeScript, organized by domain module."""

    pattern = "mern_domain_driven"
