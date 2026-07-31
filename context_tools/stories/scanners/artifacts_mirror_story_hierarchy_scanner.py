"""artifacts-mirror-story-hierarchy - scenarios and suites follow the map.

Uses only Workspace model fields. Path shape is language-agnostic.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Set, Tuple

from story_workspace_base import StoryWorkspaceScanner


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")


def _walk_sub_epics(epic_or_sub):
    for sub in epic_or_sub.sub_epics:
        yield sub
        yield from _walk_sub_epics(sub)


def _build_story_path_map(workspace) -> Dict[str, Tuple[str, str]]:
    result: Dict[str, Tuple[str, str]] = {}
    for epic in workspace.story_map.epics:
        epic_slug = _slug(epic.name)
        for sub in _walk_sub_epics(epic):
            sub_slug = _slug(sub.name)
            for story in sub.stories:
                result[_slug(story.name)] = (epic_slug, sub_slug)
    return result


class ArtifactsMirrorStoryHierarchyScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_story_map():
            return

        story_slugs: Set[str] = set()
        for epic in workspace.story_map.epics:
            for sub in _walk_sub_epics(epic):
                for story in sub.stories:
                    story_slugs.add(_slug(story.name))

        for sc in workspace.scenarios:
            ref = sc.story_name.strip()
            if not ref:
                continue
            if _slug(ref) in story_slugs:
                continue
            yield self.violation(
                f"Scenario {sc.name!r} references story {ref!r} which is not in the story map",
                location=self.loc(sc, f"scenario {sc.name!r}"),
                severity="warning",
            )

        story_path_map = _build_story_path_map(workspace)
        if not story_path_map:
            return

        for suite in workspace.test_suites:
            if not suite.source:
                continue
            rel = suite.source.file.replace("\\", "/")
            parts = Path(rel).parts
            path_slugs = [_slug(p) for p in parts]
            matched = False
            for story_slug, (epic_slug, sub_slug) in story_path_map.items():
                try:
                    ei = path_slugs.index(epic_slug)
                    si = path_slugs.index(sub_slug)
                    if si > ei and any(story_slug in ps for ps in path_slugs[si:]):
                        matched = True
                        break
                except ValueError:
                    continue
            if not matched:
                yield self.violation(
                    f"Code file {rel!r} is not under its story map hierarchy "
                    f"({'{epic}/{sub-epic}/{story-slug}/'} folder structure required)",
                    location=self.loc(suite, rel),
                    severity="error",
                )
