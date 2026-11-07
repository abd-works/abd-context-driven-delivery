"""LernDomainDriven generator - implementation fidelity for a domain-module-organized
LERN stack (lowdb JSON files / Express / React / Node) on an already-designed vertical slice.
Each aggregate owns its own JSON store; repositories load, create, search, and update
the aggregate root. See practices/ddd/ddd.md model and tactics."""

from __future__ import annotations

from functools import cached_property

from harness.agent_tools.agent_tools import agent_toolset

from cdd_guidance.patterns.domain_driven_stack import DomainDrivenStack
from cdd_guidance.patterns.lern_domain_driven.graph_overlay import LernOverlay


@agent_toolset
class LernDomainDriven(DomainDrivenStack):
    """The LERN stack: lowdb JSON files, Express, React, and Node, in TypeScript, organized by domain module."""

    pattern = "lern_domain_driven"
    # The shared step library (story-test.ts, story-playwright.ts, my-paradise.ts, repositories.ts) sits outside tests/,
    # so tests/ holds only story-map folders.
    story_test_folder = "test-utils/story-test"

    @cached_property
    def graph_overlay(self) -> LernOverlay:
        """What this pattern gives the knowledge graph on top of the practices: each aggregate's tier files, the
        behavior and story test files, the context mappings, and the rules on them. Made once and kept."""
        return LernOverlay(self)
