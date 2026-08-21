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

    # -- Actions ---------------------------------------------------------------
    # grill / sketch: inline each child's high-level pass (action mode).
    # generate / iterate / validate / satisfy / document: set child mode=tool so
    # each is a separate tools run — never inline full child recipes.

    @action
    def generate_output(self) -> str:
        """Invoke each stage child's generate as its own tools run."""
        for context_tool in self.context_tools():
            context_tool.mode = "tool"
            context_tool.generate()
        return "Invoke each Separate tools run above, one child at a time."

    @action
    def grill(self) -> str:
        """Inline each stage child's grill via the grill kit (high-level Q&A only)."""
        from grill_context.grill_context import GrillContext

        grill = GrillContext()
        for context_tool in self.context_tools():
            grill.grill(tools=[context_tool])
        return ""

    @action
    def sketch(self) -> str:
        """Inline each stage child's sketch via the sketch kit (high-level shape only)."""
        from sketch.sketch import Sketcher

        sketcher = Sketcher()
        for context_tool in self.context_tools():
            sketcher.sketch(tools=[context_tool])
        return ""

    @action
    def iterate(self) -> str:
        """Invoke each stage child's iterate via the iterate kit."""
        from iterate.iterate import Iterator

        iterator = Iterator()
        for context_tool in self.context_tools():
            iterator.iterate(tools=[context_tool])
        return "Invoke each Separate tools run above, one child at a time."

    @action
    def validate(self) -> str:
        """Invoke each stage child's validate as its own tools run."""
        for context_tool in self.context_tools():
            context_tool.mode = "tool"
            context_tool.validate()
        return "Invoke each Separate tools run above, one child at a time."

    @action
    def satisfy(self) -> str:
        """Invoke each stage child's satisfy as its own tools run."""
        for context_tool in self.context_tools():
            context_tool.mode = "tool"
            context_tool.satisfy()
        return "Invoke each Separate tools run above, one child at a time."

    @action
    def document(self, paths: list[str]) -> str:
        """Invoke each stage child's document as its own tools run."""
        for context_tool in self.context_tools():
            context_tool.mode = "tool"
            context_tool.document(paths)
        return "Invoke each Separate tools run above, one child at a time."
