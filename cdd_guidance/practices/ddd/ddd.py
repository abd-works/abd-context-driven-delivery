"""DDD generator - domain emphasis, contexts, building blocks over clean_engineering."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class Ddd(PracticeGuidance):
    """# Instructions

    Depends on CleanEngineering (lazy import to avoid circular imports at
    module load time).
    """

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

    def _skip_inactive_fidelity(self, current_name: str | None, name: str) -> bool:
        del current_name, name
        return False

    def _parse_content(self, source_format: str, content):
        parsed = super()._parse_content(source_format, content)
        if self._canonical_format(source_format) in self._code_formats and isinstance(content, str):
            _take_doc_comments(parsed, content)
        if self._canonical_format(source_format) == "markdown" and not _has_aggregates(parsed):
            # Plain class-model markdown with no contexts or aggregates reads as Clean Engineering.
            from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import (
                MarkdownCleanEngineeringModel,
            )

            return MarkdownCleanEngineeringModel().parse(self._incoming(source_format, content))
        return parsed

    def _call_render(self, target, parsed, previous: str, keep_positioning: bool, workspace: str = ""):
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
        return super()._call_render(target, parsed, previous, keep_positioning, workspace)

    @property
    def model(self):
        from cdd_guidance.practices.ddd.model.transformation.ddd_transformer import DddTransformer

        class DddPracticeModel:
            transformer = DddTransformer

        return DddPracticeModel()


def _has_aggregates(parsed) -> bool:
    contexts = list(getattr(parsed, "contexts", []) or [])
    while contexts:
        context = contexts.pop()
        if context.aggregates:
            return True
        contexts.extend(context.contexts)
    return False


_DOC_COMMENT = r"/\*\*((?:(?!\*/)[\s\S])*)\*/\s*(?:@\w+(?:\([^)]*\))?\s*)*(?:export\s+)?(?:abstract\s+)?class\s+{name}\b"


def _take_doc_comments(parsed, text: str) -> None:
    # Brace-language parsers skip the JSDoc above a class; the aggregate model keeps its stereotypes and place there.
    import re

    for module in getattr(parsed, "modules", []):
        for oclass in module.classes:
            if oclass.intent:
                continue
            found = re.search(_DOC_COMMENT.format(name=re.escape(oclass.name)), text)
            if found is None:
                continue
            lines = [line.strip().lstrip("*").strip() for line in found.group(1).splitlines()]
            oclass.intent = "\n".join(line for line in lines if line)


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
