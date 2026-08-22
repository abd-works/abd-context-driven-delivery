# @toolset-manifest python -m tools manifest context_tools.engineering_specification.mern_domain_driven.mern_domain_driven:MernDomainDriven
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
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
    def generate(self) -> str:
        """1. Follow session_guidance (handled by the inherited body below). Fill
        templates/ for the feature package this slice touches ({epicSlug}/ with
        nested domain module + process boot) if not already present.
        2. Call self._stories().generate() - *_spec.{tier} for tier in
        (server, client, e2e), applying the testing-architecture rules below.
        Specs first — small RED cycles before production. Its own ce().generate()
        then wires the minimum matching production TypeScript under CE's OOAD
        rules plus the naming/layering rules below.
        3. Cite the ux screen/navigation artifact for this slice under Sources /
        context on the touched view files - this tool does not call ux itself.
        4. Run validate. If it fails, fix and validate again until it passes."""
        super().generate()
        self._stories().generate()
        return "Ran stories (acceptance tests + ce production) for this slice. Run validate."

    @agent_instructions
    def iterate(self) -> str:
        """One cycle: self._stories().iterate() (grill + one spec, RED, then its
        own ce().iterate() wires the minimum code until GREEN), then run this
        tool's own scan for MERN-specific naming/layering rules. Repeat - one
        test, one production change, one GREEN, one scan - until validate passes."""
        from iterate.iterate import Iterator

        Iterator().iterate(tools=[self])
        self._stories().iterate()
        return "Iterate cycle complete for this slice. Run validate."

    @agent_instructions
    def satisfy(self) -> str:
        """Find and fix every problem under this slice: call
        self._stories().satisfy() (specs first; its own ce().satisfy() keeps
        production GREEN). Run validate - it scans this tool's own MERN
        naming/layering rules below alongside CE's and Stories' rules - and
        repeat until it passes."""
        super().satisfy()
        self._stories().satisfy()
        return "Satisfied stories (acceptance tests + ce production) for this slice. Run validate."
