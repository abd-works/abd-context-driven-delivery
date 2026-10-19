"""CDD orchestrator — stage menu across stories, ddd, ux, clean engineering, and bdd."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance
from cdd_guidance.practices.bdd.bdd import Bdd
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.ddd.ddd import Ddd
from cdd_guidance.practices.stories.stories import Stories
from cdd_guidance.practices.ux.ux import Ux

_CONTEXT_TOOLS_BY_STAGE: dict[str, list[type]] = {
    "discovery": [Stories, Ddd, Ux, CleanEngineering],
    "spec": [Ddd, Stories, Ux, CleanEngineering, Bdd],
    "engineer": [Ddd, Stories, Ux, CleanEngineering, Bdd],
}


@agent_toolset
class Cdd(PracticeGuidance):
    """# Instructions"""

    def __init__(self, fidelity: str = "discovery", format: str | None = None) -> None:
        super().__init__(
            format=format,
            fidelity=fidelity,
            default_workspace_folder=".",
        )
