"""LernDomainDriven generator - implementation fidelity for a domain-module-organized
LERN stack (lowdb JSON files / Express / React / Node) on an already-designed vertical slice.
Each aggregate owns its own JSON store; repositories load, create, search, and update
the aggregate root. See practices/ddd/ddd.md building_blocks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from practices.base.base_context_tool import BaseContextTool
from primitives.agent_tools.agent_tools import agent_instructions
from primitives.instructions import Instruction
from primitives.instructions import instruction

if TYPE_CHECKING:
    from practices.stories.stories import Stories


class LernDomainDriven(BaseContextTool):
    """# Instructions"""

    default_workspace_folder: str = "packages"
    context_index_key: str = "lern_domain_driven"

    def __init__(
        self,
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
    ) -> None:
        super().__init__(format="typescript", path=path, session=session, workspace=workspace)

    def _stories(self) -> "Stories":
        """Stories companion pinned at acceptance_tests fidelity, typescript format -
        writes *_spec.{tier} for tier in (server, client, e2e) and, via its own ce(),
        the matching TypeScript production code (ce() passes format through)."""
        from practices.stories.stories import Stories

        instance = Stories(
            fidelity="acceptance_tests",
            format="typescript",
            path=self._raw_path,
            session=(
                self.workspace.current_work_session.name
                if self.workspace.current_work_session
                else ""
            ),
            workspace=self.workspace.path,
        )
        instance.mode = "tool"
        return instance

    @instruction
    def contexts(self) -> Instruction: ...

    @agent_instructions
    def guidance(recipe) -> str:
        """1. Follow session_guidance (handled by the inherited body below). Fill
        templates/ for the feature package this slice touches ({epicSlug}/ with
        nested domain module + process boot + one lowdb JSON file per aggregate)
        if not already present.
        2. ask-cross-aggregate-sync — if this slice involves more than one
        aggregate, AskQuestion (event-based orchestration vs direct repository
        calls by the client) and record the answer in grill-answers.md before
        writing stories. Single-aggregate slices record single-aggregate.
        3. Call guidance on the Stories companion - *_spec.{tier} for tier in
        (server, client, e2e), applying the testing-architecture rules below.
        Specs first — small RED cycles before production. Pass that companion
        to this action as a separate tools run; the action already knows what
        to do for every tool, including the Stories CE companion.
        4. Cite the ux screen/navigation artifact for this slice under Sources /
        context on the touched view files - this tool does not call ux itself.
        5. Run validate. If it fails, fix and validate again until it passes.
        When this LERN work is done, call guidance on the Stories companion and pass that companion to this action as a separate tools run. The action already knows what to do for every tool. Do not inline."""
        super().guidance()
        self._stories().guidance()
        return (
            "When this LERN work is done, call guidance on the Stories companion "
            "and pass that companion to this action as a separate tools run. "
            "The action already knows what to do for every tool. Do not inline."
        )
