# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity behavior
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD generator - multi-fidelity behavior skeletons and development."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from context_tools.base.base_context_tool import BaseContextTool
from primitives.actions.action import agent_instructions
from primitives.instructions import instruction
from primitives.tools.tool import agent_tool  # noqa: F401

if TYPE_CHECKING:
    from utilities.diagnose.diagnose import Diagnose

_FIDELITY_FORMAT_DEFAULTS = {
    "modules": "markdown",   # delegates to CE; no BDD-specific spec file written
    "behavior": "python",
    "development": "python",
}
_SUPPORTED_FORMATS = frozenset({"markdown", "python", "typescript", "java"})

# BDD fidelity → CleanEngineering fidelity at the same design depth.
_CE_FIDELITY: dict[str, str] = {
    "modules": "modules",
    "behavior": "model",
    "development": "code",
}


class TransformResult(TypedDict):
    """Result of a sideways format conversion."""

    source_format: str
    target_format: str
    content: str


def _resolve_format(fidelity: str, format: str | None) -> str:
    """Validate fidelity, resolve format to its default when None, validate format, and return it."""
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


class Bdd(BaseContextTool):
    """# Instructions

    Depends on CleanEngineering (lazy import in ce() and transform to avoid circular imports at
    module load time).
    """

    default_workspace_folder: str = "src"
    context_index_key: str = "bdd"
    _fidelity_format_defaults = dict(_FIDELITY_FORMAT_DEFAULTS)
    supported_formats = _SUPPORTED_FORMATS


    fidelities = {
        BaseContextTool.DISCOVERY: "modules",
        BaseContextTool.SPEC:      "behavior",
        BaseContextTool.ENGINEER:  "development",
    }

    def __init__(
        self,
        fidelity: str = "behavior",
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
    ) -> None:
        fidelity = type(self).resolve_fidelity(fidelity)
        resolved_format = _resolve_format(fidelity, format)
        super().__init__(
            format=resolved_format, path=path, session=session, workspace=workspace
        )
        self.fidelity = fidelity

    # -- CleanEngineering companion ------------------------------------------

    def ce(self) -> "BaseContextTool":
        """CleanEngineering companion at the matching fidelity (tool mode — invoke separately when ready)."""
        # lazy import: avoids circular import at module load
        from context_tools.clean_engineering.clean_engineering import CleanEngineering

        instance = CleanEngineering(
            fidelity=_CE_FIDELITY.get(self.fidelity, "modules"),
            path=self._raw_path,
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
        from utilities.diagnose.diagnose import Diagnose

        return Diagnose()

    # -- Lifecycle actions: BDD first, then CE classes -----------------------

    @agent_instructions
    def guidance(self) -> str:
        """Provide guidance for creating behavior skeletons and development tests.
        At modules fidelity: no BDD spec file is written — bootstrap CE class structure via the companion.
        At behavior fidelity: write all BDD test signatures (SIGNATURE markers).
        At development fidelity: write full test bodies and production code.
        When the target module already exists, scan the production source for every public method and property and verify each has test coverage — add missing signatures for any gap before writing new ones.
        BDD tests must conform to CE class structure: describe/it hierarchies must map onto public CE interfaces and operations.
        When this BDD work is done, call guidance on the Clean Engineering companion and pass that companion to this action as a separate tools run. The action already knows what to do for every tool. Do not inline."""
        super().guidance()
        self.ce().guidance()
        return (
            "When this BDD work is done, call guidance on the Clean Engineering companion "
            "and pass that companion to this action as a separate tools run. "
            "The action already knows what to do for every tool. Do not inline."
        )

    # -- Tool: sideways format conversion ------------------------------------

    @agent_tool
    def transform(self, source_format: str, target_format: str, content: str) -> TransformResult:
        """Sideways format conversion at the same fidelity.
        Delegates to clean_engineering.transform until BDD has its own channel model."""
        # lazy import: avoids circular import at module load
        from context_tools.clean_engineering.clean_engineering import CleanEngineering

        return CleanEngineering().transform(source_format, target_format, content)

    @agent_tool
    def render(self, format: str, content: str = "") -> dict:
        """Render already-generated BDD output into ``format`` via CleanEngineering channels."""
        if not content:
            raise ValueError("content is required — pass the already-generated artifact")
        source = self.format
        if not source:
            raise ValueError("source format is not set")
        return self.transform(source, format, content)
