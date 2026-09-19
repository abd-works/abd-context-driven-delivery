"""MernDomainDriven generator - implementation fidelity for a domain-module-organized
MERN stack (MongoDB / Express / React / Node) on an already-designed vertical slice."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.agent_tools.agent_tools import agent_instructions, agent_toolset
from harness.guidance.guidance import PracticeGuidance
from installation.harness_files.harness_files import Skill
from installation.mcp.mcp_server import Mcp

if TYPE_CHECKING:
    from practices.stories.stories import Stories


@agent_toolset
class MernDomainDriven(PracticeGuidance):
    """# Instructions"""

    domain_slug = "mern_domain_driven"
    default_workspace_folder: str = "packages"
    context_index_key: str = "mern_domain_driven"

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
        """Stories companion pinned at acceptance_tests fidelity, typescript format."""
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
        """Implementation fidelity for a domain-module-organized MERN stack (MongoDB / Express / React / Node, TypeScript everywhere) on an already-designed vertical slice — story map, module boundaries, and screens all exist before this tool runs."""
        return super().instructions
