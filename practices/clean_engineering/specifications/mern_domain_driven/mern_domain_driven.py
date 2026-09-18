"""MernDomainDriven generator - implementation fidelity for a domain-module-organized
MERN stack (MongoDB / Express / React / Node) on an already-designed vertical slice."""

from __future__ import annotations

from typing import TYPE_CHECKING

from practices.workspace_bind import init_practice_guidance
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
        init_practice_guidance(
            self,
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
        """1. Follow session_guidance (handled by the inherited body below). Fill
        templates/ for the feature package this slice touches ({epicSlug}/ with
        nested domain module + process boot) if not already present.
        2. Call guidance on the Stories companion - *_spec.{tier} for tier in
        (server, client, e2e), applying the testing-architecture rules below.
        Specs first — small RED cycles before production. Pass that companion
        to this action as a separate tools run; the action already knows what
        to do for every tool, including the Stories CE companion.
        3. Cite the ux screen/navigation artifact for this slice under Sources /
        context on the touched view files - this tool does not call ux itself.
        4. Run validate. If it fails, fix and validate again until it passes.
        When this MERN work is done, call guidance on the Stories companion and pass that companion to this action as a separate tools run. The action already knows what to do for every tool. Do not inline."""
        return super().instructions

    @property
    @agent_instructions
    def guidance(self) -> str:
        """Expand this practice's Guidance section, then Stories companion guidance."""
        super().guidance
        self._stories().guidance
        return (
            "When this MERN work is done, call guidance on the Stories companion "
            "and pass that companion to this action as a separate tools run. "
            "The action already knows what to do for every tool. Do not inline."
        )
