"""What the domain-driven TypeScript stack patterns (LERN, MERN) share."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.guidance.guidance import PracticeGuidance

if TYPE_CHECKING:
    from cdd_guidance.practices.stories.stories import Stories


class DomainDrivenStack(PracticeGuidance):
    """Implementation fidelity for a domain-module-organized TypeScript stack on an already-designed vertical slice. Its
    generate writes the acceptance tests first, through a Stories companion at acceptance_tests in TypeScript, and then
    the production code those tests drive."""

    # The folder of the shared step library the acceptance tests import; None keeps story-test.ts at the tests root.
    story_test_folder: str | None = None

    def __init__(self) -> None:
        super().__init__(format="typescript", default_workspace_folder="packages")

    def _stories(self) -> "Stories":
        """The Stories companion, made at acceptance_tests in TypeScript with this stack's step library folder. It runs
        as a tool inside this pattern's generate, so its recipes are listed rather than expanded inline."""
        from cdd_guidance.practices.stories.stories import Stories

        companion = Stories(fidelity="acceptance_tests", format="typescript", story_test_folder=self.story_test_folder)
        companion.mode = "tool"
        return companion
