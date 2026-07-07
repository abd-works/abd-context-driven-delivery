"""parallel-structure-across-connected-domains — sibling domain epics stay in sync.

When two epics share a name frame — same first word and same last word,
e.g. `Make Wire Payment` / `Make ACH Payment` — the rule requires their
downstream shape (sub-epic count, story count) to match so the domain
comparison stays legible.

Mechanical check:
- Cluster epics by `(first_token.lower(), last_token.lower())`.
- Within each cluster of size >= 2, compare `len(epic.sub_epics)`.
- Any cluster whose sub-epic counts are not all equal yields one violation
  per outlier epic (against the cluster's most common count).

The nested comparison of matching sub-epic names / story counts is
AI-judge territory — this scanner catches the coarse mismatch.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Iterator, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


_WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-']*")


def _frame(name: str):
    words = _WORD_RE.findall(name)
    if len(words) < 2:
        return None
    return (words[0].lower(), words[-1].lower())


class ParallelStructureScanner(ArtifactScanner):
    """Sibling domain epics stay parallel."""
    rule = "parallel-structure-across-connected-domains"
    kind = "quality"
    reads = ("story_map",)

    def scan(self) -> Iterator[Violation]:
        if not self.workspace.has_story_map():
            return
        clusters: Dict[Tuple[str, str], List] = {}
        for epic in self.workspace.story_map.epics:
            frame = _frame(epic.name)
            if frame is None:
                continue
            clusters.setdefault(frame, []).append(epic)

        for frame, cluster in clusters.items():
            if len(cluster) < 2:
                continue
            counts = [len(e.sub_epics) for e in cluster]
            if len(set(counts)) <= 1:
                continue
            baseline = Counter(counts).most_common(1)[0][0]
            for epic, count in zip(cluster, counts):
                if count == baseline:
                    continue
                yield Violation(
                    rule=self.rule,
                    message=(
                        f"Epic {epic.name!r} has {count} sub-epics, but siblings in "
                        f"the {frame[0].capitalize()} … {frame[1].capitalize()} "
                        f"cluster have {baseline}"
                    ),
                    location=self.location(getattr(epic, "source", None), f"epic {epic.name!r}"),
                    severity="warning",
                    hint=(
                        "Give sibling domains the same sub-epic and story shape; "
                        "diverge only where mechanics genuinely differ"
                    ),
                )


if __name__ == "__main__":
    sys.exit(run(ParallelStructureScanner))
