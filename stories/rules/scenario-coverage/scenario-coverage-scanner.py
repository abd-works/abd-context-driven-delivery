"""scenario-coverage — every story in the in-scope delivery has at least one scenario.

Mechanical check: for each Story name that is in scope, at least one
Scenario in `workspace.scenarios` must slug-match it.

Scope determination:
- No thin-slice increments → sub-epic scope: only stories in sub-epics that
  already have at least one scenario are required.
- Thin-slice increments present → increment scope: only stories in increments
  that already have at least one scenario are required.  This avoids false
  positives when increment 1 is explored but later increments share the same
  sub-epic (e.g. "Attach memo to transfer" in increment 2 of Compose transfer).

Deep coverage disciplines (happy + error + boundary + channel enumeration)
are AI-judge territory — this scanner catches only the "no scenario at all"
gap for a story that is already in scope.
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


class ScenarioCoverageScanner(ArtifactScanner):
    """Every in-scope story has at least one scenario."""
    rule = "scenario-coverage"
    kind = "quality"
    reads = ("story_map", "scenarios")

    def scan(self) -> Iterator[Violation]:
        if not self.workspace.has_story_map():
            return

        scenario_story_slugs: Set[str] = set()
        for sc in self.workspace.scenarios:
            if sc.story_name:
                scenario_story_slugs.add(_slug(sc.story_name))

        # Determine in-scope story slugs.
        # When thin-slice increments are present, a "touched" increment is one
        # where at least one of its stories already has a scenario.  Only stories
        # inside touched increments are required — this prevents false positives
        # when increment 1 is explored but later increments also share the same
        # sub-epic (e.g. "Attach memo to transfer" in increment 2 of Compose
        # transfer).  When no increments are present, fall back to sub-epic scope.
        increments = self.workspace.increments
        touched_story_slugs: Set[str] = set()

        if increments:
            for inc in increments:
                inc_slugs = {_slug(name) for name in inc.stories}
                if inc_slugs & scenario_story_slugs:
                    touched_story_slugs.update(inc_slugs)
        else:
            for epic in self.workspace.story_map.epics:
                for sub in _walk_sub_epics(epic):
                    sub_slugs = {_slug(s.name) for s in sub.stories}
                    if sub_slugs & scenario_story_slugs:
                        touched_story_slugs.update(sub_slugs)

        # If nothing is covered yet, fall back to requiring all stories.
        in_scope: Set[str] | None = touched_story_slugs if touched_story_slugs else None

        for epic in self.workspace.story_map.epics:
            for sub in _walk_sub_epics(epic):
                for story in sub.stories:
                    story_slug = _slug(story.name)
                    if in_scope is not None and story_slug not in in_scope:
                        continue
                    if story_slug not in scenario_story_slugs:
                        yield Violation(
                            rule=self.rule,
                            message=(
                                f"Story {story.name!r} has no scenarios in the workspace"
                            ),
                            location=self.location(
                                getattr(story, "source", None), f"story {story.name!r}"
                            ),
                            severity="warning",
                            hint=(
                                "Add at least one scenario under `scenarios/` with a "
                                "`## Story:` heading naming this story"
                            ),
                        )


def _walk_sub_epics(epic_or_sub):
    for sub in epic_or_sub.sub_epics:
        yield sub
        for nested in _walk_sub_epics(sub):
            yield nested


if __name__ == "__main__":
    sys.exit(run(ScenarioCoverageScanner))
