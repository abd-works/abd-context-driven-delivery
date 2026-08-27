# @toolset-manifest python -m tools manifest context_tools.ddd.ddd:Ddd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity bounded_context
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""DDD generator - domain emphasis, contexts, building blocks over clean_engineering."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from pathlib import Path

from primitives.actions.action import agent_instructions
from context_tools.base.base_context_tool import BaseContextTool
from primitives.instructions import Instruction
from primitives.instructions import instruction
from scanners.scan import Scan
from scanners.scanner_collection import ScannerCollection
from tools.tool import agent_tool  # noqa: F401

if TYPE_CHECKING:
    from utilities.diagnose.diagnose import Diagnose

_FIDELITY_FORMAT_DEFAULTS = {
    "scaffold": "markdown",
    "bounded_context": "markdown",
    "building_blocks": "markdown",
    "tactics": "python",
}

# DDD fidelity -> clean_engineering fidelity (CE owns OO ladder; DDD overlays domain/strategic).
_CE_FIDELITY = {
    "scaffold": "modules",
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


class _DddScan(Scan):
    """Discover DDD scanners under ``context_tools/ddd/scanners``."""

    def __init__(self, module_dir: Path) -> None:
        self._module_dir = Path(module_dir)

    def _scanner_collection(self) -> ScannerCollection:
        return ScannerCollection(
            module_dir=self._module_dir,
            root_path=self._module_dir / "scanners",
        )


class Ddd(BaseContextTool):
    """# Instructions

    Depends on CleanEngineering (lazy import in ce() and transform to avoid circular imports at
    module load time).
    """

    _fidelity_format_defaults = dict(_FIDELITY_FORMAT_DEFAULTS)
    supported_formats = _SUPPORTED_FORMATS

    fidelities = {
        BaseContextTool.SHAPING:   "scaffold",
        BaseContextTool.DISCOVERY: "bounded_context",
        BaseContextTool.SPEC:      "building_blocks",
        BaseContextTool.ENGINEER:  "tactics",
    }

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
        super().__init__(
            format=resolved_format, path=path, session=session, workspace=workspace
        )
        self._fidelity = fidelity
        self.scanner = _DddScan(self.module_dir)

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

    def ce(self) -> "BaseContextTool":
        """CleanEngineering companion at the matching fidelity (tool mode — invoke separately when ready)."""
        from context_tools.clean_engineering.clean_engineering import CleanEngineering

        instance = CleanEngineering(
            fidelity=_CE_FIDELITY.get(self.fidelity, "modules"),
            format=self.format,
            path=self.workspace.path,
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
        from utilities.diagnose.diagnose import Diagnose

        return Diagnose()

    @agent_tool
    def apply_document_workspace_default(self) -> str:
        """Set the durable working area to `domain/` for /document.

        Does not change CleanEngineering's own default folder. Skip when `path`
        was passed or `default_workspace_folder` is already not the generate
        default (`src`). Returns the working path in force.
        """
        generate_folder = type(self).default_workspace_folder
        if self._raw_path is not None:
            current = self.workspace.current_work_session
            return current.path if current is not None else self.workspace.path
        if self.default_workspace_folder != generate_folder:
            current = self.workspace.current_work_session
            return current.path if current is not None else self.workspace.path
        self.default_workspace_folder = type(self)._DOCUMENT_WORKSPACE_FOLDER
        current = self.workspace.current_work_session
        if current is None:
            return self.workspace.path
        current.default_workspace_folder = type(self)._DOCUMENT_WORKSPACE_FOLDER
        current.path = current._resolve_working_area(None)
        return current.path

    @instruction
    def contexts(self) -> Instruction: ...

    @agent_instructions
    def guidance(self) -> str:
        """Provide guidance for creating bounded contexts, building blocks, and tactics.
        When DDD scaffolding is ready, call guidance on the CE companion and pass that companion to this action as a separate tools run for matching OO artifacts.
        Scan the production source for every public method and property; flag any with no corresponding test as a coverage gap. Fix every BDD violation and coverage gap — confirm each failing test is RED for the right reason.
        If the same test is still RED after 2 consecutive fix attempts — stop guessing. Call diagnostic().diagnose() before a third fix (wrong exception, wrong line, shifting failure mode, or a re-read of the code that does not explain the failure).
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
