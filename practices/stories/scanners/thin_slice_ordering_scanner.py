"""thin-slice-ordering - every increment names a decision prompt."""

from __future__ import annotations

import re
from typing import Set

from story_workspace_base import StoryWorkspaceScanner


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")


def _walk_sub_epics(epic_or_sub):
    for sub in epic_or_sub.sub_epics:
        yield sub
        yield from _walk_sub_epics(sub)


class ThinSliceOrderingScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_increments():
            return

        map_slugs: Set[str] = set()
        if workspace.has_story_map():
            for epic in workspace.story_map.epics:
                for sub in _walk_sub_epics(epic):
                    for story in sub.stories:
                        map_slugs.add(_slug(story.name))

        for inc in workspace.story_map.increments:
            if not (inc.decision_prompt or "").strip():
                yield self.violation(
                    f"Increment {inc.name!r} has no **Decision prompt:** line",
                    location=self.loc(inc, f"increment {inc.name!r}"),
                    severity="warning",
                )
                continue

            if map_slugs:
                for story_name in inc.stories:
                    if _slug(story_name) not in map_slugs:
                        yield self.violation(
                            f"Increment {inc.name!r} lists story {story_name!r} "
                            f"which is not in the story map",
                            location=self.loc(inc, f"increment {inc.name!r}"),
                            severity="error",
                        )
