"""Links a story map and its story files carry.

A story map node links to its entry in ``story-map.md`` and to the story's own
markdown file. A domain term in a story file links to the heading that defines
it in the domain model markdown (``class-model.md`` or ``domain-model.md``).
A link is written only when its target file exists; otherwise the text stays plain.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

_LINK = re.compile(r"\[([^\]\n]+)\]\(([^)\s]*)\)")
_CODE_SPAN = re.compile(r"`[^`\n]+`")
_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_STEREOTYPE = re.compile(r"<<[^>]*>>")
_STORY_FILE_SUFFIXES = ("_story.test.md", "_story.spec.md")
_SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", ".pycache"}

MODEL_FILES = ("domain-model.md", "class-model.md")
_MODEL_SECTIONS = {"layout", "event map", "invariants", "interactions"}


def unlink(text: str) -> str:
    """Markdown text with every ``[label](target)`` link reduced to its label."""
    return _LINK.sub(lambda match: match.group(1), text)


def heading_anchor(heading: str) -> str:
    """The anchor GitHub and VS Code give a heading: lower case, punctuation dropped, spaces as hyphens."""
    text = unlink(heading).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", unlink(name).lower()).strip("-")


def _words(name: str) -> List[str]:
    return re.findall(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+", name)


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
        ``(E) {name}`` for an epic or sub-epic, ``(S) {actor} --> {name}`` for a story.
        Empty when there is no ``story-map.md``.
        """
        if self.map_file is None or not self.map_file.is_file():
            return {}
        target = _relative(self.map_file, self.base)
        anchors = _Anchors()
        links: Dict[int, str] = {}

        def story_entries(epic) -> None:
            for story in epic.stories:
                actor = unlink(story.actors[0]).strip() if story.actors else ""
                heading = f"(S) {actor} --> {story.name}" if actor else f"(S) --> {story.name}"
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


class DomainModelLinks:
    """Domain terms and the model heading that defines each one.

    A term is a class, aggregate, or context heading (level 2 or deeper) in ``domain-model.md``
    (DDD) or ``class-model.md`` (Clean Engineering). The anchor is the heading's own anchor,
    stereotypes included: ``#### Sim <<Aggregate Root>> <<Entity>>`` is ``#sim-aggregate-root-entity``.
    """

    def __init__(self, base: Path | str, terms: Optional[Dict[str, Tuple[Path | str, str]]] = None) -> None:
        self.base = Path(base).resolve()
        self.terms = {name: (Path(path).resolve(), anchor) for name, (path, anchor) in (terms or {}).items()}
        self._by_key: Dict[str, str] = {}
        self._pattern = self._compile()

    @classmethod
    def from_workspace(cls, root: Path | str, base: Optional[Path | str] = None) -> "DomainModelLinks":
        root = Path(root).resolve()
        terms: Dict[str, Tuple[Path, str]] = {}
        for path in _walk(root, names=MODEL_FILES):
            found = cls.headings(path.read_text(encoding="utf-8"))
            classes = [(name, anchor) for name, anchor, is_class in found if is_class]
            sections = [(name, anchor) for name, anchor, is_class in found if not is_class]
            for name, anchor in classes + sections:
                terms.setdefault(name, (path, anchor))
        return cls(base if base is not None else root, terms)

    @classmethod
    def headings(cls, text: str) -> List[Tuple[str, str, bool]]:
        """``(term, anchor, is_class)`` for each class or term heading in a model markdown file.
        A class heading carries a ``<<stereotype>>``; it wins over a section of the same name."""
        anchors = _Anchors()
        found: List[Tuple[str, str, bool]] = []
        fenced = False
        for line in text.splitlines():
            if line.lstrip().startswith("```"):
                fenced = not fenced
                continue
            match = _HEADING.match(line) if not fenced else None
            if match is None:
                continue
            raw = match.group(2)
            anchor = anchors.next(raw)
            if len(match.group(1)) < 2:
                continue
            name = _STEREOTYPE.sub("", unlink(raw)).split("|", 1)[0].split(" : ", 1)[0]
            name = name.replace("**", "").replace("`", "").strip()
            if name and name.casefold() not in _MODEL_SECTIONS:
                found.append((name, anchor, "<<" in raw))
        return found

    def _compile(self) -> Optional[re.Pattern]:
        if not self.terms:
            return None
        parts: List[str] = []
        for name in sorted(self.terms, key=len, reverse=True):
            words = _words(name) or [name]
            self._by_key.setdefault(" ".join(w.lower() for w in words), name)
            parts.append(r"\s*".join(re.escape(w) for w in words))
        return re.compile(r"\b(?:" + "|".join(parts) + r")s?\b", re.IGNORECASE)

    def target(self, term: str) -> str:
        """``path#anchor`` for *term*, or ``""`` when the model does not define it."""
        key = " ".join(w.lower() for w in _words(term))
        name = self._by_key.get(key) or self._by_key.get(key.removesuffix("s"))
        if name is None:
            return ""
        path, anchor = self.terms[name]
        if not path.is_file():
            return ""
        return f"{_relative(path, self.base)}#{anchor}"

    def link(self, text: str) -> str:
        """*text* with each domain term linked to its model heading; existing links and other code stay as written."""
        if self._pattern is None or not text:
            return text
        out: List[str] = []
        position = 0
        for match in re.finditer(f"{_LINK.pattern}|{_CODE_SPAN.pattern}", text):
            out.append(self._link_plain(text[position:match.start()]))
            out.append(self._link_code(match.group(0)))
            position = match.end()
        out.append(self._link_plain(text[position:]))
        return "".join(out)

    def _link_code(self, span: str) -> str:
        if not span.startswith("`"):
            return span
        target = self.target(span.strip("`").strip())
        return f"[{span}]({target})" if target else span

    def _link_plain(self, text: str) -> str:
        def replace(match: re.Match) -> str:
            target = self.target(match.group(0))
            return f"[{match.group(0)}]({target})" if target else match.group(0)

        return self._pattern.sub(replace, text)
