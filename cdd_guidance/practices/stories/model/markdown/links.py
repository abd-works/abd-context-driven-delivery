"""Links a story map and its story files carry.

A story map node links to its entry in ``story-map.md`` and to the story's own
markdown file; a story to the prototype of each screen it is shown on. A link is written only when its target file exists; otherwise the text stays plain.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from harness.annotations.name import Name
from harness.design_canvas.versions import ported_project

from cdd_guidance.practices.stories.model.story_map_files import STORY_FILE_SUFFIXES, STORY_TEST_SUFFIXES, StoryMapFiles, story_line

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from cdd_guidance.practices.stories.model.story_map import Epic, Story, StoryMap, StoryNode

_LINK = re.compile(r"\[([^\]\n]+)\]\(([^)\s]*)\)")



def unlink(text: str) -> str:
    """Markdown text with every ``[label](target)`` link reduced to its label."""
    return _LINK.sub(lambda match: match.group(1), text)


class DomainTermLinks:
    """The link each domain term has in a story's notes, ``++[Cart](domain-model.md#cart-entity)++``, so a step that
    names the term underlined, ``++Cart++``, is written with the same link. A step read from code names its terms
    without links, which the notes of its story keep."""

    _LINKED = re.compile(r"\+\+\[([^\]\n]+)\]\(([^)\n]*)\)\+\+")
    _UNDERLINED = re.compile(r"\+\+([^\[\]+\n]+?)\+\+")

    def __init__(self, notes: str) -> None:
        self._targets = {label.strip(): target for label, target in self._LINKED.findall(notes)}

    def linked(self, line: str) -> str:
        """line with each underlined term the notes link written as that link; every other term as it is."""
        return self._UNDERLINED.sub(self._link_of, line)

    def targets(self) -> Dict[str, str]:
        """Each term the notes link, with the target its link names, as written (``domain-model.md#cart-entity``)."""
        return dict(self._targets)

    def _link_of(self, match: re.Match) -> str:
        target = self._targets.get(match.group(1).strip())
        return f"++[{match.group(1)}]({target})++" if target else match.group(0)


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

    def __init__(self, story_map: "StoryMap", root: Path | str) -> None:
        """The links of story_map placed in the folder root: the markdown story map *StoryMapFiles* finds there and
        every ``*_story.test.md`` / ``*_story.spec.md`` under root, written relative to the folder that holds that
        story map, where the rendered story map sits beside it."""
        root = Path(root).resolve()
        maps = StoryMapFiles(root).markdown_below()
        self._map_file = maps[0] if maps else None
        self._base = self._map_file.parent if self._map_file is not None else root
        files = StoryMapFiles(root)
        self._story_files = self._by_story(files.story_files_below(), STORY_FILE_SUFFIXES)
        self._story_tests = self._by_story(files.story_tests_below(), STORY_TEST_SUFFIXES)
        self._holders = [*files.story_files_below(), *files.story_tests_below(), *files.shared_stories_below()]
        self._texts: Dict[Path, str] = {}
        self._entries = self._entries_of(story_map)

    def story_file(self, story: "Story") -> str:
        """Relative path to the story's own scenario file, else to its acceptance test, else to the file that holds it
        among others, at its heading when that file is markdown; ``""`` when it has none."""
        path = self.story_path(story)
        if path is None:
            return ""
        anchor = self._heading_anchor(path, story.name) if self._holds_among_others(path, story) else ""
        return self.relative(path) + (f"#{anchor}" if anchor else "")

    def story_path(self, story: "Story") -> Optional[Path]:
        """The story's own scenario file, else its acceptance test, else the first story file that names it among
        others (a sub-epic's markdown, a story test or a shared story file in code); none when no file writes it."""
        slug = self._slug(story.name)
        path = self._story_files.get(slug) or self._story_tests.get(slug)
        if path is None:
            path = next((holder for holder in self._holders if story_line(self._text_of(holder), story.name)), None)
        return path if path is not None and path.is_file() else None

    def _holds_among_others(self, path: Path, story: "Story") -> bool:
        slug = self._slug(story.name)
        return path not in (self._story_files.get(slug), self._story_tests.get(slug))

    def _text_of(self, path: Path) -> str:
        if path not in self._texts:
            self._texts[path] = path.read_text(encoding="utf-8")
        return self._texts[path]

    def _heading_anchor(self, path: Path, name: str) -> str:
        """The anchor of the markdown heading in path that names the story called name; empty when path is no markdown
        or names it in no heading."""
        if path.suffix.lower() != ".md":
            return ""
        line = story_line(self._text_of(path), name)
        anchors = _Anchors()
        for number, text in enumerate(self._text_of(path).splitlines(), 1):
            heading = re.match(r"#+ (.+)$", text)
            anchor = anchors.next(heading.group(1)) if heading else ""
            if number == line:
                return anchor
        return ""

    def screen_files(self, story: "Story") -> List[Tuple[str, Path]]:
        """Each screen the story is shown on whose prototype is a file in the folder the graph reads, with that file:
        the prototype's path in the project of the design canvas its UX map is ported to (``ported_project``). A
        screen whose prototype is no file there, or a file outside that folder, is left out."""
        found: List[Tuple[str, Path]] = []
        for screen in story.screens:
            path = self._prototype_file(screen)
            if path is not None:
                found.append((screen.name, path))
        return found

    def _prototype_file(self, screen: "Node") -> Optional[Path]:
        """The file screen's prototype is kept in; none when its UX map leads to no canvas, or the file is not there or
        not inside the folder the graph reads."""
        prototype = str(getattr(screen, "prototype", "") or screen.get_fact("prototype") or "")
        source = screen.source
        if not prototype or source is None or not source.root or not source.file:
            return None
        top = Path(source.root).resolve()
        project = ported_project(top / source.file, top)
        path = (project / prototype).resolve() if project is not None else None
        return path if path is not None and path.is_file() and top in path.parents else None

    def _by_story(self, paths: List[Path], suffixes: tuple) -> Dict[str, Path]:
        """Each of paths by the slug of the story its name, without suffixes, names; the first of each story's."""
        found: Dict[str, Path] = {}
        for path in paths:
            stem = path.name
            for suffix in suffixes:
                stem = stem.removesuffix(suffix)
            found.setdefault(self._slug(stem), path)
        return found

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

    def relative(self, target: Path) -> str:
        """target as a path from the folder the links are written in; as it is when it sits on another drive."""
        try:
            return Path(os.path.relpath(target, self._base)).as_posix()
        except ValueError:  # another drive on Windows
            return target.as_posix()

    def _entries_of(self, story_map: "StoryMap") -> List[tuple]:
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
        target = self.relative(self._map_file)
        entries: List[tuple] = [(epic, f"{target}#{anchors.next(f'(E) {epic.name}')}")]
        for story in epic.stories:
            actor = f"{unlink(story.actors[0]).strip()} " if story.actors else ""
            heading = f"{story.story_type.outline_mark} {actor}--> {story.name}"
            entries.append((story, f"{target}#{anchors.next(heading)}"))
        for sub in epic.epics:
            entries.extend(self._entries_under(sub, anchors))
        return entries
