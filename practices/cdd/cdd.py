"""CDD orchestrator - stage menu across stories, ddd, ux, clean_engineering, bdd."""

from __future__ import annotations

from practices.stages import DISCOVERY, ENGINEER, SPEC, resolve_stage_fidelity
from practices.workspace_bind import init_practice_guidance
from primitives.agent_tools.agent_tools import agent_instructions, agent_toolset
from primitives.guidance.guidance import PracticeGuidance
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


@agent_toolset
class Cdd(PracticeGuidance):
    """# Instructions"""

    domain_slug = "cdd"
    STAGE_TO_FIDELITY = {
        DISCOVERY: "discovery",
        SPEC: "spec",
        ENGINEER: "engineer",
    }

    @classmethod
    def resolve_fidelity(cls, fidelity: str) -> str:
        return resolve_stage_fidelity(fidelity, cls.STAGE_TO_FIDELITY)

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
        init_practice_guidance(
            self,
            format=format or _FORMAT[fidelity],
            path=path,
            session=session,
            fidelity=fidelity,
            stage_to_fidelity=self.STAGE_TO_FIDELITY,
        )


    # -- Context-tool provider -------------------------------------------------
    # Returns the ordered list of active context tool instances for this stage.
    # Each class's own ``fidelities`` dict maps the stage key to the child fidelity,
    # replacing the old inline (class, fidelity) tuples in _STAGES.

    def practices(self) -> list:
        stage = self.fidelity
        return [
            cls(fidelity=cls.STAGE_TO_FIDELITY[stage])
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
        for context_tool in self.practices():
            context_tool.mode = "tool"
            context_tool.guidance()
        return (
            "Call guidance on each stage child and pass that child to this action "
            "as a separate tools run. The action already knows what to do for every tool. "
            "Do not inline."
        )
