"""story-domain-js-imported — bound story/object reference paths must exist on disk."""

from __future__ import annotations

from pathlib import Path

from ux_workspace_base import UxWorkspaceScanner


class StoryDomainJsImportedScanner(UxWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_ux_map():
            return
        root = workspace.root
        for path in workspace.ux_map.story_references:
            if not _exists(root, path):
                yield self.violation(
                    f"story reference {path!r} is bound but missing — "
                    "run Stories transform / emit_story_javascript",
                    location=f"story_reference:{path}",
                )
        for path in workspace.ux_map.object_references:
            if not _exists(root, path):
                yield self.violation(
                    f"object reference {path!r} is bound but missing — "
                    "run Clean Engineering transform to javascript",
                    location=f"object_reference:{path}",
                )


def _exists(root: Path, path: str) -> bool:
    candidate = Path(path)
    if candidate.is_file():
        return True
    return (root / path).is_file() or (root.parent / path).is_file()
