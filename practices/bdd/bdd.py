"""BDD generator - multi-fidelity behavior skeletons and development."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from harness.agent_tools.agent_tools import agent_instructions, agent_toolset
from harness.guidance.guidance import PracticeGuidance
from installation.harness_files.harness_files import Skill
from installation.mcp.mcp_server import Mcp
from agent_tools.agent_tools import agent_tool  # noqa: F401

if TYPE_CHECKING:
    from practices.clean_engineering.clean_engineering import CleanEngineering
    from tools.diagnose.diagnose import Diagnose

_FIDELITY_FORMAT_DEFAULTS = {
    "behavior": "python",
    "development": "python",
}
_SUPPORTED_FORMATS = frozenset({"markdown", "python", "typescript", "java"})

# BDD fidelity → CleanEngineering fidelity at the same design depth.
_CE_FIDELITY: dict[str, str] = {
    "behavior": "model",
    "development": "code",
}


class TransformResult(TypedDict):
    """Result of a sideways format conversion."""

    source_format: str
    target_format: str
    content: str


@agent_toolset
class Bdd(PracticeGuidance):
    """# Instructions

    Depends on CleanEngineering (lazy import in ce() and transform to avoid circular imports at
    module load time).
    """

    domain_slug = "bdd"
    default_workspace_folder: str = "src"
    context_index_key: str = "bdd"
    _fidelity_format_defaults = dict(_FIDELITY_FORMAT_DEFAULTS)
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

    # -- CleanEngineering companion ------------------------------------------

    def ce(self) -> "CleanEngineering":
        """CleanEngineering companion at the matching fidelity (tool mode — invoke separately when ready)."""
        # lazy import: avoids circular import at module load
        from practices.clean_engineering.clean_engineering import CleanEngineering

        ce_fidelity = _CE_FIDELITY[self.fidelities.current.fidelity]
        instance = CleanEngineering(
            fidelity=ce_fidelity,
            path=self.path,
            session=(
                self.workspace.current_work_session.name
                if self.workspace.current_work_session
                else ""
            ),
            workspace=self.workspace.path,
        )
        instance.mode = "tool"
        return instance

    def diagnostic(self) -> "Diagnose":
        """Diagnose companion — common six-phase loop as a tool (not inlined)."""
        # lazy import: keeps diagnose optional at module load
        from tools.diagnose.diagnose import Diagnose

        return Diagnose()

    # -- Lifecycle actions: BDD first, then CE classes -----------------------

    @property
    @Mcp
    @Skill
    @agent_instructions
    def instructions(self) -> str:
        """Behavior-driven development turns domain vocabulary into passing tests. Every BDD artifact is an indented hierarchy. Sketch that shape first (`templates/bdd-sketch.md`)."""
        return super().instructions

    @property
    @agent_instructions
    def guidance(self) -> str:
        """Expand this practice's Guidance section, then Clean Engineering companion guidance."""
        super().guidance
        self.ce().guidance
        return (
            "When this BDD work is done, call guidance on the Clean Engineering companion "
            "and pass that companion to this action as a separate tools run. "
            "The action already knows what to do for every tool. Do not inline."
        )

    # -- Tool: sideways format conversion ------------------------------------

    @agent_tool
    def render(self, format: str, content: str, source: str | None = None) -> TransformResult:
        """Sideways format conversion at the same fidelity.
        Delegates to clean_engineering.render until BDD has its own channel model."""
        from practices.clean_engineering.clean_engineering import CleanEngineering

        source_format = source or self.format
        if not source_format:
            raise ValueError("source format is not set")
        return CleanEngineering().render(format, content, source=source_format)
