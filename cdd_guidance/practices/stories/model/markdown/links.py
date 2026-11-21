"""Links a story map and its story files carry.

A story map node links to its entry in ``story-map.md`` and to the story's own
markdown file. A link is written only when its target file exists; otherwise the text stays plain.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List

from harness.annotations.name import Name

from cdd_guidance.practices.stories.model.story_map_files import STORY_FILE_SUFFIXES, StoryMapFiles

if TYPE_CHECKING:
    from cdd_guidance.practices.stories.model.story_model import Epic, Story, StoryModel, StoryNode

_LINK = re.compile(r"\[([^\]\n]+)\]\(([^)\s]*)\)")



def unlink(text: str) -> str:
    """Markdown text with every ``[label](target)`` link reduced to its label."""
    return _LINK.sub(lambda match: match.group(1), text)


def heading_anchor(heading: str) -> str:
    """The anchor GitHub and VS Code give a heading: lower case, punctuation dropped, spaces as hyphens."""
    text = unlink(heading).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


# The prefix the draw.io editor of VS Code and Cursor gives the data it links a cell to a file with.
CODE_LINK = "hedietLinkedDataV1"


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
    """Where each node of one story map placed in a folder links: its ``story-map.md`` entry there and the story's own
    file. The links are made once, when the map is placed in the folder.

    Paths are written relative to the folder of the file being rendered.
    """

    def __init__(self, story_map: "StoryModel", root: Path | str) -> None:
        """The links of story_map placed in the folder root: the markdown story map *StoryMapFiles* finds there and
        every ``*_story.test.md`` / ``*_story.spec.md`` under root, written relative to the folder that holds that
        story map, where the rendered story map sits beside it."""
        root = Path(root).resolve()
        maps = StoryMapFiles(root).markdown_below()
        self._map_file = maps[0] if maps else None
        self._base = self._map_file.parent if self._map_file is not None else root
        self._story_files: Dict[str, Path] = {}
        for path in StoryMapFiles(root).story_files_below():
            stem = path.name
            for suffix in STORY_FILE_SUFFIXES:
                stem = stem.removesuffix(suffix)
            self._story_files.setdefault(self._slug(stem), path)
        self._entries = self._entries_of(story_map)

    def story_file(self, story: "Story") -> str:
        """Relative path to the story's own markdown file, or ``""`` when it has none."""
        path = self._story_files.get(self._slug(story.name))
        if path is None or not path.is_file():
            return ""
        return self._relative(path)

    def entry_for(self, node: "StoryNode") -> str:
        """The node's ``story-map.md#anchor`` link; empty for a node the map does not hold, or with no story map."""
        return next((entry for held, entry in self._entries if held is node), "")

    def code_link(self, link: str) -> Dict[str, str]:
        """The cell attributes the draw.io editor of VS Code and Cursor opens link with.

        That editor does not follow a cell's ``link`` to a file in the workspace; with its Code Link on, selecting a
        cell opens the file its ``hedietLinkedDataV1`` attributes name, relative to the diagram file itself, at the
        line they name. The diagram sits in that folder, so the file is ``../`` and link's path, and the line is the
        heading link's anchor names (the first line when it names none). Empty when link names no file there."""
        path, _, anchor = link.partition("#")
        target = self._base / path
        if not path or not target.is_file():
            return {}
        line = self._heading_line(target, anchor)
        return {
            f"{CODE_LINK}_path": f"../{path}",
            f"{CODE_LINK}_start_line_x-num": str(line), f"{CODE_LINK}_start_col_x-num": "0",
            f"{CODE_LINK}_end_line_x-num": str(line), f"{CODE_LINK}_end_col_x-num": "0",
        }

    def _heading_line(self, path: Path, anchor: str) -> int:
        """The zero-based line of the heading in path whose anchor is anchor; 0 when anchor is empty or no heading has
        it."""
        if not anchor:
            return 0
        anchors = _Anchors()
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
            heading = re.match(r"#+ (.+)$", line)
            if heading and anchors.next(heading.group(1)) == anchor:
                return number
        return 0

    def _slug(self, name: str) -> str:
        return Name(unlink(name)).title_slug

    def _relative(self, target: Path) -> str:
        """target as a path from the folder the links are written in; as it is when it sits on another drive."""
        try:
            return Path(os.path.relpath(target, self._base)).as_posix()
        except ValueError:  # another drive on Windows
            return target.as_posix()

    def _entries_of(self, story_map: "StoryModel") -> List[tuple]:
        """Each epic, sub-epic, and story of story_map with its ``story-map.md#anchor`` link, in map order.

        Anchors follow the outline headings the markdown story map renders:
        ``(E) {name}`` for an epic or sub-epic, ``(S) {actor} --> {name}`` for a story, its mark naming the kind
        when it is not a user story (``(S:system)``).
        Empty when there is no ``story-map.md``.
        """
        if self._map_file is None or not self._map_file.is_file():
            return []
        anchors = _Anchors()
        return [entry for epic in story_map.epics for entry in self._entries_under(epic, anchors)]

    def _entries_under(self, epic: "Epic", anchors: "_Anchors") -> List[tuple]:
        """The epic's entry, then each of its stories', then each of its sub-epics' and theirs, anchored in order."""
        target = self._relative(self._map_file)
        entries: List[tuple] = [(epic, f"{target}#{anchors.next(f'(E) {epic.name}')}")]
        for story in epic.stories:
            actor = f"{unlink(story.actors[0]).strip()} " if story.actors else ""
            heading = f"{story.story_type.outline_mark} {actor}--> {story.name}"
            entries.append((story, f"{target}#{anchors.next(heading)}"))
        for sub in epic.epics:
            entries.extend(self._entries_under(sub, anchors))
        return entries
