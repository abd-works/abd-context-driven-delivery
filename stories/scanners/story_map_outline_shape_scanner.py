"""story-map-outline-shape — shaping fidelity outline constraints."""

from __future__ import annotations

from story_workspace_base import StoryWorkspaceScanner


def _iter_all_sub_epics(node):
    for sub in node.sub_epics:
        yield sub
        yield from _iter_all_sub_epics(sub)


class StoryMapOutlineShapeScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_story_map():
            return

        sm = workspace.story_map
        has_estimate_only_sub_epic = False

        for epic in sm.epics:
            if not (epic.estimate or "").strip():
                yield self.violation(
                    f"Epic {epic.name!r} is missing an estimate line",
                    location=self.loc(epic, f"epic {epic.name!r}"),
                    severity="error",
                )

            for sub_epic in _iter_all_sub_epics(epic):
                if not (sub_epic.estimate or "").strip():
                    yield self.violation(
                        f"Sub-epic {sub_epic.name!r} is missing an estimate line",
                        location=self.loc(sub_epic, f"sub-epic {sub_epic.name!r}"),
                        severity="error",
                    )

                if not sub_epic.stories:
                    has_estimate_only_sub_epic = True

        if sm.epics and not has_estimate_only_sub_epic:
            yield self.violation(
                "Every sub-epic has named stories — map appears to be at discovery depth, not shaping",
                location="story-map.md",
                severity="warning",
            )
