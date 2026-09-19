"""DDD generator - domain emphasis, contexts, building blocks over clean_engineering."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.agent_tools.agent_tools import agent_instructions, agent_toolset
from harness.guidance.guidance import PracticeGuidance
from installation.harness_files.harness_files import Skill
from installation.mcp.mcp_server import Mcp

if TYPE_CHECKING:
    from tools.diagnose.diagnose import Diagnose

_SUPPORTED_FORMATS = frozenset(
    {"markdown", "json", "python", "typescript", "java", "javascript", "drawio"}
)


@agent_toolset
class Ddd(PracticeGuidance):
    """# Instructions

    Depends on CleanEngineering (lazy import in diagnostic to avoid circular imports at
    module load time).
    """

    domain_slug = "ddd"
    supported_formats = _SUPPORTED_FORMATS
    default_workspace_folder: str = "src"
    context_index_key: str = "ddd"

    def __init__(
        self,
        fidelity: str = "bounded_context",
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
        """Build the solution around how the business actually works, in the words the business already uses. When the software mirrors the business, it holds the business's logic and knowledge where that understanding actually lives; when it mirrors a database, a framework, or a screen layout, every business conversation has to be re-translated and what the business knows ends up scattered wherever the technology happened to put it."""
        return super().instructions
