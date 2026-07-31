"""parallel-structure-across-connected-domains - sibling domain epics stay in sync."""

from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List, Tuple

from story_workspace_base import StoryWorkspaceScanner

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-']*")


def _frame(name: str):
    words = _WORD_RE.findall(name)
    if len(words) < 2:
        return None
    return (words[0].lower(), words[-1].lower())


class ParallelStructureAcrossConnectedDomainsScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_story_map():
            return
        clusters: Dict[Tuple[str, str], List] = {}
        for epic in workspace.story_map.epics:
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
                yield self.violation(
                    f"Epic {epic.name!r} has {count} sub-epics, but siblings in "
                    f"the {frame[0].capitalize()} ... {frame[1].capitalize()} "
                    f"cluster have {baseline}",
                    location=self.loc(epic, f"epic {epic.name!r}"),
                    severity="warning",
                )
