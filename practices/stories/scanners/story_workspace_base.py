"""Base scanner that loads the Stories Workspace and checks the canonical model."""

from __future__ import annotations

from pathlib import Path

from scanners import Scanner

from stories.story_model.workspace import Workspace


class StoryWorkspaceScanner(Scanner):
    """Scanners operate on Workspace — not language-specific text."""

    def scan(self, root: Path, files: list[Path]) -> list:
        # File list is ignored: story rules are graph-wide.
        workspace = Workspace.load(root)
        return list(self.scan_workspace(workspace))

    def scan_workspace(self, workspace: Workspace):
        raise NotImplementedError

    def loc(self, node, fallback: str = "") -> str:
        source = getattr(node, "source", None)
        if source is None:
            return fallback
        try:
            return source.render()
        except Exception:
            return fallback
