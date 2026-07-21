"""document-observed-quirks — no bare TODO/FIXME/HACK markers in artifacts."""

from __future__ import annotations

import re

from story_workspace_base import StoryWorkspaceScanner

_BARE_MARKER = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b")


class DocumentObservedQuirksScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        seen_paths: set[str] = set()
        for sc in workspace.scenarios:
            if sc.source is None:
                continue
            path = workspace.root / sc.source.file
            if not path.exists() or sc.source.file in seen_paths:
                continue
            seen_paths.add(sc.source.file)
            yield from self._scan_file(path, sc.source.file)
        for ctx in workspace.story_contexts:
            if ctx.source is None:
                continue
            if ctx.source.file in seen_paths:
                continue
            path = workspace.root / ctx.source.file
            if not path.exists():
                continue
            seen_paths.add(ctx.source.file)
            yield from self._scan_file(path, ctx.source.file)

    def _scan_file(self, path, rel_file):
        text = path.read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), start=1):
            m = _BARE_MARKER.search(line)
            if not m:
                continue
            yield self.violation(
                f"{rel_file}:{i} contains a bare {m.group(1)} marker — "
                f"convert to `## Context gaps` bullet or `_Observed quirk:_` note",
                location=f"{rel_file}:{i}",
                severity="warning",
            )
            return
