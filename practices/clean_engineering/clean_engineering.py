"""Clean Engineering generator - multi-fidelity OO design and implementation."""

from __future__ import annotations

from practices.clean_engineering.model.drawio.drawio_class_model import DrawIOCleanEngineeringModel
from practices.clean_engineering.model.java.java_class_model import JavaCleanEngineeringModel
from practices.clean_engineering.model.javascript.javascript_class_model import JavaScriptCleanEngineeringModel
from practices.clean_engineering.model.json.json_class_model import JsonCleanEngineeringModel
from practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel
from practices.clean_engineering.model.python.python_class_model import PythonCleanEngineeringModel
from practices.clean_engineering.model.typescript.typescript_class_model import TypeScriptCleanEngineeringModel
from harness.agent_tools.agent_tools import agent_instructions, agent_toolset, tools
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class CleanEngineering(PracticeGuidance):
    """# Instructions"""

    def __init__(
        self,
        fidelity: str = "modules",
        format: str | None = None,
        drawio=None,
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
            },
        )
        self.drawio = drawio
        if self.drawio is not None:
            self.drawio.mode = "tool"

    @property
    def model(self):
        from practices.clean_engineering.model.transformation.clean_engineering_transformer import (
            CleanEngineeringTransformer,
        )

        class CleanEngineeringPracticeModel:
            transformer = CleanEngineeringTransformer

        return CleanEngineeringPracticeModel()

    @agent_instructions
    def generate_output(self) -> str:
        """Write the fidelity artifact under the session.

        When ``format`` is ``drawio``, call ``drawio.render`` (create diagram →
        scan layout rules in drawio contexts → repair sub-agent on definitive
        layout failures). Otherwise produce the active channel output
        (markdown / python / …) from contexts, examples, and templates — do
        not invoke drawio.render.
        """
        tools(self.drawio.render())
        return "Artifact written under {session.path}/."
    