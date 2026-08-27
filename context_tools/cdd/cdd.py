# @toolset-manifest python -m tools manifest context_tools.cdd.cdd:Cdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity discovery
# invoke-edit: action satisfy | toolset: context_tools.cdd.cdd:Cdd
# invoke-check: action validate | toolset: context_tools.cdd.cdd:Cdd
"""CDD orchestrator - stage menu across stories, ddd, ux, clean_engineering, bdd."""

from __future__ import annotations

from primitives.actions.action import agent_instructions
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
        fidelity = type(self).resolve_fidelity(fidelity)
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

    # -- Guidance --------------------------------------------------------------
    # Stage children are companions: list each as a tool-mode guidance run.
    # Kits own generate / validate / satisfy / document / grill / sketch / iterate.

    @agent_instructions
    def guidance(self) -> str:
        """Provide guidance for orchestrating CDD stages across stories, ddd, ux, clean_engineering, and bdd.
        Call guidance on each stage child and pass that child to this action as a separate tools run. The action already knows what to do for every tool. Do not inline."""
        super().guidance()
        for context_tool in self.context_tools():
            context_tool.mode = "tool"
            context_tool.guidance()
        return (
            "Call guidance on each stage child and pass that child to this action "
            "as a separate tools run. The action already knows what to do for every tool. "
            "Do not inline."
        )
