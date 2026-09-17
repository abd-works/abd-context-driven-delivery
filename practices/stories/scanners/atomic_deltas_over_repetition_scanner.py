"""atomic-deltas-over-repetition - sibling scenarios sharing prefix -> Background."""

from __future__ import annotations

import re
from collections import defaultdict
from itertools import combinations
from typing import Dict, List

from story_workspace_base import StoryWorkspaceScanner


def _normalise(text: str) -> str:
    stripped = re.sub(r"[`*_]", "", text).strip().lower()
    return re.sub(r"\s+", " ", stripped)


class AtomicDeltasOverRepetitionScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        by_file: Dict[str, List] = defaultdict(list)
        for sc in workspace.scenarios:
            key = sc.source.file if sc.source else ""
            by_file[key].append(sc)

        for _file, group in by_file.items():
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
                    yield self.violation(
                        f"Scenarios {group[i].name!r} and {later.name!r} "
                        f"share their first {shared} step(s) - factor into "
                        f"a Background block or state the general case once",
                        location=self.loc(later, f"scenario {later.name!r}"),
                        severity="warning",
                    )
                    return
