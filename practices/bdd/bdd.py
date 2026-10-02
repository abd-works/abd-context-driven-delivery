"""BDD generator - multi-fidelity behavior skeletons and development."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class Bdd(PracticeGuidance):
    """# Instructions

    Depends on CleanEngineering (lazy import to avoid circular imports at
    module load time).
    """

    def __init__(
        self,
        fidelity: str = "behavior",
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
    ) -> None:
        super().__init__(
            format=format,
            fidelity=fidelity,
            default_workspace_folder="src",
            formats={
                "sketch": ("practices.bdd.model.sketch.sketch_bdd_model", "SketchBddModel"),
                "knowledge_graph": (
                    "practices.bdd.model.knowledge_graph.nodes",
                    "KnowledgeGraphDescription",
                ),
                "markdown": ("practices.bdd.model.bdd_model", "MarkdownBddModel"),
                "python": ("practices.bdd.model.bdd_model", "PythonBddModel"),
                "typescript": ("practices.bdd.model.bdd_model", "TypeScriptBddModel"),
            },
        )
        if path is not None or session is not None:
            self._attach_workspace(path=path, session=session)

    @property
    def model(self):
        from practices.bdd.model.transformation.bdd_transformer import BddTransformer

        class BddPracticeModel:
            transformer = BddTransformer

        return BddPracticeModel()
