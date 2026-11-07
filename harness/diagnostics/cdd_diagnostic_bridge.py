"""The optional ``cdd-diagnostic`` package's workspace fixtures (branches, sessions) for the heavy probes."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

# The checkout of the ``cdd-diagnostic`` package, when it is not installed into this Python.
CDD_DIAGNOSTIC_REPO_ENV = "CDD_DIAGNOSTIC_REPO"


class CddDiagnosticFixtures:
    """The ``cdd-diagnostic`` workspace fixtures for one checkout: the branches and sessions a heavy probe works in, and
    the arguments it calls each session and graph operation with. Without the package there are none."""

    def __init__(self, repo: Path | str) -> None:
        self.repo = Path(repo)

    @property
    def is_installed(self) -> bool:
        self._add_package_checkout_to_import_path()
        try:
            import cdd_diagnostic.workspace  # noqa: F401
        except ImportError:
            return False
        return True

    def prepare(self) -> None:
        """Make the workspace fixtures in the checkout, when the package is installed."""
        if not self.is_installed:
            return
        from cdd_diagnostic.workspace import WorkspaceFixtures

        WorkspaceFixtures(self.repo)

    def probe_arguments(self, mcp_name: str) -> tuple[dict[str, Any], list[str]] | None:
        """The arguments the fixtures give for the operation, and the required ones they cannot make; none without the
        package."""
        if not self.is_installed:
            return None
        from cdd_diagnostic.workspace import probe_arguments

        return probe_arguments(mcp_name, self.repo)

    def _add_package_checkout_to_import_path(self) -> None:
        root = os.environ.get(CDD_DIAGNOSTIC_REPO_ENV)
        if not root:
            return
        for folder in (Path(root).resolve(), Path(root).resolve() / "src"):
            if folder.is_dir() and str(folder) not in sys.path:
                sys.path.insert(0, str(folder))
