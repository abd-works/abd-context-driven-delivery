"""artifacts-mirror-story-hierarchy — every downstream artifact traces to a story
and code files follow the story map folder hierarchy.

The story map is canonical. This scanner enforces:

1. **Scenario traceability** — each `Scenario.story_name` must match a Story in
   the story map. Orphan scenarios yield a violation.

2. **Code file hierarchy** — every test-suite file (`.test.ts`, `.test.tsx`,
   `.spec.ts`, `-stories.ts`, `.test.py`, `.test.js`, etc.) must be placed
   under a folder path that contains `{epic-slug}/{sub-epic-slug}/{story-slug}/`.
   Files that sit flat (e.g. `draft-transfer-details-stories.ts` at the root)
   are flagged because they cannot be navigated without knowing the story map.

Missing scenarios for map stories are `scenario-coverage`'s job.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, Iterator, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")


# File suffixes that must follow the story map hierarchy.
_CODE_SUFFIXES = (
    "-stories.ts",
    "-stories.tsx",
    "-stories.py",
    "-stories.js",
    ".test.ts",
    ".test.tsx",
    ".test.py",
    ".test.js",
    ".spec.ts",
    ".spec.tsx",
    ".spec.py",
    ".spec.js",
)


def _is_code_artifact(rel_path: str) -> bool:
    lower = rel_path.lower()
    return any(lower.endswith(s) for s in _CODE_SUFFIXES)


def _build_story_path_map(workspace) -> Dict[str, Tuple[str, str]]:
    """Return {story-slug: (epic-slug, sub-epic-slug)} for all stories."""
    result: Dict[str, Tuple[str, str]] = {}
    for epic in workspace.story_map.epics:
        epic_slug = _slug(epic.name)
        for sub in _walk_sub_epics(epic):
            sub_slug = _slug(sub.name)
            for story in sub.stories:
                result[_slug(story.name)] = (epic_slug, sub_slug)
    return result


class ArtifactsMirrorStoryHierarchyScanner(ArtifactScanner):
    """Scenarios trace to the story map; code files follow its folder hierarchy."""
    rule = "artifacts-mirror-story-hierarchy"
    kind = "shape"
    reads = ("story_map", "scenarios", "test_suites")

    def scan(self) -> Iterator[Violation]:
        if not self.workspace.has_story_map():
            return

        story_slugs: Set[str] = set()
        for epic in self.workspace.story_map.epics:
            for sub in _walk_sub_epics(epic):
                for story in sub.stories:
                    story_slugs.add(_slug(story.name))

        # 1. Scenario traceability.
        for sc in self.workspace.scenarios:
            ref = sc.story_name.strip()
            if not ref:
                continue
            if _slug(ref) in story_slugs:
                continue
            yield Violation(
                rule=self.rule,
                message=(
                    f"Scenario {sc.name!r} references story {ref!r} which is not in the story map"
                ),
                location=self.location(sc.source, f"scenario {sc.name!r}"),
                severity="warning",
                hint=(
                    "Either add the story to the story map, or fix the scenario's "
                    "`## Story:` heading / folder name to match an existing story"
                ),
            )

        # 2. Code file hierarchy check.
        story_path_map = _build_story_path_map(self.workspace)
        for suite in self.workspace.test_suites:
            if not suite.source:
                continue
            rel = suite.source.file.replace("\\", "/")
            if not _is_code_artifact(rel):
                continue
            parts = Path(rel).parts
            # Expect at least epic/sub-epic/story-slug/ somewhere in the path.
            path_slugs = [_slug(p) for p in parts]
            matched = False
            for story_slug, (epic_slug, sub_slug) in story_path_map.items():
                try:
                    ei = path_slugs.index(epic_slug)
                    si = path_slugs.index(sub_slug)
                    # story slug must appear somewhere after sub-epic
                    if si > ei and any(
                        story_slug in ps for ps in path_slugs[si:]
                    ):
                        matched = True
                        break
                except ValueError:
                    continue
            if not matched:
                yield Violation(
                    rule=self.rule,
                    message=(
                        f"Code file {rel!r} is not under its story map hierarchy "
                        f"({'{epic}/{sub-epic}/{story-slug}/'} folder structure required)"
                    ),
                    location=self.location(suite.source, rel),
                    severity="error",
                    hint=(
                        "Place code files under `{epic-slug}/{sub-epic-slug}/{story-slug}/` "
                        "so the folder structure mirrors the story map. "
                        "Example: move-money/compose-transfer/draft-transfer-details/"
                        "draft-transfer-details-stories.ts"
                    ),
                )


def _walk_sub_epics(epic_or_sub):
    for sub in epic_or_sub.sub_epics:
        yield sub
        for nested in _walk_sub_epics(sub):
            yield nested


if __name__ == "__main__":
    sys.exit(run(ArtifactsMirrorStoryHierarchyScanner))
