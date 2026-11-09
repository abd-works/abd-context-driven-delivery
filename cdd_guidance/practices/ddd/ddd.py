"""DDD generator - domain emphasis, contexts, building blocks over clean_engineering."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance

from cdd_guidance.practices.ddd.ddd_formats import DddFormats
from cdd_guidance.practices.ddd.model.graph_reading import DddReading
from cdd_guidance.practices.ddd.model.nodes import DomainNode
from cdd_guidance.practices.ddd.model.sketch.sketch_ddd_model import SketchDddModel


@agent_toolset
class Ddd(PracticeGuidance):
    """# Instructions"""

    # Its section of a sketch is the one its sketch format reads, held as that one lens.
    sketch_lens = SketchDddModel.lens
    # Its map reads and writes the Clean Engineering class models its code formats hold; and it takes part in the graph
    # through the bounded contexts, aggregates and building blocks it reads after Clean Engineering's classes.
    formats_type = DddFormats
    reading_type = DddReading
    SHORT_NAME = "DDD"
    COLOUR = "#6C5CE7"

    # How the catalog shows this practice; the generator discovers it like the installer does.
    catalog_card = {
        "name": "Domain-Driven Design",
        "label": "domain-driven-design",
        "product_engineering_label": "Domain-driven design",
        "family": "aad-fam-ddd",
        "perspective": "ddd",
        "order": 50,
        "blurb": "Organize the code around domain state, domain logic, and domain rules.",
        "spec_blurb": "An aggregate model of the core domain, then the building blocks that implement it",
    }

    def __init__(
        self,
        fidelity: str = "bounded_context",
        format: str | None = None,
    ) -> None:
        super().__init__(
            format=format,
            fidelity=fidelity,
            default_workspace_folder="src",
            formats={
                "sketch": ("cdd_guidance.practices.ddd.model.sketch.sketch_ddd_model", "SketchDddModel"),
                "drawio": (
                    "cdd_guidance.practices.ddd.model.drawio.drawio_bounded_context_map",
                    "DrawIOBoundedContextMap",
                ),
                "markdown": ("cdd_guidance.practices.ddd.model.markdown.nodes", "MarkdownBoundedContextMap"),
                "python": (
                    "cdd_guidance.practices.clean_engineering.model.python.python_class_model",
                    "PythonCleanEngineeringModel",
                ),
                "typescript": (
                    "cdd_guidance.practices.clean_engineering.model.typescript.typescript_class_model",
                    "TypeScriptCleanEngineeringModel",
                ),
            },
        )

    # Its scoped markdown shows every fidelity, since a bounded context, its model and its tactics read as one.
    shows_every_fidelity = True
    extends = "clean_engineering"


DomainNode.register_practice(Ddd)
