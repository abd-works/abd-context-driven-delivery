# @toolset-manifest python -m tools manifest context_tools.cdd.cdd:Cdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity discovery
# invoke-edit: action satisfy | toolset: context_tools.cdd.cdd:Cdd
# invoke-check: action validate | toolset: context_tools.cdd.cdd:Cdd
"""CDD orchestrator — stage menu across stories, ddd, ux, clean_engineering, bdd."""

from __future__ import annotations

import inspect
from pathlib import Path

from primitives.actions.action import action
from context_tools import base_context_tool
from context_tools.bdd.bdd import Bdd
from context_tools.clean_engineering.clean_engineering import CleanEngineering
from context_tools.ddd.ddd import Ddd
from context_tools.stories.stories import Stories
from context_tools.ux.ux import Ux
from primitives.instructions import Instruction
from primitives.instructions import instruction
from sketch import Sketcher
from tools.tool import tool  # noqa: F401

_FORMAT = {
    "discovery": "markdown",
    "explore": "markdown",
    "spec": "python",
    "engineer": "python",
}

# Stage → (concept class, child fidelity). AI may reorder / skip.
_STAGES: dict[str, list[tuple[type, str]]] = {
    "discovery": [
        (Stories, "discovery"),
        (Ddd, "bounded_context"),
        (Ux, "ia"),
        (CleanEngineering, "modules"),
    ],
    "explore": [
        (Ddd, "building_blocks"),
        (Stories, "exploration"),
        (Ux, "mockup"),
        (CleanEngineering, "model"),
        (Bdd, "behavior"),
    ],
    "spec": [
        (Ddd, "code"),
        (Stories, "specification"),
        (Ux, "specification"),
        (CleanEngineering, "specification"),
        (Bdd, "development"),
    ],
    "engineer": [
        (Ddd, "code"),
        (Stories, "engineering"),
        (CleanEngineering, "code"),
        (Bdd, "development"),
    ],
}


@base_context_tool
class Cdd:
    """§ Instructions"""

    def __init__(
        self,
        fidelity: str = "discovery",
        format: str | None = None,
        path: str | None = None, session: str | None = None,
    ) -> None:
        if fidelity not in _STAGES:
            raise ValueError(
                f"Unsupported fidelity {fidelity!r}. Choose from: {sorted(_STAGES)}"
            )
        super().__init__(format=format or _FORMAT[fidelity], path=path, session=session)
        self.fidelity = fidelity

    @instruction
    def contexts(self) -> Instruction: ...

    @action
    def generate(self) -> str:
        """"""
        self.resolve_targets()
        return ""

    @action
    def generate_output(self) -> str:
        """"""
        self.resolve_targets()
        return ""

    @tool
    def resolve_targets(self, fidelity: str | None = None) -> list[dict]:
        """Resolve contexts for a stage (default: this instance).

        Each row: ``context``, ``fidelity``, ``sketch_template`` (for the one CDD sketch),
        and ``run`` (pipe to ``python -m tools run -``). Sketch from the templates first,
        then run chosen rows in any order.
        """
        stage = fidelity or self.fidelity
        if stage not in _STAGES:
            raise ValueError(
                f"Unsupported fidelity {stage!r}. Choose from: {sorted(_STAGES)}"
            )
        sketcher = Sketcher()
        rows = []
        for cls, child in _STAGES[stage]:
            name = cls.__module__.split(".")[1]
            toolset = f"{cls.__module__}:{cls.__name__}"
            agent_dir = str(Path(inspect.getfile(cls)).resolve().parent)
            rows.append(
                {
                    "context": name,
                    "fidelity": child,
                    "sketch_template": sketcher.find_template(agent_dir=agent_dir),
                    "run": {
                        "toolset": toolset,
                        "context": {"fidelity": child},
                        "action": "generate",
                        "arguments": {
                            "plan": f"CDD {stage} → {name}@{child}",
                            "slug": name.replace("_", "-"),
                        },
                    },
                }
            )
        return rows
