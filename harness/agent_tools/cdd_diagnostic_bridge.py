"""Optional ``cdd-diagnostic`` package for heavy workspace fixtures (branches, sessions)."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any


def _ensure_cdd_diagnostic_path() -> None:
    root = os.environ.get("CDD_DIAGNOSTIC_REPO")
    if root:
        path = str(Path(root).resolve())
        if path not in sys.path:
            sys.path.insert(0, path)
        src = Path(root) / "src"
        if src.is_dir() and str(src) not in sys.path:
            sys.path.insert(0, str(src))


def probe_arguments_from_cdd_diagnostic(
    mcp_name: str,
    repo_root: Path | str,
) -> tuple[dict[str, Any], list[str]] | None:
    _ensure_cdd_diagnostic_path()
    try:
        from cdd_diagnostic.workspace import probe_arguments
    except ImportError:
        return None
    return probe_arguments(mcp_name, repo_root)
