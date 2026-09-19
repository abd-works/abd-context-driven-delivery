"""Clean Engineering generator - multi-fidelity OO design and implementation."""

from __future__ import annotations

from practices.clean_engineering.class_model.drawio.drawio_class_model import DrawIOCleanEngineeringModel
from practices.clean_engineering.class_model.java_class_model import JavaCleanEngineeringModel
from practices.clean_engineering.class_model.javascript_class_model import JavaScriptCleanEngineeringModel
from practices.clean_engineering.class_model.json_class_model import JsonCleanEngineeringModel
from practices.clean_engineering.class_model.markdown_class_model import MarkdownCleanEngineeringModel
from practices.clean_engineering.class_model.python_class_model import PythonCleanEngineeringModel
from practices.clean_engineering.class_model.typescript_class_model import TypeScriptCleanEngineeringModel
from harness.agent_tools.agent_tools import agent_instructions, agent_toolset, tools
from harness.guidance.guidance import PracticeGuidance
from installation.harness_files.harness_files import Skill
from installation.mcp.mcp_server import Mcp
from agent_tools.agent_tools import agent_tool  # noqa: F401

_CHANNELS: dict[str, type] = {
    "markdown": MarkdownCleanEngineeringModel,
    "json": JsonCleanEngineeringModel,
    "python": PythonCleanEngineeringModel,
    "typescript": TypeScriptCleanEngineeringModel,
    "java": JavaCleanEngineeringModel,
    "javascript": JavaScriptCleanEngineeringModel,
    "drawio": DrawIOCleanEngineeringModel,
}

_SUPPORTED_FORMATS = frozenset(_CHANNELS)


@agent_toolset
class CleanEngineering(PracticeGuidance):
    """# Instructions"""

    domain_slug = "clean_engineering"
    default_workspace_folder: str = "src"
    context_index_key: str = "clean_engineering"
    _formats = _CHANNELS
    supported_formats = _SUPPORTED_FORMATS

    def __init__(
        self,
        fidelity: str = "modules",
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
        stage: str | None = None,
    ) -> None:
        super().__init__(
            format=format,
            path=path,
            session=session,
            workspace=workspace,
            fidelity=fidelity,
            stage=stage,
        )
        self.drawio = None
        if self.format == "drawio":
            from practices.clean_engineering.class_model.drawio.drawio import Drawio

            self.drawio = Drawio(workspace=self.workspace)
            self.drawio.mode = "tool"

    @property
    @Mcp
    @Skill
    @agent_instructions
    def instructions(self) -> str:
        """Structure the problem into independent modules with small public interfaces, substantial hidden functionality, and one-way dependencies. Implement those modules with rigorous object-oriented and clean-code practices. When boundaries hold, a change stays inside one module; when they blur, callers depend on internal decisions and must change with them."""
        return super().instructions

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

    @agent_tool
    def render(
        self,
        format: str,
        content: str,
        source: str | None = None,
        previous: str = "",
        keep_positioning: bool = False,
    ) -> dict:
        """Parse content into the canonical model, then render into format.
        source defaults to this instance's format. Peer channels at the same fidelity.
        When format is drawio and keep_positioning is true, pass previous Draw.io XML
        so existing class positions and relationship routing are kept."""
        source_format = source or self.format
        if not source_format:
            raise ValueError("source format is not set")
        if source_format not in _CHANNELS:
            raise ValueError(
                f"Unsupported source {source_format!r}. Choose from: {sorted(_CHANNELS)}"
            )
        if format not in _CHANNELS:
            raise ValueError(
                f"Unsupported format {format!r}. Choose from: {sorted(_CHANNELS)}"
            )
        canonical = _CHANNELS[source_format].parse(content)
        if format == "drawio":
            rendered = _CHANNELS[format].render(
                canonical,
                previous=previous or None,
                keep_positioning=keep_positioning,
            )
        else:
            rendered = _CHANNELS[format].render(canonical)
        return {"format": format, "content": rendered}
