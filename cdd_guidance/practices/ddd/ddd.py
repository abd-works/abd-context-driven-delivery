"""DDD generator - domain emphasis, contexts, building blocks over clean_engineering."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance
from harness.markdown.format import Format


@agent_toolset
class Ddd(PracticeGuidance):
    """# Instructions

    Depends on CleanEngineering (lazy import to avoid circular imports at
    module load time).
    """

    sketch_titles = ("ddd:", "domain driven design:")
    SHORT_NAME = "DDD"
    COLOUR = "#6C5CE7"

    # How the catalog shows this practice; the generator discovers it like the installer does.
    catalog_card = {
        "name": "Domain-Driven Design",
        "label": "domain-driven-design",
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
        stage: str | None = None,
    ) -> None:
        super().__init__(
            format=format,
            fidelity=None if stage is not None else fidelity,
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
        if stage is not None:
            self._activate(stage=stage)

    # In the knowledge graph: DDD's nodes are read after Clean Engineering's classes, and it checks its rules with
    # Clean Engineering's.
    reads_after = ("clean_engineering",)
    extends = "clean_engineering"
    class_types = ("Entity", "EntityRoot", "ValueObject", "Aggregate", "Repository", "DomainEvent", "DomainService", "Specification")

    def own_graph_checks(self) -> dict:
        """DDD's own graph rules, then the rules of the practice it extends, which are the same in every graph."""
        from harness.guidance.practice_catalogue import PracticeCatalogue

        return {**super().own_graph_checks(), **PracticeCatalogue.practice(self.extends).graph_checks()}

    def read_working_copy(self, practice_graph) -> None:
        """Bounded contexts come from the folders that hold ``.context/bounded-context.md``, aggregates from the folders
        that hold domain classes, and building blocks from the classes Clean Engineering read, each seen through the DDD
        stereotype its declaration or name gives it."""
        from cdd_guidance.practices.ddd.model.graph_reading import read_contexts_and_blocks

        read_contexts_and_blocks(practice_graph)

    def _skip_inactive_fidelity(self, current_name: str | None, name: str) -> bool:
        del current_name, name
        return False

    def _parse_content(self, source_format: str, content):
        parsed = super()._parse_content(source_format, content)
        if Format(source_format).name == "markdown" and not _has_aggregates(parsed):
            # Plain class-model markdown with no contexts or aggregates reads as Clean Engineering.
            from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import (
                MarkdownCleanEngineeringModel,
            )

            return MarkdownCleanEngineeringModel().parse(self._incoming(source_format, content))
        return parsed

    def _model_for(self, target, parsed):
        # The code formats render Clean Engineering's class model; the DDD formats render the bounded-context map.
        from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel
        from cdd_guidance.practices.ddd.model.clean_engineering_bridge import (
            from_clean_engineering,
            to_clean_engineering,
        )
        from cdd_guidance.practices.ddd.model.nodes import BoundedContextMap

        if isinstance(target, CleanEngineeringModel) and isinstance(parsed, BoundedContextMap):
            parsed = to_clean_engineering(parsed)
            if type(target).__name__.startswith("Python"):
                _python_generics(parsed)
        elif isinstance(target, BoundedContextMap) and isinstance(parsed, CleanEngineeringModel):
            parsed = from_clean_engineering(parsed)
        return parsed


def _has_aggregates(parsed) -> bool:
    from cdd_guidance.practices.ddd.model.nodes import BoundedContextMap

    return isinstance(parsed, BoundedContextMap) and bool(parsed.every_aggregate)


def _python_generics(model) -> None:
    # `Collection<Root>` is not Python; the python channel needs `Collection[Root]` to read its own output back.
    def fixed(hint: str) -> str:
        return (hint or "").replace("<", "[").replace(">", "]")

    for module in model.modules:
        for oclass in module.classes:
            for prop in oclass.properties:
                prop.type_hint = fixed(prop.type_hint)
            for operation in oclass.operations:
                operation.return_type = fixed(operation.return_type)
                for parameter in operation.parameters:
                    parameter.type_hint = fixed(parameter.type_hint)
