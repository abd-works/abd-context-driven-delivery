"""Where story maps and story files sit. This is the one place that knows a story map's file name, a story's own file
name, the files scenarios and increments are written in, and which folders are searched for them, so the practice, the
markdown format, its links, and a story test's reader all find the same files."""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath
from typing import Iterator, List, Optional

from harness.annotations.name import Name
from harness.graph.skipped_folders import skips_folder

STORY_MAP_SUFFIXES = (".md", ".drawio")
# Documents go in a folder's `.context` while code sits straight in the folder, so a story map may sit in either.
CONTEXT_FOLDER = ".context"
_MARKDOWN = ".md"
# A story's own markdown file: `submit_order_story.test.md`, `submit_order_story.spec.md`.
STORY_FILE_SUFFIXES = ("_story.test.md", "_story.spec.md")
# The markdown a map's increments are written in, in the order a folder is searched for them.
THIN_SLICING_FILES = ("thin-slicing.md", "thin-slice.md", "thin-slices.md", "increments.md")


def is_story_map_file(path) -> bool:
    """A story map is a markdown or drawio file named story-map (or story_map), alone or after a prefix."""
    path = Path(path)
    stem = Name(path.stem).title_slug
    return path.suffix.lower() in STORY_MAP_SUFFIXES and (stem == "story-map" or stem.endswith("-story-map"))


class StoryMapFiles:
    """The story maps around one folder: the one in it or the nearest folder above it, up to the top folder the search
    stops at (the project the folder belongs to, when one is given), and the ones below it."""

    def __init__(self, folder: Path, top: Optional[Path] = None) -> None:
        folder = Path(folder).resolve()
        self.folder = folder.parent if folder.is_file() else folder
        self.top = Path(top).resolve() if top is not None else None

    def nearest(self) -> Optional[Path]:
        """The story map in this folder or the nearest folder above it, up to the top folder, or in that folder's
        ``.context``: its markdown when it has one, since a drawio of the same map would add every Story twice. A map
        outside the project is another project's, and the folders above a project can hold far more files than it."""
        for candidate in self._this_and_above():
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
        return sorted(path for path in self._markdown_below() if is_story_map_file(path))

    def story_files_below(self) -> List[Path]:
        """Each story's own markdown file in this folder and the folders below it."""
        return sorted(path for path in self._markdown_below() if path.name.endswith(STORY_FILE_SUFFIXES))

    def thin_slicing(self) -> Optional[Path]:
        """The markdown that slices the map into increments: `thin-slicing.md` (or `thin-slice.md`, `thin-slices.md`,
        `increments.md`, in that order), in this folder, else the first in the folders below it; none when there is
        none."""
        below = list(self._markdown_below())
        for name in THIN_SLICING_FILES:
            beside = self.folder / name
            if beside.is_file():
                return beside.resolve()
            found = next((path for path in below if path.name == name), None)
            if found is not None:
                return found
        return None

    def scenario_files_below(self) -> List[Path]:
        """Each markdown file scenarios are written in, in this folder and the folders below it: in a `scenarios`, `md`
        or `stories` folder, a `scenarios.md` or `story-scenarios.md`, or a story's own file. Grouped by the kind of
        file in that order, then by path, so a folder's scenarios read in the same order every time."""
        found = [(kind, path) for path in self._markdown_below() for kind in [_scenario_file_kind(PurePosixPath(path.relative_to(self.folder).as_posix()))] if kind is not None]
        return [path for _kind, path in sorted(found)]

    def _markdown_below(self) -> Iterator[Path]:
        """Every markdown file in this folder and the folders below it, entering each folder's `.context`, where
        documents are kept, and no folder a working-copy scan never enters."""
        for folder, folders, names in os.walk(self.folder):
            folders[:] = sorted(name for name in folders if name == CONTEXT_FOLDER or not skips_folder(name))
            yield from (Path(folder, name).resolve() for name in sorted(names) if name.lower().endswith(_MARKDOWN))

    def _this_and_above(self) -> List[Path]:
        folders = [self.folder, *self.folder.parents]
        if self.top is None or self.top not in folders:
            return folders
        return folders[: folders.index(self.top) + 1]

    def _maps_in(self, folder: Path) -> List[Path]:
        context = folder / CONTEXT_FOLDER
        beside = list(context.iterdir()) if context.is_dir() else []
        return sorted(path.resolve() for path in [*folder.iterdir(), *beside] if path.is_file() and is_story_map_file(path))


# The folders and file names scenarios are written in, in the order a folder's scenario files are read.
_SCENARIO_FOLDERS = ("scenarios", "md")
_SCENARIO_FILES = ("scenarios.md",)
_STORY_SCENARIO_FILES = ("story-scenarios.md",)
_STORIES_FOLDER = "stories"


def _scenario_file_kind(relative: PurePosixPath) -> Optional[int]:
    """Which kind of scenario file a path is, by the order they are read in; none for another markdown file."""
    folders = relative.parts[:-1]
    kinds = (
        any(folder in _SCENARIO_FOLDERS[:1] for folder in folders) or relative.name in _SCENARIO_FILES,
        any(folder in _SCENARIO_FOLDERS[1:] for folder in folders),
        relative.name.endswith(STORY_FILE_SUFFIXES),
        relative.name in _STORY_SCENARIO_FILES,
        _STORIES_FOLDER in folders,
    )
    return next((index for index, matches in enumerate(kinds) if matches), None)
