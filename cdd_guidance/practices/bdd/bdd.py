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

    # How the catalog shows this practice; the generator discovers it like the installer does.
    catalog_card = {
        "name": "Behavior-Driven Development",
        "label": "behavior-driven-development",
        "family": "aad-fam-sdd",
        "perspective": "bdd",
        "order": 40,
        "blurb": "Specify domain logic through behavioural, automated tests.",
        "spec_blurb": "Nested describe/it behaviour tests that serve as both documentation and automated tests for domain logic",
    }

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
                "sketch": ("cdd_guidance.practices.bdd.model.sketch.sketch_bdd_model", "SketchBddModel"),
                "markdown": ("cdd_guidance.practices.bdd.model.bdd_model", "MarkdownBddModel"),
                "python": ("cdd_guidance.practices.bdd.model.code_spec_model", "PythonBddModel"),
                "typescript": ("cdd_guidance.practices.bdd.model.code_spec_model", "TypeScriptBddModel"),
            },
        )
        if path is not None or session is not None:
            self._attach_workspace(path=path, session=session)

    @property
    def model(self):
        from cdd_guidance.practices.bdd.model.transformation.bdd_transformer import BddTransformer

        class BddPracticeModel:
            transformer = BddTransformer

        return BddPracticeModel()
