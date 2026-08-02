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

from primitives.actions.action import action
from context_tools.base.base_context_tool import BaseContextTool
from primitives.instructions import Instruction
from primitives.instructions import instruction
from tools.tool import tool  # noqa: F401

if TYPE_CHECKING:
    from utilities.diagnose.diagnose import Diagnose

_FIDELITY_FORMAT_DEFAULTS = {
    "bounded_context": "markdown",
    "building_blocks": "markdown",
    "code": "python",
}

# DDD fidelity -> clean_engineering fidelity (CE owns OO ladder; DDD overlays domain/strategic).
_CE_FIDELITY = {
    "bounded_context": "modules",
    "building_blocks": "model",
    "code": "code",
}

_SUPPORTED_FORMATS = frozenset(
    {"markdown", "json", "python", "typescript", "java", "javascript", "drawio"}
)


class TransformResult(TypedDict):
    """Result of a sideways format conversion."""

    format: str
    content: str


class Ddd(BaseContextTool):
    """# Instructions

    Depends on CleanEngineering (lazy import in ce() and transform to avoid circular imports at
    module load time).
    """

    _fidelity_format_defaults = dict(_FIDELITY_FORMAT_DEFAULTS)

    fidelities = {
        BaseContextTool.DISCOVERY: "bounded_context",
        BaseContextTool.SPEC:      "building_blocks",
        BaseContextTool.ENGINEER:  "code",
    }

    default_workspace_folder: str = "src"
    context_index_key: str = "ddd"
    def _partition_params(self) -> dict[str, str]:
        return {
            "lens_name": "DDD",
            "index_columns": "Bounded Context / Ubiquitous Language",
            "primary_artifact": "Bounded Context",
            "secondary_artifact": "candidate aggregates and a ubiquitous-language note",
            "artifact_naming_rule": "domain noun",
            "skim_focus": "language boundaries — where a term shifts meaning or belongs to a different team",
            "partition_done_checks": "- [ ] `language-is-context-scoped` applied — context names are domain nouns anchored to a language boundary, not chapter titles.",
        }

    def __init__(
        self,
        fidelity: str = "bounded_context",
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
    ) -> None:
        resolved_format = self._resolve_format(fidelity, format)
        super().__init__(
            format=resolved_format, path=path, session=session, workspace=workspace
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

    def ce(self) -> "BaseContextTool":
        """CleanEngineering companion at the matching fidelity (tool mode — invoke separately when ready)."""
        from context_tools.clean_engineering.clean_engineering import CleanEngineering

        instance = CleanEngineering(
            fidelity=_CE_FIDELITY.get(self.fidelity, "modules"),
            format=self.format,
            path=self._ws_path,
            session=self._ws_session_name,
            workspace=self._ws_workspace,
        )
        instance.mode = "tool"
        return instance

    def diagnostic(self) -> "Diagnose":
        """Diagnose companion — common six-phase loop as a tool (not inlined)."""
        from utilities.diagnose.diagnose import Diagnose

        return Diagnose()

    @instruction
    def contexts(self) -> Instruction: ...

    @action
    def generate_output(self) -> str:
        """When DDD scaffolding is ready, call ce().generate() for matching OO artifacts."""
        self.ce().generate()
        return ""

    @action
    def validate(self) -> str:
        """Validate all DDD artifacts at the current fidelity.
        When DDD validation passes, call ce().validate() to validate the matching class artifacts."""
        self.contexts
        self.ce().validate()
        self.scan()
        return "Validation report."

    @action
    def satisfy(self) -> str:
        """Scan the production source for every public method and property; flag any with no corresponding test as a coverage gap. Fix every BDD violation and coverage gap — confirm each failing test is RED for the right reason.
        When BDD violations and coverage gaps are resolved, call ce().satisfy() to build or fix the minimum production code until GREEN. One test, one production change, one GREEN — repeat until validate passes.
        If the same test is still RED after 2 consecutive fix attempts — stop guessing. Call diagnostic().diagnose() before a third fix (wrong exception, wrong line, shifting failure mode, or a re-read of the code that does not explain the failure)."""
        self.contexts
        self.templates
        self.ce().satisfy()
        self.diagnostic().diagnose()
        return "When done, run validate."

    @action
    def repair(self, asset: str, violation: str) -> str:
        """Repair the DDD artifact that is failing or malformed.
        When the DDD artifact is clean, call ce().repair() to repair the matching class artifact."""
        self.scan()
        self.contexts
        self.examples
        self.templates
        self.ce().repair()
        self.validate()
        return "Repair {asset} until validate passes."

    @tool
    def transform(self, source_format: str, target_format: str, content: str) -> TransformResult:
        """Sideways format conversion at the same fidelity.
        Delegates to clean_engineering.transform - DDD adds no separate channel model."""
        return self.ce().transform(source_format, target_format, content)
