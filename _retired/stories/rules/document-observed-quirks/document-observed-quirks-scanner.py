"""document-observed-quirks — no bare TODO/FIXME/HACK markers in artifacts.

The rule requires anomalies to be documented on the artifact using the
canonical shapes: `## Context gaps` sections, `_Observed quirk:_` inline
notes. Anything else — TODO comments, FIXME markers, "we should" prose —
signals an anomaly that hasn't been properly captured.

Mechanical check: scan the raw text of every scenario file and every
story-context sheet for bare `TODO`, `FIXME`, or `HACK` markers. If any
appear, flag them and point the author at the canonical documentation
shape.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


_BARE_MARKER = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b")


class DocumentObservedQuirksScanner(ArtifactScanner):
    """Bare TODO / FIXME markers are undocumented quirks."""
    rule = "document-observed-quirks"
    kind = "shape"
    reads = ("scenarios",)

    def scan(self) -> Iterator[Violation]:
        seen_paths: set[str] = set()
        for sc in self.workspace.scenarios:
            if sc.source is None:
                continue
            path = self.workspace.root / sc.source.file
            if not path.exists() or sc.source.file in seen_paths:
                continue
            seen_paths.add(sc.source.file)
            yield from self._scan_file(path, sc.source.file)
        for ctx in self.workspace.story_contexts:
            if ctx.source is None:
                continue
            if ctx.source.file in seen_paths:
                continue
            path = self.workspace.root / ctx.source.file
            if not path.exists():
                continue
            seen_paths.add(ctx.source.file)
            yield from self._scan_file(path, ctx.source.file)

    def _scan_file(self, path, rel_file) -> Iterator[Violation]:
        text = path.read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), start=1):
            m = _BARE_MARKER.search(line)
            if not m:
                continue
            yield Violation(
                rule=self.rule,
                message=(
                    f"{rel_file}:{i} contains a bare {m.group(1)} marker — "
                    f"convert to `## Context gaps` bullet or `_Observed quirk:_` note"
                ),
                location=f"{rel_file}:{i}",
                severity="warning",
                hint=(
                    "Document anomalies inside the artifact using the canonical "
                    "shape: `## Context gaps` with a bullet, or an inline "
                    "`_Observed quirk: …_` next to the citation"
                ),
            )
            return


if __name__ == "__main__":
    sys.exit(run(DocumentObservedQuirksScanner))
