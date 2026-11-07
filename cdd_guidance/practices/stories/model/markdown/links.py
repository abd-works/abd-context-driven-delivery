"""Links a story map and its story files carry.

A story map node links to its entry in ``story-map.md`` and to the story's own
markdown file. A link is written only when its target file exists; otherwise the text stays plain.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from harness.annotations.name import Name

_LINK = re.compile(r"\[([^\]\n]+)\]\(([^)\s]*)\)")
_STORY_FILE_SUFFIXES = ("_story.test.md", "_story.spec.md")
_SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", ".pycache"}



def unlink(text: str) -> str:
    """Markdown text with every ``[label](target)`` link reduced to its label."""
    return _LINK.sub(lambda match: match.group(1), text)


def heading_anchor(heading: str) -> str:
    """The anchor GitHub and VS Code give a heading: lower case, punctuation dropped, spaces as hyphens."""
    text = unlink(heading).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def _slug(name: str) -> str:
    return Name(unlink(name)).title_slug


def _relative(target: Path, base: Path) -> str:
    try:
        return Path(os.path.relpath(target, base)).as_posix()
    except ValueError:  # another drive on Windows
        return target.as_posix()


def _walk(root: Path, names: Iterable[str] = (), suffixes: Iterable[str] = ()) -> List[Path]:
    names, suffixes = set(names), tuple(suffixes)
    found: List[Path] = []
    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in _SKIP_DIRS)
        for file in sorted(files):
            if file in names or (suffixes and file.endswith(suffixes)):
                found.append(Path(folder) / file)
    return found


class _Anchors:
    """Anchors in document order; a repeated heading takes ``-1``, ``-2`` like GitHub."""

    def __init__(self) -> None:
        self._seen: Dict[str, int] = {}

    def next(self, heading: str) -> str:
        anchor = heading_anchor(heading)
        count = self._seen.get(anchor)
        self._seen[anchor] = 0 if count is None else count + 1
        return anchor if count is None else f"{anchor}-{count + 1}"


class StoryMapLinks:
    """Where each story map node links: its ``story-map.md`` entry and the story's own file.

    Paths are written relative to ``base``, the folder of the file being rendered.
    """

    def __init__(
        self,
        base: Path | str,
        map_file: Optional[Path | str] = None,
        story_files: Optional[Dict[str, Path | str]] = None,
    ) -> None:
        self.base = Path(base).resolve()
        self.map_file = Path(map_file).resolve() if map_file else None
        self.story_files = {_slug(k): Path(v).resolve() for k, v in (story_files or {}).items()}

    @classmethod
    def from_workspace(cls, root: Path | str, base: Optional[Path | str] = None) -> "StoryMapLinks":
        """Find ``story-map.md`` and every ``*_story.test.md`` / ``*_story.spec.md`` under *root*.

        Paths are written relative to *base*; by default the folder that holds ``story-map.md``,
        where the rendered story map sits beside it.
        """
        root = Path(root).resolve()
        map_file = root / "story-map.md"
        if not map_file.is_file():
            found = _walk(root, names=("story-map.md",))
            map_file = found[0] if found else None
        story_files: Dict[str, Path] = {}
        for path in _walk(root, suffixes=_STORY_FILE_SUFFIXES):
            stem = path.name
            for suffix in _STORY_FILE_SUFFIXES:
                stem = stem.removesuffix(suffix)
            story_files.setdefault(_slug(stem), path)
        if base is None:
            base = map_file.parent if map_file is not None else root
        return cls(base, map_file, story_files)

    def story_file(self, story) -> str:
        """Relative path to the story's own markdown file, or ``""`` when it has none."""
        path = self.story_files.get(_slug(story.name))
        if path is None or not path.is_file():
            return ""
        return _relative(path, self.base)

    def entries(self, story_map) -> Dict[int, str]:
        """``id(node)`` to its ``story-map.md#anchor`` link, for every epic, sub-epic, and story.

        Anchors follow the outline headings the markdown story map renders:
        ``(E) {name}`` for an epic or sub-epic, ``(S) {actor} --> {name}`` for a story, its mark naming the kind
        when it is not a user story (``(S:system)``).
        Empty when there is no ``story-map.md``.
        """
        if self.map_file is None or not self.map_file.is_file():
            return {}
        target = _relative(self.map_file, self.base)
        anchors = _Anchors()
        links: Dict[int, str] = {}

        def story_entries(epic) -> None:
            for story in epic.stories:
                actor = f"{unlink(story.actors[0]).strip()} " if story.actors else ""
                heading = f"{story.story_type.outline_mark} {actor}--> {story.name}"
                links[id(story)] = f"{target}#{anchors.next(heading)}"

        def sub_epic_entries(epics) -> None:
            for sub in epics:
                links[id(sub)] = f"{target}#{anchors.next(f'(E) {sub.name}')}"
                story_entries(sub)
                sub_epic_entries(sub.epics)

        for epic in story_map.epics:
            links[id(epic)] = f"{target}#{anchors.next(f'(E) {epic.name}')}"
            story_entries(epic)
            sub_epic_entries(epic.epics)
        return links
