"""BDD generator - multi-fidelity behavior skeletons and development."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.guidance.guidance import PracticeGuidance

if TYPE_CHECKING:
    from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering


@agent_toolset
class Bdd(PracticeGuidance):
    """# Instructions"""

    sketch_titles = ("bdd:", "behavior driven development:")
    SHORT_NAME = "BDD"
    COLOUR = "#00B894"

    # How the catalog shows this practice; the generator discovers it like the installer does.
    catalog_card = {
        "name": "Behavior-Driven Development",
        "label": "behavior-driven-development",
        "family": "aad-fam-bdd",
        "perspective": "bdd",
        "order": 40,
        "blurb": "Specify domain logic through behavioural, automated tests.",
        "spec_blurb": "Nested describe/it behaviour tests that serve as both documentation and automated tests for domain logic",
    }

    def __init__(
        self,
        fidelity: str = "behavior",
        format: str | None = None,
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
                # A saved knowledge graph, read only: rendering from it draws the realization fidelity.
                "graph": ("cdd_guidance.practices.bdd.model.graph_bdd_model", "GraphBddModel"),
            },
        )

    # In the knowledge graph: BDD's describe trees, linked to the Clean Engineering members each observation drives.
    node_types = ("Spec", "Description", "Context", "Observation")

    def read_working_copy(self) -> None:
        """Each spec file's language model reads its describe tree, whose spec, descriptions, contexts, and observations
        are added to its graph as they are."""
        from cdd_guidance.practices.bdd.model.graph_reading import read_specs

        read_specs(self)

    def link_to_other_practices(self) -> None:
        """Link each observation to the operations and properties of the code it drives, when the graph reads Clean
        Engineering too."""
        from cdd_guidance.practices.bdd.model.graph_reading import ObservationLinks

        clean = self.clean_engineering_practice
        if clean is not None and clean in self.graph.practices.values():
            ObservationLinks(self, clean).link()

    @property
    def clean_engineering_practice(self) -> CleanEngineering | None:
        """The Clean Engineering practice the graph this practice is read in holds: the code each observation drives."""
        from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering

        held = self.graph.every_practice.values() if self.graph is not None else ()
        return next((practice for practice in held if isinstance(practice, CleanEngineering)), None)

