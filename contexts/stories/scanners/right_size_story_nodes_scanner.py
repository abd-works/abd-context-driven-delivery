"""right-size-story-nodes — flag siblings that look like superficial variants."""

from __future__ import annotations

from typing import List, Tuple

from story_workspace_base import StoryWorkspaceScanner


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


def _walk_sub_epics(epic):
    for sub in epic.sub_epics:
        yield sub
        yield from _walk_sub_epics(sub)


class RightSizeStoryNodesScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_story_map():
            return
        for epic in workspace.story_map.epics:
            yield from self._check_siblings(
                "epic",
                epic.name,
                [(s.name, s) for s in epic.sub_epics],
            )
            for sub in _walk_sub_epics(epic):
                yield from self._check_siblings(
                    "sub-epic",
                    sub.name,
                    [(s.name, s) for s in sub.sub_epics],
                )
                yield from self._check_siblings(
                    "sub-epic",
                    sub.name,
                    [(st.name, st) for st in sub.stories],
                )

    def _check_siblings(
        self, parent_kind: str, parent_name: str, siblings: List[Tuple[str, object]]
    ):
        for i, (a_name, a_node) in enumerate(siblings):
            for b_name, _b_node in siblings[i + 1 :]:
                if len(a_name) <= 6 or len(b_name) <= 6:
                    continue
                if _char_diff(a_name, b_name) <= 2:
                    yield self.violation(
                        f"Siblings {a_name!r} and {b_name!r} under {parent_kind} "
                        f"{parent_name!r} differ by <=2 chars — likely superficial variant",
                        location=self.loc(a_node, f"{parent_kind} {parent_name!r}"),
                        severity="warning",
                    )
