"""Clean Engineering generator - multi-fidelity OO design and implementation."""

from __future__ import annotations

from cdd_guidance.practices.clean_engineering.model.drawio.drawio import Drawio
from cdd_guidance.practices.clean_engineering.model.drawio.drawio_class_model import DrawIOCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.java.java_class_model import JavaCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.javascript.javascript_class_model import JavaScriptCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.json.json_class_model import JsonCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.python.python_class_model import PythonCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.sketch.sketch_class_model import SketchCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.typescript.typescript_class_model import TypeScriptCleanEngineeringModel
from harness.agent_tools.agent_tools import agent_instructions, agent_toolset, tools
from harness.guidance.guidance import PracticeGuidance, rules_in


@agent_toolset
class CleanEngineering(PracticeGuidance):
    """# Instructions"""

    sketch_titles = ("ce:", "clean engineering:")
    SHORT_NAME = "CE"
    COLOUR = "#4FC3F7"

    # How the catalog shows this practice; the generator discovers it like the installer does.
    catalog_card = {
        "name": "Clean Engineering",
        "label": "clean-engineering",
        "family": "aad-fam-arc",
        "perspective": "arc",
        "order": 20,
        "blurb": "Highest quality software through modularized architecture and clean code that is resilient to change.",
        "spec_blurb": "Deep modules with explicit, narrow seams defined using code-level, type-safe contracts",
    }

    def __init__(
        self,
        fidelity: str = "modules",
        format: str | None = None,
    ) -> None:
        super().__init__(
            format=format,
            fidelity=fidelity,
            default_workspace_folder="src",
            formats={
                "markdown": MarkdownCleanEngineeringModel,
                "json": JsonCleanEngineeringModel,
                "python": PythonCleanEngineeringModel,
                "typescript": TypeScriptCleanEngineeringModel,
                "java": JavaCleanEngineeringModel,
                "javascript": JavaScriptCleanEngineeringModel,
                "drawio": DrawIOCleanEngineeringModel,
                "sketch": SketchCleanEngineeringModel,
            },
        )
        self._drawio: Drawio | None = None

    # In the knowledge graph: Clean Engineering's modules, classes, and members, its rules, and the draw.io rules it
    # checks on a diagram's nodes.
    class_types = ("OoadClass",)
    member_types = ("Operation", "Property")
    class_node_type = "OoadClass"
    anchor_types = {
        "module": "Module",
        "class": "OoadClass",
        "property": "Property",
        "operation": "Operation",
        "parameter": "Parameter",
        "package": "Package",
    }

    def own_graph_checks(self) -> dict:
        return {**super().own_graph_checks(), **self.language_checks("drawio")}

    def language_checks(self, language: str) -> dict:
        return rules_in(f"{self.package}.model.drawio.rules") if language == "drawio" else {}

    def read_working_copy(self) -> None:
        """Read each source file with its language's class model, adding the folders, classes, properties, operations,
        and parameters it parsed as nodes, and keep the members the model documents describe on the practice's root."""
        from cdd_guidance.practices.clean_engineering.model.graph_reading import read_code_and_models

        read_code_and_models(self)

    @property
    def drawio(self) -> Drawio:
        """The Draw.io toolset this practice renders its diagrams with."""
        if self._drawio is None:
            self._drawio = Drawio()
            self._drawio.mode = "tool"
        return self._drawio

    @agent_instructions
    def generate_output(self) -> str:
        """Write the fidelity artifact under the session.

        When ``format`` is ``drawio``, call ``drawio.render`` (create diagram →
        scan layout rules in drawio contexts → repair sub-agent on definitive
        layout failures). Otherwise produce the active channel output
        (markdown / python / …) from contexts, examples, and templates — do
        not invoke drawio.render.
        """
        if self.format == "drawio":
            tools(self.drawio.render())
        return "Artifact written under {session.path}/."
    