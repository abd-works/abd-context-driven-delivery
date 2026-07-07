"""brownfield-story-mapping — no lingering UNVERIFIED evidence markers.

From `brownfield-story-mapping.md`:
> If none [no evidence] is available, mark the story `_Evidence: **UNVERIFIED**_`
> and treat it as speculative until confirmed.

The mechanical check is: after the story has been through discovery, no
`**UNVERIFIED**` markers should remain in the corresponding story-context
sheets. The presence of one is a signal that evidence collection stalled
and the story is still speculative.

The `story-context/*.md` sheets are the canonical place for evidence
citations (see the story-context template). This scanner reads their raw
text to preserve the exact `_Evidence: **UNVERIFIED**_` phrasing.

Other brownfield disciplines (map observed behaviour verbatim, keep a
separate redesign-candidates list, cite endpoints/code paths in Sources)
are AI-judge territory — the templates do not enforce a machine-detectable
citation format.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


_UNVERIFIED_MARKER = "**UNVERIFIED**"


class BrownfieldStoryMappingScanner(ArtifactScanner):
    """No `**UNVERIFIED**` evidence markers survive in story-context sheets."""
    rule = "brownfield-story-mapping"
    kind = "quality"
    reads = ("story_map",)

    def scan(self) -> Iterator[Violation]:
        for ctx in self.workspace.story_contexts:
            source = ctx.source
            if source is None:
                continue
            source_path = self.workspace.root / source.file
            if not source_path.exists():
                continue
            text = source_path.read_text(encoding="utf-8", errors="replace")
            if _UNVERIFIED_MARKER in text:
                yield Violation(
                    rule=self.rule,
                    message=(
                        f"Story context {source.file} still marks evidence as {_UNVERIFIED_MARKER}"
                    ),
                    location=source.render(),
                    severity="warning",
                    hint=(
                        "Cite a code path, endpoint, screen, or observation "
                        "(see brownfield-story-mapping.md § 'Evidence formats "
                        "accepted') — or drop the story"
                    ),
                )


if __name__ == "__main__":
    sys.exit(run(BrownfieldStoryMappingScanner))
