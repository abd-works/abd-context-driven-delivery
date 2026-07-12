"""story-map-outline-shape — validates shaping fidelity outline constraints.

Checks:
1. Every epic has an estimate line.
2. Every sub-epic has an estimate line.
3. At least one sub-epic is estimate-only (no named stories), confirming
   the map is at shaping depth, not discovery depth.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


class StoryMapOutlineShapeScanner(ArtifactScanner):
    """Shaping story-map has estimates on every epic/sub-epic and is not fully decomposed."""

    rule = "story-map-outline-shape"
    kind = "outline-shape"
    reads = ("story_map",)

    def scan(self) -> Iterator[Violation]:
        sm = self.workspace.story_map

        if not self.workspace.has_story_map():
            return

        has_estimate_only_sub_epic = False

        for epic in sm.epics:
            if not epic.estimate.strip():
                yield Violation(
                    rule=self.rule,
                    message=f"Epic {epic.name!r} is missing an estimate line",
                    location=self.location(getattr(epic, "source", None), f"epic {epic.name!r}"),
                    severity="error",
                    hint="Add '* approx N-M total stories' under the epic name",
                )

            for sub_epic in _iter_all_sub_epics(epic):
                if not sub_epic.estimate.strip():
                    yield Violation(
                        rule=self.rule,
                        message=f"Sub-epic {sub_epic.name!r} is missing an estimate line",
                        location=self.location(
                            getattr(sub_epic, "source", None),
                            f"sub-epic {sub_epic.name!r}",
                        ),
                        severity="error",
                        hint="Add '* approx N-M more stories (brief description)' under the sub-epic",
                    )

                if not sub_epic.stories:
                    has_estimate_only_sub_epic = True

        if sm.epics and not has_estimate_only_sub_epic:
            yield Violation(
                rule=self.rule,
                message="Every sub-epic has named stories — map appears to be at discovery depth, not shaping",
                location="story-map.md",
                severity="warning",
                hint=(
                    "At shaping fidelity at least one sub-epic should be estimate-only "
                    "(no named stories). Remove story names and replace with "
                    "'* approx N-M more stories (...)' for sub-epics not yet fully scoped."
                ),
            )


def _iter_all_sub_epics(node):
    for sub in node.sub_epics:
        yield sub
        yield from _iter_all_sub_epics(sub)


if __name__ == "__main__":
    sys.exit(run(StoryMapOutlineShapeScanner))
