"""DDD generator - domain emphasis, contexts, building blocks over clean_engineering."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap
from cdd_guidance.practices.ddd.model.nodes import BoundedContextMap, DomainNode
from cdd_guidance.practices.ddd.model.stereotypes import BUILDING_BLOCK_KINDS
from cdd_guidance.practices.ddd.model.sketch.sketch_ddd_model import SketchDddModel


@agent_toolset
class Ddd(PracticeGuidance):
    """# Instructions"""

    # Its section of a sketch is the one its sketch format reads, held as that one lens.
    sketch_lens = SketchDddModel.lens
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

    # In the knowledge graph: DDD's nodes are read after Clean Engineering's classes, and it checks its rules with
    # Clean Engineering's.
    reads_after = ("clean_engineering",)
    # Its scoped markdown shows every fidelity, since a bounded context, its model and its tactics read as one.
    shows_every_fidelity = True
    extends = "clean_engineering"
    class_types = (*BUILDING_BLOCK_KINDS, "Aggregate", "DomainEvent")

    def own_graph_checks(self) -> dict:
        """DDD's own graph rules, then the rules of the practice it extends, which it holds."""
        extended = self.extended.graph_checks() if self.extended is not None else {}
        return {**super().own_graph_checks(), **extended}

    def read_working_copy(self) -> None:
        """Bounded contexts come from the folders that hold ``.context/bounded-context.md``, aggregates from the folders
        that hold domain classes, and building blocks from the classes Clean Engineering read, each seen through the DDD
        stereotype its declaration or name gives it."""
        from cdd_guidance.practices.ddd.model.graph_reading import DddReading

        DddReading(self).read()

    def _parse_content(self, source_format: str, content):
        """A text the map reads as a plain class model, with no aggregate in it, is read by the Clean Engineering
        practice this practice's fidelity has as its companion, through that practice's own adapter."""
        parsed = super()._parse_content(source_format, content)
        if isinstance(parsed, BoundedContextMap) and parsed.holds_classes_only:
            return self.clean_engineering_companion.practice_guidance._parse_content(source_format, content)
        return parsed

    def _model_for(self, target, parsed):
        """The code formats are Clean Engineering class models, which the map writes itself into as their own classes,
        so they render themselves; the DDD formats render the bounded-context map, which reads a class model back."""
        if isinstance(target, CleanEngineeringModel) and isinstance(parsed, BoundedContextMap):
            parsed.write_classes(target)
            return target
        if isinstance(target, BoundedContextMap) and isinstance(parsed, CleanEngineeringModel):
            return MarkdownBoundedContextMap().read_class_model(parsed)
        return parsed


DomainNode.register_practice(Ddd)
