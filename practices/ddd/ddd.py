"""DDD generator - domain emphasis, contexts, building blocks over clean_engineering."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

from practices.stages import DISCOVERY, ENGINEER, SHAPING, SPEC, resolve_stage_fidelity
from practices.workspace_bind import init_practice_guidance
from primitives.agent_tools.agent_tools import agent_instructions, agent_toolset
from primitives.guidance.guidance import PracticeGuidance
from agent_tools.agent_tools import agent_tool  # noqa: F401

if TYPE_CHECKING:
    from practices.clean_engineering.clean_engineering import CleanEngineering
    from tools.diagnose.diagnose import Diagnose

_FIDELITY_FORMAT_DEFAULTS = {
    "bounded_context": "markdown",
    "building_blocks": "markdown",
    "tactics": "python",
}

# DDD fidelity -> clean_engineering fidelity (CE owns OO ladder; DDD overlays domain/strategic).
_CE_FIDELITY = {
    "bounded_context": "modules",
    "building_blocks": "model",
    "tactics": "code",
}

_SUPPORTED_FORMATS = frozenset(
    {"markdown", "json", "python", "typescript", "java", "javascript", "drawio"}
)


class TransformResult(TypedDict):
    """Result of a sideways format conversion."""

    format: str
    content: str


@agent_toolset
class Ddd(PracticeGuidance):
    """# Instructions

    Depends on CleanEngineering (lazy import in ce() and transform to avoid circular imports at
    module load time).
    """

    domain_slug = "ddd"
    _fidelity_format_defaults = dict(_FIDELITY_FORMAT_DEFAULTS)
    supported_formats = _SUPPORTED_FORMATS

    STAGE_TO_FIDELITY = {
        SHAPING: "bounded_context",
        DISCOVERY: "bounded_context",
        SPEC: "building_blocks",
        ENGINEER: "tactics",
    }

    @classmethod
    def resolve_fidelity(cls, fidelity: str) -> str:
        return resolve_stage_fidelity(fidelity, cls.STAGE_TO_FIDELITY)

    # Generate / new work: src/. /document defaults to domain/ unless path or folder is set.
    default_workspace_folder: str = "src"
    context_index_key: str = "ddd"
    _DOCUMENT_WORKSPACE_FOLDER: str = "domain"

    def __init__(
        self,
        fidelity: str = "bounded_context",
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
    ) -> None:
        fidelity = type(self).resolve_fidelity(fidelity)
        resolved_format = self._resolve_format(fidelity, format)
        init_practice_guidance(
            self,
            format=resolved_format,
            path=path,
            session=session,
            workspace=workspace,
            fidelity=fidelity,
            stage_to_fidelity=self.STAGE_TO_FIDELITY,
        )
        self._fidelity = fidelity

    @property
    def fidelity(self) -> str:
        return self._fidelity

    def _resolve_format(self, fidelity: str, format: str | None) -> str:
        if fidelity not in _FIDELITY_FORMAT_DEFAULTS:
            raise ValueError(
                f"Unsupported fidelity {fidelity!r}. Choose from: {sorted(_FIDELITY_FORMAT_DEFAULTS)}"
            )
        resolved = format if format is not None else _FIDELITY_FORMAT_DEFAULTS[fidelity]
        if resolved not in _SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format {resolved!r}. Choose from: {sorted(_SUPPORTED_FORMATS)}"
            )
        return resolved

    def ce(self) -> "CleanEngineering":
        """CleanEngineering companion at the matching fidelity (tool mode — invoke separately when ready)."""
        from practices.clean_engineering.clean_engineering import CleanEngineering

        current = self.workspace.current_work_session
        working_path = current.path if current is not None else self.path
        workspace_root = current.workspace_root if current is not None else self.workspace.path
        ce_fidelity = _CE_FIDELITY[self.fidelity]
        instance = CleanEngineering(
            fidelity=ce_fidelity,
            format=self.format,
            path=working_path,
            session=current.name if current is not None else "",
            workspace=workspace_root,
        )
        instance.mode = "tool"
        return instance

    def diagnostic(self) -> "Diagnose":
        """Diagnose companion — common six-phase loop as a tool (not inlined)."""
        from tools.diagnose.diagnose import Diagnose

        return Diagnose()

    @agent_tool
    def apply_document_workspace_default(self) -> str:
        """Set the durable working area to `domain/` for /document.

        Does not change CleanEngineering's own default folder. Skip when `path`
        was passed or `default_workspace_folder` is already not the generate
        default (`src`). Returns the working path in force.
        """
        generate_folder = type(self).default_workspace_folder
        current = self.workspace.current_work_session
        if current is None:
            self.workspace.open(
                self,
                name=self.session,
                path=self.path or "",
            )
            current = self.workspace.current_work_session
        if current is None:
            raise RuntimeError("DDD work session did not open")
        if self.path is not None:
            return current.path
        if self.default_workspace_folder != generate_folder:
            return current.path
        generated_path = Path(current.workspace_root) / generate_folder
        if Path(current.path).resolve() != generated_path.resolve():
            return current.path
        self.default_workspace_folder = type(self)._DOCUMENT_WORKSPACE_FOLDER
        current.default_workspace_folder = type(self)._DOCUMENT_WORKSPACE_FOLDER
        current.path = str(Path(current.workspace_root) / current.default_workspace_folder)
        current.record_context_root()
        return current.path

    @agent_instructions
    def guidance(self) -> str:
        """Provide guidance for creating bounded contexts, building blocks, and tactics.
        When this DDD work is done, call guidance on the Clean Engineering companion and pass that companion to this action as a separate tools run. The action already knows what to do for every tool. Do not inline."""
        super().guidance()
        self.ce().guidance()
        return (
            "When this DDD work is done, call guidance on the Clean Engineering companion "
            "and pass that companion to this action as a separate tools run. "
            "The action already knows what to do for every tool. Do not inline."
        )

    @agent_tool
    def transform(self, source_format: str, target_format: str, content: str) -> TransformResult:
        """Sideways format conversion at the same fidelity.
        Delegates to clean_engineering.transform - DDD adds no separate channel model."""
        return self.ce().transform(source_format, target_format, content)

    @agent_tool
    def render(self, format: str, content: str = "") -> dict:
        """Render already-generated DDD output into ``format`` via CleanEngineering channels."""
        if not content:
            raise ValueError("content is required — pass the already-generated artifact")
        source = self.format
        if not source:
            raise ValueError("source format is not set")
        return self.transform(source, format, content)
