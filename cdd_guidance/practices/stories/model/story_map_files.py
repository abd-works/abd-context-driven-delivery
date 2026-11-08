"""Where story maps sit. This is the one place that knows a story map's file name and which folders are searched for
one, so the practice, the markdown format, and a story test's reader all find the same files."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from harness.annotations.name import Name

STORY_MAP_SUFFIXES = (".md", ".drawio")
# Documents go in a folder's `.context` while code sits straight in the folder, so a story map may sit in either.
CONTEXT_FOLDER = ".context"
_MARKDOWN = ".md"


def is_story_map_file(path) -> bool:
    """A story map is a markdown or drawio file named story-map (or story_map), alone or after a prefix."""
    path = Path(path)
    stem = Name(path.stem).title_slug
    return path.suffix.lower() in STORY_MAP_SUFFIXES and (stem == "story-map" or stem.endswith("-story-map"))


class StoryMapFiles:
    """The story maps around one folder: the one in it or the nearest folder above it, and the ones below it."""

    def __init__(self, folder: Path) -> None:
        folder = Path(folder).resolve()
        self.folder = folder.parent if folder.is_file() else folder

    def nearest(self) -> Optional[Path]:
        """The story map in this folder or the nearest folder above it, or in that folder's ``.context``: its markdown
        when it has one, since a drawio of the same map would add every Story twice."""
        for candidate in (self.folder, *self.folder.parents):
            maps = self._maps_in(candidate)
            if maps:
                markdown = [path for path in maps if path.suffix.lower() == _MARKDOWN]
                return (markdown or maps)[0]
        return None

    def markdown_below(self) -> List[Path]:
        """The markdown story maps this folder holds: its own when it has one, else every one in the folders below it."""
        own = [path for path in self._maps_in(self.folder) if path.suffix.lower() == _MARKDOWN]
        if own:
            return own
        return sorted(path.resolve() for path in self.folder.rglob(f"*{_MARKDOWN}") if is_story_map_file(path))

    def _maps_in(self, folder: Path) -> List[Path]:
        context = folder / CONTEXT_FOLDER
        beside = list(context.iterdir()) if context.is_dir() else []
        return sorted(path.resolve() for path in [*folder.iterdir(), *beside] if path.is_file() and is_story_map_file(path))
