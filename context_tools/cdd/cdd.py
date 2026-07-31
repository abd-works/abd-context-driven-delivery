# @toolset-manifest python -m tools manifest context_tools.cdd.cdd:Cdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity discovery
# invoke-edit: action satisfy | toolset: context_tools.cdd.cdd:Cdd
# invoke-check: action validate | toolset: context_tools.cdd.cdd:Cdd
"""CDD orchestrator - stage menu across stories, ddd, ux, clean_engineering, bdd."""

from __future__ import annotations

from primitives.actions.action import action
from context_tools import base_context_tool
from context_tools.bdd.bdd import Bdd
from context_tools.clean_engineering.clean_engineering import CleanEngineering
from context_tools.ddd.ddd import Ddd
from context_tools.stories.stories import Stories
from context_tools.ux.ux import Ux

_FORMAT = {
    "discovery": "markdown",
    "explore":   "markdown",
    "spec":      "python",
    "engineer":  "python",
}

# Stage -> ordered (ContextClass, child_fidelity).
# This is the complete fidelity contract. AI may reorder or skip rows.
_STAGES: dict[str, list[tuple[type, str]]] = {
    "discovery": [
        (Stories,          "discovery"),
        (Ddd,              "bounded_context"),
        (Ux,               "ia"),
        (CleanEngineering, "modules"),
    ],
    "explore": [
        (Ddd,              "building_blocks"),
        (Stories,          "exploration"),
        (Ux,               "mockup"),
        (CleanEngineering, "model"),
        (Bdd,              "behavior"),
    ],
    "spec": [
        (Ddd,              "code"),
        (Stories,          "exploration"),   # specification absorbed into exploration (optional variations)
        (Ux,               "mockup"),        # specification absorbed into mockup (stubs + optional brand)
        (CleanEngineering, "code"),          # specification fidelity retired; Phase 1 typed contracts are "code"
        (Bdd,              "development"),
    ],
    "engineer": [
        (Ddd,              "code"),
        (Stories,          "engineering"),
        (CleanEngineering, "code"),
        (Bdd,              "development"),
    ],
}


@base_context_tool
class Cdd:
    """# Instructions"""

    def __init__(
        self,
        fidelity: str = "discovery",
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
    ) -> None:
        if fidelity not in _STAGES:
            raise ValueError(
                f"Unsupported fidelity {fidelity!r}. Choose from: {sorted(_STAGES)}"
            )
        super().__init__(format=format or _FORMAT[fidelity], path=path, session=session)
        self.fidelity = fidelity


    # -- Context-tool provider -------------------------------------------------
    # Returns the ordered list of active context tool instances for this stage.
    # The for-each expander calls this at expansion time and walks each instance's
    # named @action method inline - embedding its full decorator stack automatically.

    def context_tools(self) -> list:
        return [cls(fidelity=fidelity) for cls, fidelity in _STAGES[self.fidelity]]

    # -- Actions ---------------------------------------------------------------
    # Each action body is a single for-each loop over context_tools().
    # The expander iterates the live list and walks <tool>.<action> on each instance,
    # embedding that child's full instruction set (including its own decorators) inline.

    @action
    def generate_output(self) -> str:
        for context_tool in self.context_tools():
            context_tool.generate()
        return ""

    @action
    def grill(self) -> str:
        for context_tool in self.context_tools():
            context_tool.grill()
        return ""

    @action
    def sketch(self) -> str:
        for context_tool in self.context_tools():
            context_tool.sketch()
        return ""

    @action
    def iterate(self) -> str:
        for context_tool in self.context_tools():
            context_tool.iterate()
        return ""

    @action
    def validate(self) -> str:
        for context_tool in self.context_tools():
            context_tool.validate()
        return ""

    @action
    def satisfy(self) -> str:
        for context_tool in self.context_tools():
            context_tool.satisfy()
        return ""

    @action
    def document(self, paths: list[str]) -> str:
        for context_tool in self.context_tools():
            context_tool.document(paths)
        return ""
