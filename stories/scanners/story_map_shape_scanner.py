"""story-map-shape — validates the fundamental Patton skeleton."""

from __future__ import annotations

from story_workspace_base import StoryWorkspaceScanner


def _iter_all_sub_epics(epic):
    for sub in epic.sub_epics:
        yield sub
        yield from _iter_all_sub_epics(sub)


def _iter_all_stories(epic):
    for sub_epic in _iter_all_sub_epics(epic):
        yield from sub_epic.stories


class StoryMapShapeScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        sm = workspace.story_map

        if not workspace.has_story_map():
            yield self.violation(
                "No story map found or story map contains no epics",
                location="story-map.md",
                severity="error",
            )
            return

        any_actor = False
        for epic in sm.epics:
            if not epic.sub_epics:
                yield self.violation(
                    f"Epic {epic.name!r} has no sub-epics (activities)",
                    location=self.loc(epic, f"epic {epic.name!r}"),
                    severity="error",
                )
                continue
            for sub in epic.sub_epics:
                yield from self._check_sub_epic(sub)
            for story in _iter_all_stories(epic):
                if story.users:
                    any_actor = True

        if not any_actor:
            yield self.violation(
                "No story in the map names an actor",
                location="story-map.md",
                severity="error",
            )

    def _check_sub_epic(self, sub_epic):
        if not sub_epic.sub_epics and not sub_epic.stories:
            estimate = (sub_epic.estimate or "").strip()
            if not estimate:
                yield self.violation(
                    f"Leaf sub-epic {sub_epic.name!r} has no stories",
                    location=self.loc(sub_epic, f"sub-epic {sub_epic.name!r}"),
                    severity="error",
                )
        for nested in sub_epic.sub_epics:
            yield from self._check_sub_epic(nested)
