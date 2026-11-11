"""LERN rule that a person's story is done only when a screen does it."""

from __future__ import annotations

import re
from pathlib import Path

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.skipped_folders import scanned_files

_SCREEN_STORY_FILE = re.compile(r"(\.story\.ui\.spec\.ts|\.story\.playwright\.ts|\.playwright\.ts)$")
_DESCRIBED = re.compile(r"""(?:test\.)?describe\(\s*(['"`])(.+?)\1""")


class UserStoriesHaveAFrontEnd(PracticeGraphRule):
    """A user story is something a person does, so it is not done until a screen lets them do it. Only system and
    technical stories may have no front end. A screen story, a Playwright file whose describe names the story, is what
    shows the screen does it."""

    slug = "user-stories-have-a-front-end"
    node_types = ("Story",)

    def check_practice(self, context) -> list[tuple[str, str]]:
        shown = self._screen_stories(context.source_root)
        return [
            (story.node_id, f"{story.source.file}: user story `{story.name}` has no front end: no screen story "
                       f"(`*.story.ui.spec.ts` or Playwright file) describes it; build its screen and drive it there.")
            for story in context.nodes("Story")
            if story.get_fact("story_type", "user") == "user" and _key(story.name) not in shown
        ]

    def _screen_stories(self, root: Path | None) -> set[str]:
        """Every story a screen story file under root describes, by its name."""
        if root is None:
            return set()
        names: set[str] = set()
        for file in scanned_files(root):
            if _SCREEN_STORY_FILE.search(file.name):
                text = file.read_text(encoding="utf-8", errors="replace")
                names.update(_key(match.group(2)) for match in _DESCRIBED.finditer(text))
        return names


def _key(name: str) -> str:
    return " ".join(name.lower().split())
