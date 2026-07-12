"""thin-slice-shape — validates the fundamental increments skeleton.

Required members:
1. `story_map.increments` has at least one Increment
2. Every Increment lists at least one story

Increments now live on `StoryMap.increments` per `domain-context.md`; the old
`ThinSlice` wrapper has been removed. The workspace exposes
`has_increments()` as the canonical guard.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


class ThinSliceShapeScanner(ArtifactScanner):
    """Every thin-slicing.md has at least one increment and each lists stories."""
    rule = "thin-slice-shape"
    kind = "shape"
    reads = ("increments",)

    def scan(self) -> Iterator[Violation]:
        if not self.workspace.has_increments():
            yield Violation(
                rule=self.rule,
                message="No thin-slice found or thin-slice contains no increments",
                location="thin-slicing.md",
                severity="error",
                hint="Add at least one `### Increment N: <outcome>` block to thin-slicing.md",
            )
            return

        for increment in self.workspace.story_map.increments:
            if not increment.stories:
                yield Violation(
                    rule=self.rule,
                    message=f"Increment {increment.name!r} lists no stories",
                    location=self.location(getattr(increment, "source", None), f"increment {increment.name!r}"),
                    severity="error",
                    hint=(
                        "Add a `**Stories in this increment:**` block with at least "
                        "one story name (must match a story in the story map)"
                    ),
                )


if __name__ == "__main__":
    sys.exit(run(ThinSliceShapeScanner))
