"""scenario-coverage - every in-scope story has at least one scenario."""

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


class ScenarioCoverageScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_story_map():
            return

        scenario_story_slugs: Set[str] = set()
        for sc in workspace.scenarios:
            if sc.story_name:
                scenario_story_slugs.add(_slug(sc.story_name))

        increments = workspace.increments
        touched_story_slugs: Set[str] = set()

        if increments:
            for inc in increments:
                inc_slugs = {_slug(name) for name in inc.stories}
                if inc_slugs & scenario_story_slugs:
                    touched_story_slugs.update(inc_slugs)
        else:
            for epic in workspace.story_map.epics:
                for sub in _walk_sub_epics(epic):
                    sub_slugs = {_slug(s.name) for s in sub.stories}
                    if sub_slugs & scenario_story_slugs:
                        touched_story_slugs.update(sub_slugs)

        in_scope: Set[str] | None = touched_story_slugs if touched_story_slugs else None

        for epic in workspace.story_map.epics:
            for sub in _walk_sub_epics(epic):
                for story in sub.stories:
                    story_slug = _slug(story.name)
                    if in_scope is not None and story_slug not in in_scope:
                        continue
                    if story_slug not in scenario_story_slugs:
                        yield self.violation(
                            f"Story {story.name!r} has no scenarios in the workspace",
                            location=self.loc(story, f"story {story.name!r}"),
                            severity="warning",
                        )
