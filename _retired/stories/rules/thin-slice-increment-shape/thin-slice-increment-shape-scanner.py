"""thin-slice-increment-shape — every increment carries an outcome and stories.

Mechanical check on `workspace.thin_slice`:
- Each increment has a non-empty `outcome` (the marketable-outcome line).
- Each increment has at least one story name.

`outcome` is populated by the thin_slice_loader from the `**Outcome:**` key-value
line under `### Increment N:` — see stories/templates/md/thin-slice.md.

"Vertical", "marketable", and "minimal" are AI-judge disciplines — the mechanical
check only enforces that the outcome sentence exists and stories are listed.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


class ThinSliceIncrementShapeScanner(ArtifactScanner):
    """Every thin-slice increment has an outcome and at least one story."""
    rule = "thin-slice-increment-shape"
    kind = "shape"
    reads = ("increments",)

    def scan(self) -> Iterator[Violation]:
        if not self.workspace.has_increments():
            return
        for inc in self.workspace.story_map.increments:
            if not inc.outcome.strip():
                yield Violation(
                    rule=self.rule,
                    message=f"Increment {inc.name!r} has no **Outcome:** line",
                    location=self.location(inc.source, f"increment {inc.name!r}"),
                    severity="error",
                    hint=(
                        "Add `**Outcome:** <one line — what users or the business can "
                        "do after this ships>` under the increment heading"
                    ),
                )
                continue
            if not inc.stories:
                yield Violation(
                    rule=self.rule,
                    message=f"Increment {inc.name!r} has no stories",
                    location=self.location(inc.source, f"increment {inc.name!r}"),
                    severity="error",
                    hint="Add `**Stories in this increment:**` followed by bullet-listed story names",
                )


if __name__ == "__main__":
    sys.exit(run(ThinSliceIncrementShapeScanner))
