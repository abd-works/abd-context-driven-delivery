"""LernDomainDriven generator - implementation fidelity for a domain-module-organized
LERN stack (lowdb JSON files / Express / React / Node) on an already-designed vertical slice.
Each aggregate owns its own JSON store; repositories load, create, search, and update
the aggregate root. See practices/ddd/ddd.md building_blocks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance

if TYPE_CHECKING:
    from practices.stories.stories import Stories


@agent_toolset
class LernDomainDriven(PracticeGuidance):
    """# Instructions"""

    def __init__(self) -> None:
        super().__init__(
            format="typescript",
            default_workspace_folder="packages",
        )

    def _stories(self) -> "Stories":
        """Stories companion pinned at acceptance_tests fidelity, typescript format."""
        from practices.stories.stories import Stories

        instance = Stories(
            fidelity="acceptance_tests",
            format="typescript",
        )
        instance.mode = "tool"
        return instance
