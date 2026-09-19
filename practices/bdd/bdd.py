"""BDD generator - multi-fidelity behavior skeletons and development."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.agent_tools.agent_tools import agent_instructions, agent_toolset
from harness.guidance.guidance import PracticeGuidance
from installation.harness_files.harness_files import Skill
from installation.mcp.mcp_server import Mcp
from agent_tools.agent_tools import agent_tool  # noqa: F401

if TYPE_CHECKING:
    from tools.diagnose.diagnose import Diagnose

_SUPPORTED_FORMATS = frozenset({"markdown", "python", "typescript", "java"})


@agent_toolset
class Bdd(PracticeGuidance):
    """# Instructions

    Depends on CleanEngineering (lazy import in diagnostic to avoid circular imports at
    module load time).
    """

    domain_slug = "bdd"
    default_workspace_folder: str = "src"
    context_index_key: str = "bdd"
    supported_formats = _SUPPORTED_FORMATS

    def __init__(
        self,
        fidelity: str = "behavior",
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

    @property
    @Mcp
    @Skill
    @agent_instructions
    def instructions(self) -> str:
        """Behavior-driven development turns domain vocabulary into passing tests. Every BDD artifact is an indented hierarchy. Sketch that shape first (`templates/bdd-sketch.md`)."""
        return super().instructions
