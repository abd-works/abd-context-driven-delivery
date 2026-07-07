"""thin-slice-ordering — every increment names a decision prompt.

Mechanical check on `workspace.thin_slice`:
- Each increment has a non-empty `decision_prompt` (from `**Decision prompt:**`).

Story-name-matches-map is enforced by `artifacts-mirror-story-hierarchy` at the
scenario level. For thin-slice we additionally verify the story-name-verbatim
constraint when a story map is present in the workspace: each story listed in
an increment must exist in the story map (case-insensitive slug match).

Ordering by architectural risk / spine-first is AI-judge territory — the
mechanical check catches the missing-decision-prompt failure mode.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterator, Set

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")


class ThinSliceOrderingScanner(ArtifactScanner):
    """Every increment declares a decision prompt and lists real map stories."""
    rule = "thin-slice-ordering"
    kind = "shape"
    reads = ("increments", "story_map")

    def scan(self) -> Iterator[Violation]:
        if not self.workspace.has_increments():
            return

        map_slugs: Set[str] = set()
        if self.workspace.has_story_map():
            for epic in self.workspace.story_map.epics:
                for sub in _walk_sub_epics(epic):
                    for story in sub.stories:
                        map_slugs.add(_slug(story.name))

        for inc in self.workspace.story_map.increments:
            if not inc.decision_prompt.strip():
                yield Violation(
                    rule=self.rule,
                    message=f"Increment {inc.name!r} has no **Decision prompt:** line",
                    location=self.location(inc.source, f"increment {inc.name!r}"),
                    severity="warning",
                    hint=(
                        "Add `**Decision prompt:** <the question this increment answers>` — "
                        "every increment must state the question shipping it answers"
                    ),
                )
                continue

            if map_slugs:
                for story_name in inc.stories:
                    if _slug(story_name) not in map_slugs:
                        yield Violation(
                            rule=self.rule,
                            message=(
                                f"Increment {inc.name!r} lists story {story_name!r} "
                                f"which is not in the story map"
                            ),
                            location=self.location(inc.source, f"increment {inc.name!r}"),
                            severity="error",
                            hint="Copy the story name verbatim from story-map.md",
                        )


def _walk_sub_epics(epic_or_sub):
    for sub in epic_or_sub.sub_epics:
        yield sub
        for nested in _walk_sub_epics(sub):
            yield nested


if __name__ == "__main__":
    sys.exit(run(ThinSliceOrderingScanner))
