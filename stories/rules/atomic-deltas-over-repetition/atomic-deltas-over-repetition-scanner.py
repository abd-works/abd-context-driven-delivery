"""atomic-deltas-over-repetition — sibling scenarios share prefix -> factor to Background.

Pairs of scenarios in the same file sharing >= 3 leading normalised steps
are flagged: state the general case once (Background) and follow-ons should
describe only the delta.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Dict, Iterator, List

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


def _normalise(text: str) -> str:
    stripped = re.sub(r"[`*_]", "", text).strip().lower()
    return re.sub(r"\s+", " ", stripped)


class AtomicDeltasScanner(ArtifactScanner):
    """Sibling scenarios sharing 3+ leading steps should factor a Background."""
    rule = "atomic-deltas-over-repetition"
    kind = "quality"
    reads = ("scenarios",)

    def scan(self) -> Iterator[Violation]:
        by_file: Dict[str, List] = defaultdict(list)
        for sc in self.workspace.scenarios:
            key = sc.source.file if sc.source else ""
            by_file[key].append(sc)

        for file, group in by_file.items():
            if len(group) < 2:
                continue
            fingerprints = [
                [f"{clause.phase.value}:{_normalise(clause.text)}" for clause in sc.all_clauses]
                for sc in group
            ]
            for (i, a), (j, b) in combinations(list(enumerate(fingerprints)), 2):
                shared = 0
                for s1, s2 in zip(a, b):
                    if s1 == s2:
                        shared += 1
                    else:
                        break
                if shared >= 3:
                    later = group[j]
                    yield Violation(
                        rule=self.rule,
                        message=(
                            f"Scenarios {group[i].name!r} and {later.name!r} "
                            f"share their first {shared} step(s) — factor into "
                            f"a Background block or state the general case once"
                        ),
                        location=self.location(later.source, f"scenario {later.name!r}"),
                        severity="warning",
                        hint="Move shared Givens into a `Background:` block above the scenarios",
                    )
                    return


if __name__ == "__main__":
    sys.exit(run(AtomicDeltasScanner))
