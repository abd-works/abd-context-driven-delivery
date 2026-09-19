"""Stories generator - multi-fidelity story maps, scenarios, and acceptance tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.agent_tools.agent_tools import agent_instructions, agent_toolset
from harness.guidance.guidance import PracticeGuidance
from installation.harness_files.harness_files import Skill
from installation.mcp.mcp_server import Mcp

if TYPE_CHECKING:
    from tools.diagnose.diagnose import Diagnose


@agent_toolset
class Stories(PracticeGuidance):
    """# Instructions"""

    domain_slug = "stories"
    default_workspace_folder: str = "tests"
    context_index_key: str = "stories"
    _formats = {
        "markdown": ("stories.model.markdown.nodes", "MarkdownStoryMap"),
        "json": ("stories.model.json.nodes", "JsonStoryMap"),
        "drawio": ("stories.model.drawio.nodes", "DrawIOStoryMap"),
        "miro": ("stories.model.miro.nodes", "MiroStoryMap"),
        "python": ("stories.model.python.python_story_map", "PythonStoryMap"),
        "typescript": ("stories.model.typescript.typescript_story_map", "TypeScriptStoryMap"),
        "java": ("stories.model.java.java_story_map", "JavaStoryMap"),
        "javascript": ("stories.model.javascript.javascript_story_map", "JavaScriptStoryMap"),
    }
    supported_formats = frozenset(_formats)

    def __init__(
        self,
        fidelity: str = "story_map",
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

    def diagnostic(self) -> "Diagnose":
        """Diagnose companion — common six-phase loop as a tool (not inlined)."""
        from tools.diagnose.diagnose import Diagnose

        return Diagnose()

    @property
    @Mcp
    @Skill
    @agent_instructions
    def instructions(self) -> str:
        """Map stakeholder and system interactions as behaviours that deliver a solution. Every later fidelity builds on these behaviours, so the story map must describe operations that named actors perform and results they can observe."""
        return super().instructions
