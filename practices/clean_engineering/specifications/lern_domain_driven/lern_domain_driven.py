"""LernDomainDriven generator - implementation fidelity for a domain-module-organized
LERN stack (lowdb JSON files / Express / React / Node) on an already-designed vertical slice.
Each aggregate owns its own JSON store; repositories load, create, search, and update
the aggregate root. See practices/ddd/ddd.md building_blocks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.agent_tools.agent_tools import agent_instructions, agent_toolset
from harness.guidance.guidance import PracticeGuidance
from installation.harness_files.harness_files import Skill
from installation.mcp.mcp_server import Mcp

if TYPE_CHECKING:
    from practices.stories.stories import Stories


@agent_toolset
class LernDomainDriven(PracticeGuidance):
    """# Instructions"""

    domain_slug = "lern_domain_driven"
    default_workspace_folder: str = "packages"
    context_index_key: str = "lern_domain_driven"

    def __init__(
        self,
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
    ) -> None:
        super().__init__(
            format="typescript",
            path=path,
            session=session,
            workspace=workspace,
        )

    def _stories(self) -> "Stories":
        """Stories companion pinned at acceptance_tests fidelity, typescript format -
        writes *_spec.{tier} for tier in (server, client, e2e) and, via its own ce(),
        the matching TypeScript production code (ce() passes format through)."""
        from practices.stories.stories import Stories

        instance = Stories(
            fidelity="acceptance_tests",
            format="typescript",
            path=self.path,
            session=(
                self.workspace.current_work_session.name
                if self.workspace.current_work_session
                else ""
            ),
            workspace=self.workspace.path,
        )
        instance.mode = "tool"
        return instance

    @property
    @Mcp
    @Skill
    @agent_instructions
    def instructions(self) -> str:
        """Implementation fidelity for a domain-module-organized LERN stack (lowdb JSON files / Express / React / Node, TypeScript everywhere) on an already-designed vertical slice — story map, module boundaries, and screens all exist before this tool runs."""
        return super().instructions

    @property
    @agent_instructions
    def guidance(self) -> str:
        """Expand this practice's Guidance section, then Stories companion guidance."""
        super().guidance
        self._stories().guidance
        return (
            "When this LERN work is done, call guidance on the Stories companion "
            "and pass that companion to this action as a separate tools run. "
            "The action already knows what to do for every tool. Do not inline."
        )
