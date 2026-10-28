"""LernDomainDriven generator - implementation fidelity for a domain-module-organized
LERN stack (lowdb JSON files / Express / React / Node) on an already-designed vertical slice.
Each aggregate owns its own JSON store; repositories load, create, search, and update
the aggregate root. See practices/ddd/ddd.md model and tactics."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance

if TYPE_CHECKING:
    from cdd_guidance.practices.stories.stories import Stories


@agent_toolset
class LernDomainDriven(PracticeGuidance):
    """# Instructions"""

    pattern = "lern_domain_driven"
    # The shared step library (story-test.ts, story-playwright.ts, my-paradise.ts, repositories.ts) sits outside tests/,
    # so tests/ holds only story-map folders.
    story_test_folder = "test-utils/story-test"

    def __init__(self) -> None:
        super().__init__(
            format="typescript",
            default_workspace_folder="packages",
        )

    def _stories(self) -> "Stories":
        """Stories companion pinned at acceptance_tests fidelity, typescript format."""
        from cdd_guidance.practices.stories.stories import Stories

        instance = Stories(
            fidelity="acceptance_tests",
            format="typescript",
        )
        instance.mode = "tool"
        instance.story_test_folder = self.story_test_folder
        return instance
