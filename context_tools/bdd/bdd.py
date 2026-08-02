# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity behavior
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD generator - multi-fidelity behavior skeletons and development."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from context_tools.base.base_context_tool import BaseContextTool
from primitives.actions.action import action
from primitives.tools.tool import tool  # noqa: F401

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
    def _partition_params(self) -> dict[str, str]:
        return {
            "lens_name": "BDD",
            "index_columns": "Subject / `that`·`with`",
            "primary_artifact": "Subject",
            "secondary_artifact": "`that` / `with` candidates",
            "artifact_naming_rule": "usage order",
            "skim_focus": "observable domain behaviors",
            "partition_done_checks": (
                "- [ ] Subjects are plain-English domain observables — no internals/`@…`.\n"
                "- [ ] `state-not-when` applied — order is a usage story; nest hints use `that`/`with`, never `when`.\n"
                "- [ ] Subject count ≠ chapter / major-heading / top-level-type count (mirrored TOC = hard fail)."
            ),
        }

    _fidelity_format_defaults = dict(_FIDELITY_FORMAT_DEFAULTS)

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
            path=self._ws_path,
            session=self._ws_session_name,
            workspace=self._ws_workspace,
        )
        instance.mode = "tool"
        return instance

    def diagnostic(self) -> "Diagnose":
        """Diagnose companion — common six-phase loop as a tool (not inlined)."""
        # lazy import: keeps diagnose optional at module load
        from utilities.diagnose.diagnose import Diagnose

        return Diagnose()

    # -- Lifecycle actions: BDD first, then CE classes -----------------------

    @action
    def generate(self) -> str:
        """At modules fidelity: delegate entirely to ce().generate() — no BDD spec file is written at this stage. Use this to bootstrap CE class structure before writing tests.
        At behavior fidelity: write all BDD test signatures (SIGNATURE markers).
        At development fidelity: write full test bodies and production code.
        When the target module already exists, scan the production source for every public method and property and verify each has test coverage — add missing signatures for any gap before writing new ones.
        BDD tests must conform to CE class structure: describe/it hierarchies must map onto public CE interfaces and operations.
        When BDD artifacts are complete, call ce().generate() to produce the matching class skeletons."""
        super().generate()
        self.ce().generate()
        return "When done, run validate."

    @action
    def grill(self) -> str:
        """Run the BDD grill loop to surface assumptions and gaps.
        When BDD grill is complete, call ce().grill() to do the same for the matching classes."""
        super().grill()
        self.ce().grill()
        return "Grill complete; run generate."

    @action
    def sketch(self) -> str:
        """Sketch the BDD hierarchy at the current fidelity.
        When BDD sketch is complete, call ce().sketch() to sketch the matching classes."""
        super().sketch()
        self.ce().sketch()
        return "Sketch complete; run generate."

    @action
    def iterate(self) -> str:
        """Iterate one BDD cycle: write one test, confirm it is RED, then call ce().iterate() to build the minimum production code until GREEN. Repeat — one test, one production change, one GREEN — until all tests pass.
        If the same test is still RED after 2 consecutive fix attempts — stop guessing. Call diagnostic().diagnose() before a third fix (wrong exception, wrong line, shifting failure mode, or a re-read of the code that does not explain the failure)."""
        super().iterate()
        self.ce().iterate()
        self.diagnostic().diagnose()
        return "Iterate complete; run validate."

    @action
    def satisfy(self) -> str:
        """Scan the production source for every public method and property; flag any with no corresponding test as a coverage gap. Fix every BDD violation and coverage gap — confirm each failing test is RED for the right reason.
        When BDD violations and coverage gaps are resolved, call ce().satisfy() to build or fix the minimum production code until GREEN. One test, one production change, one GREEN — repeat until validate passes.
        If the same test is still RED after 2 consecutive fix attempts — stop guessing. Call diagnostic().diagnose() before a third fix (wrong exception, wrong line, shifting failure mode, or a re-read of the code that does not explain the failure)."""
        super().satisfy()
        self.ce().satisfy()
        self.diagnostic().diagnose()
        return "When done, run validate on artifacts under {session.path}/."

    @action
    def validate(self) -> str:
        """Validate all BDD artifacts at the current fidelity.
        When BDD validation passes, call ce().validate() to validate the matching class artifacts."""
        super().validate()
        self.ce().validate()
        return "Validation report for artifacts under {session.path}/."

    @action
    def repair(self) -> str:
        """Repair the BDD artifact that is failing or malformed.
        When the BDD artifact is clean, call ce().repair() to repair the matching class artifact."""
        super().repair()
        self.ce().repair()
        return "Repair complete; run validate."

    # -- Tool: sideways format conversion ------------------------------------

    @tool
    def transform(self, source_format: str, target_format: str, content: str) -> TransformResult:
        """Sideways format conversion at the same fidelity.
        Delegates to clean_engineering.transform until BDD has its own channel model."""
        # lazy import: avoids circular import at module load
        from context_tools.clean_engineering.clean_engineering import CleanEngineering

        return CleanEngineering().transform(source_format, target_format, content)
