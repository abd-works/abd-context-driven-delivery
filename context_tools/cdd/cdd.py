# @toolset-manifest python -m tools manifest context_tools.cdd.cdd:Cdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity discovery
# invoke-edit: action satisfy | toolset: context_tools.cdd.cdd:Cdd
# invoke-check: action validate | toolset: context_tools.cdd.cdd:Cdd
"""CDD orchestrator - stage menu across stories, ddd, ux, clean_engineering, bdd."""

from __future__ import annotations

from primitives.actions.action import action
from context_tools.base.base_context_tool import BaseContextTool
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

# Stage → ordered list of context tool classes for that stage.
# Child fidelity is looked up from each class's own ``fidelities`` dict
# using the same stage key — no inline (class, fidelity) pairs needed.
_CONTEXT_TOOLS_BY_STAGE: dict[str, list[type]] = {
    "discovery": [Stories, Ddd, Ux, CleanEngineering],
    "spec":      [Ddd, Stories, Ux, CleanEngineering, Bdd],
    "engineer":  [Ddd, Stories, Ux, CleanEngineering, Bdd],
}


class Cdd(BaseContextTool):
    """# Instructions"""

    fidelities = {
        BaseContextTool.DISCOVERY: "discovery",
        BaseContextTool.SPEC:      "spec",
        BaseContextTool.ENGINEER:  "engineer",
    }

    def __init__(
        self,
        fidelity: str = "discovery",
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
    ) -> None:
        if fidelity not in _CONTEXT_TOOLS_BY_STAGE:
            raise ValueError(
                f"Unsupported fidelity {fidelity!r}. Choose from: {sorted(_CONTEXT_TOOLS_BY_STAGE)}"
            )
        super().__init__(format=format or _FORMAT[fidelity], path=path, session=session)
        self.fidelity = fidelity


    # -- Context-tool provider -------------------------------------------------
    # Returns the ordered list of active context tool instances for this stage.
    # Each class's own ``fidelities`` dict maps the stage key to the child fidelity,
    # replacing the old inline (class, fidelity) tuples in _STAGES.

    def context_tools(self) -> list:
        stage = self.fidelity
        return [
            cls(fidelity=cls.fidelities[stage])
            for cls in _CONTEXT_TOOLS_BY_STAGE[stage]
        ]

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
