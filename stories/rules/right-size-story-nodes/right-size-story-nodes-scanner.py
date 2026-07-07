"""right-size-story-nodes — flag siblings that look like superficial variants.

Companion to four-to-nine-children: that scanner checks *count*, this one
checks *shape* of the names within a parent.

Mechanical check (semantic distinct-mechanics detection is AI-judge territory):
- Two sibling nodes (siblings of the same parent, in the story map) whose
  names differ by <= 2 characters and are longer than 6 chars are flagged
  as likely superficial variants — merge into one parameterised node or
  make the difference explicit.

Named-conjunction check is not performed here to keep the scanner
conservative; `right-size-story-nodes.md` calls out plenty of AI-judge cases
that we intentionally do not encode.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


def _char_diff(a: str, b: str) -> int:
    if abs(len(a) - len(b)) > 5:
        return 999
    la, lb = a.lower(), b.lower()
    if la == lb:
        return 0
    diff = abs(len(la) - len(lb))
    for x, y in zip(la, lb):
        if x != y:
            diff += 1
    return diff


class RightSizeStoryNodesScanner(ArtifactScanner):
    """Flag sibling story-map nodes that look like superficial variants."""
    rule = "right-size-story-nodes"
    kind = "quality"
    reads = ("story_map",)

    def scan(self) -> Iterator[Violation]:
        if not self.workspace.has_story_map():
            return
        for epic in self.workspace.story_map.epics:
            yield from self._check_siblings(
                "epic",
                epic.name,
                [(s.name, getattr(s, "source", None)) for s in epic.sub_epics],
            )
            for sub in _walk_sub_epics(epic):
                yield from self._check_siblings(
                    "sub-epic",
                    sub.name,
                    [(s.name, getattr(s, "source", None)) for s in sub.sub_epics],
                )
                yield from self._check_siblings(
                    "sub-epic",
                    sub.name,
                    [(st.name, getattr(st, "source", None)) for st in sub.stories],
                )

    def _check_siblings(
        self, parent_kind: str, parent_name: str, siblings: List[Tuple[str, object]]
    ) -> Iterator[Violation]:
        for i, (a_name, a_src) in enumerate(siblings):
            for b_name, _b_src in siblings[i + 1 :]:
                if len(a_name) <= 6 or len(b_name) <= 6:
                    continue
                if _char_diff(a_name, b_name) <= 2:
                    yield Violation(
                        rule=self.rule,
                        message=(
                            f"Siblings {a_name!r} and {b_name!r} under {parent_kind} "
                            f"{parent_name!r} differ by <=2 chars — likely superficial variant"
                        ),
                        location=self.location(a_src, f"{parent_kind} {parent_name!r}"),
                        severity="warning",
                        hint=(
                            "Merge into one parameterised story or make the mechanical "
                            "difference explicit (actor, channel, failure mode)"
                        ),
                    )


def _walk_sub_epics(epic):
    for sub in epic.sub_epics:
        yield sub
        for nested in _walk_sub_epics(sub):
            yield nested


if __name__ == "__main__":
    sys.exit(run(RightSizeStoryNodesScanner))
