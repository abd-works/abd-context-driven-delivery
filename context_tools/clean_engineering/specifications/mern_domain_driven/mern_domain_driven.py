# @toolset-manifest python -m tools manifest context_tools.engineering_specification.mern_domain_driven.mern_domain_driven:MernDomainDriven
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
# invoke-new: action generate
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""MernDomainDriven generator - implementation fidelity for a domain-module-organized
MERN stack (MongoDB / Express / React / Node) on an already-designed vertical slice."""

from __future__ import annotations

from typing import TYPE_CHECKING

from context_tools.base.base_context_tool import BaseContextTool
from primitives.actions.action import agent_instructions
from primitives.instructions import Instruction
from primitives.instructions import instruction

if TYPE_CHECKING:
    from context_tools.stories.stories import Stories


class MernDomainDriven(BaseContextTool):
    """# Instructions"""

    default_workspace_folder: str = "packages"
    context_index_key: str = "mern_domain_driven"

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
        from context_tools.stories.stories import Stories

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
    def guidance(self) -> str:
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
        super().guidance()
        self._stories().guidance()
        return (
            "When this MERN work is done, call guidance on the Stories companion "
            "and pass that companion to this action as a separate tools run. "
            "The action already knows what to do for every tool. Do not inline."
        )
