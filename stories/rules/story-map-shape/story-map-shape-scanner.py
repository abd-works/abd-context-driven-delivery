"""story-map-shape — validates the fundamental Patton skeleton.

The loader normalises heading form and outline `(E)`/`(S)` form to the same
StoryMap object model, so this scanner runs uniformly on either.

Required members:
1. StoryMap has at least one Epic (outcome)
2. Every Epic has at least one SubEpic (activity)
3. Every leaf SubEpic (one with no nested sub-epics) has at least one Story
4. At least one Story in the whole map has a named actor (`users` non-empty)
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


class StoryMapShapeScanner(ArtifactScanner):
    """Every story-map.md has outcomes, activities, stories, and named actors."""
    rule = "story-map-shape"
    kind = "shape"
    reads = ("story_map",)

    def scan(self) -> Iterator[Violation]:
        sm = self.workspace.story_map

        if not self.workspace.has_story_map():
            yield Violation(
                rule=self.rule,
                message="No story map found or story map contains no epics",
                location="story-map.md",
                severity="error",
                hint="Add at least one `(E)` epic or `##` outcome to story-map.md",
            )
            return

        any_actor = False
        for epic in sm.epics:
            if not epic.sub_epics:
                yield Violation(
                    rule=self.rule,
                    message=f"Epic {epic.name!r} has no sub-epics (activities)",
                    location=self.location(getattr(epic, "source", None), f"epic {epic.name!r}"),
                    severity="error",
                    hint="Add at least one `(E)` sub-epic or `###` activity under this epic",
                )
                continue
            yield from self._check_sub_epic(epic)
            for story in _iter_all_stories(epic):
                if story.users:
                    any_actor = True

        if not any_actor:
            yield Violation(
                rule=self.rule,
                message="No story in the map names an actor",
                location="story-map.md",
                severity="error",
                hint=(
                    "Name at least one actor via the outline (S) Actor --> Story "
                    "or a **Actor:** prefix on a story"
                ),
            )

    def _check_sub_epic(self, sub_epic) -> Iterator[Violation]:
        # A leaf sub-epic (no nested sub-epics) must have at least one story
        # OR a shaping estimate for unmapped work.
        if not sub_epic.sub_epics and not sub_epic.stories:
            estimate = (sub_epic.estimate or "").strip()
            if not estimate:
                yield Violation(
                    rule=self.rule,
                    message=f"Leaf sub-epic {sub_epic.name!r} has no stories",
                    location=self.location(getattr(sub_epic, "source", None), f"sub-epic {sub_epic.name!r}"),
                    severity="error",
                    hint=(
                        "Add at least one (S) Actor --> Verb-Noun story, "
                        "or a shaping estimate line * approx N-M more stories (...)"
                    ),
                )
        for nested in sub_epic.sub_epics:
            yield from self._check_sub_epic(nested)


def _iter_all_stories(epic):
    for sub_epic in _iter_all_sub_epics(epic):
        yield from sub_epic.stories


def _iter_all_sub_epics(epic):
    for sub in epic.sub_epics:
        yield sub
        yield from _iter_all_sub_epics(sub)


if __name__ == "__main__":
    sys.exit(run(StoryMapShapeScanner))
