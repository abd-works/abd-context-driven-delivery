"""Knowledge graph practice — load and navigate the unified practice graph."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance
from agent_tools.agent_tools import agent_tool  # noqa: F401

from .model import PracticeGraph


@agent_toolset
class KnowledgeGraph(PracticeGuidance):
    """Load a workspace into a PracticeGraph and navigate stories, modules, and descriptions."""

    def __init__(
        self,
        fidelity: str = "behavior",
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
    ) -> None:
        super().__init__(
            format=format,
            fidelity=fidelity,
            default_workspace_folder=".",
        )
        if path is not None or session is not None:
            self._attach_workspace(path=path, session=session)

    def load(
        self,
        workspace_path: str,
        *,
        codeql_results: str | None = None,
    ) -> PracticeGraph:
        return PracticeGraph.load(workspace_path, codeql_results=codeql_results)
