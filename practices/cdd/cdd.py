"""CDD orchestrator - stage menu across stories, ddd, ux, clean_engineering, bdd."""

from __future__ import annotations

from primitives.agent_tools.agent_tools import agent_instructions
from practices.base.base_context_tool import BaseContextTool
from practices.bdd.bdd import Bdd
from practices.clean_engineering.clean_engineering import CleanEngineering
from practices.ddd.ddd import Ddd
from practices.stories.stories import Stories
from practices.ux.ux import Ux

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

    def practices(self) -> list:
        stage = self.fidelity
        return [
            cls(fidelity=cls.fidelities[stage])
            for cls in _CONTEXT_TOOLS_BY_STAGE[stage]
        ]

    # -- Guidance --------------------------------------------------------------
    # Stage children are companions: list each as a tool-mode guidance run.
    # Kits own generate / validate / satisfy / document / grill / sketch / iterate.

    @agent_instructions
    def guidance(recipe) -> str:
        """Provide guidance for orchestrating CDD stages across stories, ddd, ux, clean_engineering, and bdd.
        Call guidance on each stage child and pass that child to this action as a separate tools run. The action already knows what to do for every tool. Do not inline."""
        super().guidance()
        for context_tool in self.practices():
            context_tool.mode = "tool"
            context_tool.guidance()
        return (
            "Call guidance on each stage child and pass that child to this action "
            "as a separate tools run. The action already knows what to do for every tool. "
            "Do not inline."
        )
