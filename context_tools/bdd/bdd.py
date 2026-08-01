# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity behavior
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD generator - multi-fidelity behavior skeletons and development."""

from __future__ import annotations

from context_tools.base.base_context_tool import BaseContextTool
from tools.tool import tool  # noqa: F401

_FIDELITY_FORMAT_DEFAULTS = {
    "behavior": "python",
    "development": "python",
}
_SUPPORTED_FORMATS = frozenset({"markdown", "python", "typescript", "java"})


class Bdd(BaseContextTool):
    """# Instructions"""

    default_workspace_folder: str = "src"
    context_index_key: str = "bdd"

    def __init__(
        self,
        fidelity: str = "behavior",
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
    ) -> None:
        if fidelity not in _FIDELITY_FORMAT_DEFAULTS:
            raise ValueError(
                f"Unsupported fidelity {fidelity!r}. Choose from: {sorted(_FIDELITY_FORMAT_DEFAULTS)}"
            )
        resolved_format = format if format is not None else _FIDELITY_FORMAT_DEFAULTS[fidelity]
        if resolved_format not in _SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format {resolved_format!r}. Choose from: {sorted(_SUPPORTED_FORMATS)}"
            )
        super().__init__(
            format=resolved_format, path=path, session=session, workspace=workspace
        )
        self.fidelity = fidelity

    @tool
    def transform(self, source_format: str, target_format: str, content: str) -> dict:
        """Sideways format conversion at the same fidelity.
        Delegates to clean_engineering.transform until BDD has its own channel model."""
        from context_tools.clean_engineering.clean_engineering import CleanEngineering

        return CleanEngineering().transform(source_format, target_format, content)
