"""LernDomainDriven generator - implementation fidelity for a domain-module-organized
LERN stack (lowdb JSON files / Express / React / Node) on an already-designed vertical slice.
Each aggregate owns its own JSON store; repositories load, create, search, and update
the aggregate root. See practices/ddd/ddd.md model and tactics."""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING
from harness.agent_tools.agent_tools import agent_toolset

from cdd_guidance.patterns.domain_driven_stack.domain_driven_stack import DomainDrivenStack
from cdd_guidance.patterns.lern_domain_driven.graph_overlay import LernOverlay

if TYPE_CHECKING:
    from cdd_guidance.patterns.lern_domain_driven.practices.stories.model.claude_design.fixtures import LernCanvasFixtures


@agent_toolset
class LernDomainDriven(DomainDrivenStack):
    """The LERN stack: lowdb JSON files, Express, React, and Node, in TypeScript, organized by domain module."""

    # The shared step library (story-test.ts, story-playwright.ts, my-paradise.ts, repositories.ts) sits outside tests/,
    # so tests/ holds only story-map folders.
    story_test_folder = "test-utils/story-test"

    def canvas_fixtures(self, workspace: str | Path) -> "LernCanvasFixtures":
        """What builds the story canvas's fixtures bundle for the LERN project at workspace: its shared stories and
        their example fixtures, run through the pattern's story runtime, which it checks first."""
        from cdd_guidance.patterns.lern_domain_driven.practices.stories.model.claude_design.fixtures import LernCanvasFixtures

        return LernCanvasFixtures(workspace)

    @cached_property
    def graph_overlay(self) -> LernOverlay:
        """What this pattern gives the knowledge graph on top of the practices: each aggregate's tier files, the
        behavior and story test files, the context mappings, and the rules on them. Made once and kept."""
        return LernOverlay(self)
