"""four-to-nine-children — every parent has 4–9 direct children."""

from __future__ import annotations

from story_workspace_base import StoryWorkspaceScanner


def _band(count: int) -> str | None:
    if 4 <= count <= 9:
        return None
    if count in (3, 10):
        return "warning"
    return "error"


def _walk_sub_epics(epic_or_sub):
    for sub in getattr(epic_or_sub, "sub_epics", []) or []:
        yield sub
        yield from _walk_sub_epics(sub)


class FourToNineChildrenScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        if workspace.has_story_map():
            for epic in workspace.story_map.epics:
                yield from self._check(epic, "epic", "sub-epics", len(epic.sub_epics))
                for sub in _walk_sub_epics(epic):
                    child_count = len(sub.sub_epics) + len(sub.stories)
                    label = (
                        "children"
                        if sub.sub_epics and sub.stories
                        else ("sub-epics" if sub.sub_epics else "stories")
                    )
                    yield from self._check(sub, "sub-epic", label, child_count)
        if workspace.has_increments():
            for inc in workspace.story_map.increments:
                yield from self._check(inc, "increment", "stories", len(inc.stories))
        for sc in workspace.scenarios:
            yield from self._check(sc, "scenario", "clauses", sc.clause_count)

    def _check(self, node, kind_label: str, child_label: str, count: int):
        if count == 0:
            return
        severity = _band(count)
        if severity is None:
            return
        name = getattr(node, "name", None) or "?"
        yield self.violation(
            f"{kind_label} {name!r}: {count} {child_label} (target 4-9)",
            location=self.loc(node, f"{kind_label} {name!r}"),
            severity=severity,
        )
