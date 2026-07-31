"""Base scanner that loads the UX Workspace and checks the canonical model."""

from __future__ import annotations

from pathlib import Path

from scanners import Scanner

from context_tools.ux.ux_model.workspace import Workspace


class UxWorkspaceScanner(Scanner):
    """Scanners operate on Workspace - not format-specific text."""

    def scan(self, root: Path, files: list[Path]) -> list:
        workspace = Workspace.load(root)
        return list(self.scan_workspace(workspace))

    def scan_workspace(self, workspace: Workspace):
        raise NotImplementedError
