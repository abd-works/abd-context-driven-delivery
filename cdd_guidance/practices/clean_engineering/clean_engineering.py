"""Clean Engineering generator - multi-fidelity OO design and implementation."""

from __future__ import annotations

from cdd_guidance.practices.clean_engineering.clean_engineering_formats import CleanEngineeringFormats
from cdd_guidance.practices.clean_engineering.model.drawio.drawio import Drawio
from cdd_guidance.practices.clean_engineering.model.drawio.drawio_class_model import DrawIOCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.reading.graph_reading import GraphReading
from cdd_guidance.practices.clean_engineering.model.javascript.javascript_class_model import JavaScriptCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.json.json_class_model import JsonCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.ooad_node import OoadNode
from cdd_guidance.practices.clean_engineering.model.python.python_class_model import PythonCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.sketch.sketch_class_model import SketchCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.typescript.typescript_class_model import TypeScriptCleanEngineeringModel
from harness.agent_tools.agent_tools import agent_instructions, agent_toolset, tools
from cdd_guidance.practices.clean_engineering.rules import RULES, rule_numbers
from harness.graph.practice_rule import decided_values
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class CleanEngineering(PracticeGuidance):
    """# Instructions"""

    # Its section of a sketch is the one its sketch format reads, held as that one lens.
    sketch_lens = SketchCleanEngineeringModel.lens
    # In the knowledge graph: Clean Engineering's modules, classes, and members, and its rules. The draw.io layout rules
    # check a rendered diagram through the Draw.io toolset's scan, not the graph.
    reading_type = GraphReading
    # Its formats name the module a folder's code files form, so a render of them is written to that module's file.
    formats_type = CleanEngineeringFormats
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

    # The format its model documents (`.context/*-model.md`) are written in: it reads each into the class model the
    # document describes, which the graph reading keeps.
    model_document_format = MarkdownCleanEngineeringModel

    default_workspace_folder = "src"

    @property
    def markdown_values(self) -> dict[str, str]:
        """The numbers its rules hold, for the markers its document carries in their place (``rules/rule_numbers.py``),
        so the limit a check reads is the one its rule's text states; and how each graph rule is decided, checked by
        the graph or judged from the candidates it lists, from the rule's own ``requires_judge``."""
        return {**rule_numbers.markdown_values(), **decided_values(RULES)}

    def is_production_code(self, file: str) -> bool:
        """Code its fidelities write, not a spec, a test, or test support (its reading's ``test_code``, the project's one answer)."""
        return not self.reading.test_code.is_test_code(file)
    # The class model each format reads and writes; the whiteboard model is imported only when a whiteboard is drawn.
    format_adapters = {
        "markdown": model_document_format,
        "json": JsonCleanEngineeringModel,
        "python": PythonCleanEngineeringModel,
        "typescript": TypeScriptCleanEngineeringModel,
        "javascript": JavaScriptCleanEngineeringModel,
        "drawio": DrawIOCleanEngineeringModel,
        "whiteboard": (
            "cdd_guidance.practices.clean_engineering.model.whiteboard.whiteboard_class_model",
            "WhiteboardCleanEngineeringModel",
        ),
        "sketch": SketchCleanEngineeringModel,
    }

    first_fidelity = "modules"

    def __init__(self, fidelity: str | None = "", format: str | None = None) -> None:
        super().__init__(format=format, fidelity=fidelity)
        self._drawio: Drawio | None = None

    @property
    def drawio(self) -> Drawio:
        """The Draw.io toolset this practice renders its diagrams with, made once; it reads the sources it draws with a
        markdown model of its own, so a diagram never changes the model this practice renders markdown with."""
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
    


OoadNode.practice_class = CleanEngineering
