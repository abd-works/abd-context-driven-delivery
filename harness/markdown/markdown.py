"""Co-located markdown extract and HTML conversion — not assembly."""
from __future__ import annotations

import copy
import functools
import threading
import html
import inspect
import os
import re
import stat
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, ClassVar, Generic, Iterator, Literal, TypeAlias, TypeVar, get_args, get_origin, get_type_hints

from harness.annotations.class_folder import class_folder
from harness.annotations.name import Name
from harness.annotations.annotation import annotation_kinds, hosted_only
from harness.markdown.format import TEMPLATE_FOLDER_NAMES, Format
from harness.markdown.front_matter import FlatSettings

# The seam other modules import from the package: a class's markdown read typed, the scope an owner hands it, and the
# annotations that make a property read it. The classes that locate and read one file stay behind *Markdown*.
__all__ = [
    "FileFilter",
    "HTML",
    "Markdown",
    "MarkdownCollection",
    "MarkdownScope",
    "MarkdownText",
    "MarkdownTypeUnresolved",
    "SOURCE_STAMPS",
    "markdown",
    "markdown_collection",
]

_F = TypeVar("_F", bound=Callable[..., Any])
# The class whose objects a markdown section belongs to, such as a practice, a fidelity, or an action: its folder holds
# the markdown, and it may hand over the scope it reads it in (``markdown_scope``). Any class can own markdown, so the
# markdown parts are generic in their owner's class.
Owner = TypeVar("Owner")
# What one entry of a markdown collection is: a fidelity of a practice's fidelities, a rule of its rules.
Entry = TypeVar("Entry")
# What a markdown property's operation says it returns: a class, a generic such as ``list[Rule]``, or nothing written.
ReturnAnnotation: TypeAlias = Any


class ExtractedMarkdown(str):
    """Extracted markdown that still answers ``expand()`` and ``templates()``."""

    def expand(self) -> "ExtractedMarkdown":
        return self

    def __call__(self) -> "ExtractedMarkdown":
        return self


# A marker in an owner's markdown for a value its code holds: ``{{child_band.sub_epic}}``.
_MARKER = re.compile(r"\{\{([\w.]+)\}\}")
# A markdown bullet: a dash or star after any indent.
_BULLET = re.compile(r"^\s*[-*]\s+")


class HTML:
    def __init__(self, text: str) -> None:
        self.text = text

    @classmethod
    def from_markdown(cls, text: str) -> HTML:
        """The HTML of text without its headings: a bulleted block becomes a list, any other block a paragraph."""
        body = re.sub(r"^#{1,6}\s+.*$", "", text, flags=re.MULTILINE).strip()
        if not body:
            return cls("")
        chunks: list[str] = []
        for block in (block.strip() for block in re.split(r"\n\s*\n", body)):
            lines = block.splitlines()
            if not block:
                continue
            if all(_BULLET.match(line) for line in lines):
                chunks.append("<ul>" + "".join(f"<li>{html.escape(_BULLET.sub('', line))}</li>" for line in lines) + "</ul>")
            else:
                chunks.append(f"<p>{html.escape(block)}</p>")
        return cls("\n".join(chunks))

    def __str__(self) -> str:
        return self.text

    def __contains__(self, fragment: str) -> bool:
        return str(fragment) in self.text

    def __eq__(self, other: HTML | str) -> bool:
        if isinstance(other, HTML):
            return self.text == other.text
        return self.text == other


LocationKind = Literal["file", "folder", "section"]
# An owner's filter of the files of a folder it reads: given the label read and a file's path, whether it reads the file.
FileFilter: TypeAlias = Callable[[str, Path], bool]


# A markdown link, whose words are all of it a reader sees.
_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def link_words(text: str) -> str:
    """text as a reader sees it: each markdown link's words in place of the link (``has [Cart](model.md#cart) cart``
    reads ``has Cart cart``)."""
    return _LINK.sub(r"\1", text)


def heading_anchor(heading: str) -> str:
    """The anchor a link names a heading by, as GitHub writes it from the words the heading shows: lower case, its
    punctuation dropped, each space a hyphen (``Story: Delete Ticket`` is ``story-delete-ticket``,
    ``FilesPage (`files/files-page.ts`)`` is ``filespage-filesfiles-pagets``). A link the heading holds counts as its
    words alone (``(S) Person --> [Delete Ticket](x.md)`` is ``s-person----delete-ticket``)."""
    shown = link_words(heading)
    return re.sub(r"[^\w\- ]", "", shown.strip().lower()).replace(" ", "-")


def _section_heading(label: str) -> str:
    if label.casefold() in {"context", "contexts", "overview"}:
        return "Overview"
    return label.replace("_", " ").replace("-", " ").title()


# The first marks a heading (#) or a code fence (``` or ~~~) can open with.
_MARK_CHARACTERS = ("#", "`", "~")


class MarkdownText:
    """A markdown document: headings, slices, and child sections."""

    def __init__(self, text: str) -> None:
        self._text = text
        # Its headings, found once: the text never changes, and every section read of it asks for them.
        self._found_headings: list[tuple[int, int, int, str]] | None = None

    @property
    def text(self) -> str:
        """The whole document as written."""
        return self._text

    @property
    def yaml_fields(self) -> dict[str, Any]:
        """The fields of every ```yaml block in the document, merged in order, so a section keeps its settings beside
        its prose."""
        return YamlFields().yaml_fields(self._text)

    @property
    def without_yaml(self) -> str:
        """The document with its ```yaml blocks taken out: the prose an agent reads and an installed file holds."""
        return _YAML_FENCE.sub("", self._text).strip()

    def _fence_update(self, fence: str | None, bare: str) -> tuple[str | None, bool]:
        fence_match = re.match(r"^\s*(```|~~~)", bare)
        if not fence_match:
            return fence, False
        marker = fence_match.group(1)
        if fence is None:
            return marker, True
        if fence == marker:
            return None, True
        return fence, True

    def _heading_at(self, bare: str, offset: int) -> tuple[int, int, int, str] | None:
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", bare)
        if heading is None:
            return None
        return (offset, offset + len(bare), len(heading.group(1)), heading.group(2))

    def headings(self) -> list[tuple[int, int, int, str]]:
        if self._found_headings is None:
            self._found_headings = self._scanned_headings()
        return list(self._found_headings)

    def _scanned_headings(self) -> list[tuple[int, int, int, str]]:
        # The position and the open code fence belong to the scan, not the document: a parsed document is shared, and two
        # threads can scan it at once.
        headings: list[tuple[int, int, int, str]] = []
        offset = 0
        fence: str | None = None
        for line in self._text.splitlines(keepends=True):
            # Only a line opening with a heading's or a fence's mark can be either, so most lines are passed over unmatched.
            if line.lstrip()[:1] not in _MARK_CHARACTERS:
                offset += len(line)
                continue
            bare = line.rstrip("\r\n")
            fence, consumed = self._fence_update(fence, bare)
            if not consumed and fence is None:
                recorded = self._heading_at(bare, offset)
                if recorded is not None:
                    headings.append(recorded)
            offset += len(line)
        return headings

    def slice_heading(self, heading: str) -> str:
        if not heading:
            return self._text
        headings = self.headings()
        found = next(
            (
                (index, item)
                for index, item in enumerate(headings)
                if item[3].casefold() == heading.casefold()
            ),
            None,
        )
        if found is None:
            return ""
        index, (start, _heading_end, level, _heading) = found
        end = next(
            (position for position, _e, next_level, _h in headings[index + 1 :] if next_level <= level),
            len(self._text),
        )
        return self._text[start:end].strip()

    def anchored_lines(self, anchor: str) -> tuple[int, int] | None:
        """The lines, counted from 1, of the section under the heading a link names by anchor, such as
        ``story-delete-ticket`` for ``## Story: Delete Ticket``: its heading through its last line with text before the
        next heading as high or higher; none when no heading has that anchor."""
        found = next((index for index, item in enumerate(self.headings()) if heading_anchor(item[3]) == anchor), None)
        return self._section_lines(found) if found is not None else None

    def section_lines(self, line: int) -> tuple[int, int] | None:
        """The lines, counted from 1, of the section whose heading sits on line: its heading through its last line with
        text before the next heading as high or higher; none when no heading sits on line."""
        found = next((index for index, item in enumerate(self.headings()) if self._text.count("\n", 0, item[0]) + 1 == line), None)
        return self._section_lines(found) if found is not None else None

    def _section_lines(self, found: int) -> tuple[int, int]:
        headings = self.headings()
        start, _heading_end, level, _heading = headings[found]
        end = next((position for position, _e, next_level, _h in headings[found + 1 :] if next_level <= level), len(self._text))
        first = self._text.count("\n", 0, start) + 1
        return first, first + self._text[start:end].rstrip().count("\n")

    def _child_blocks(self, parent_heading: str) -> list[tuple[str, str]]:
        wanted = parent_heading.casefold()
        parent = next((index for index, item in enumerate(self.headings()) if item[3].casefold() == wanted), None)
        if parent is None:
            return []
        return [(self.headings()[index][3], self._body_of(index)) for index in self._children_of(parent)]

    def _children_of(self, parent_index: int) -> list[int]:
        """The index of each heading one level below the heading at parent_index. The parent is this question's own:
        a parsed document is shared between threads, so nothing of one reader's question is kept on it."""
        headings = self.headings()
        level = headings[parent_index][2]
        children: list[int] = []
        for child_index in range(parent_index + 1, len(headings)):
            next_level = headings[child_index][2]
            if next_level <= level:
                break
            if next_level == level + 1:
                children.append(child_index)
        return children

    def _body_of(self, index: int) -> str:
        """The body under the heading at index: it ends at the next heading as high as it, else at the end of the text."""
        headings = self.headings()
        _start, heading_end, level, _name = headings[index]
        end = next((later[0] for later in headings[index + 1 :] if later[2] <= level), len(self._text))
        return self._text[heading_end:end].lstrip("\r\n").strip()

    def section_child_blocks(self) -> list[tuple[str, str]]:
        headings = self.headings()
        if not headings:
            return []
        return self._child_blocks(headings[0][3])

    def block_under(self, *headings: str) -> str:
        """The body under the last of headings, each a heading one level below the one before it, such as
        ``("Fidelities", "story_map")`` for a ``### story_map`` block under ``## Fidelities``; the first may sit at any
        level. Headings match in any case. Empty when the document has no such block."""
        first, *rest = headings
        found = next((index for index, item in enumerate(self.headings()) if item[3].casefold() == first.casefold()), None)
        for wanted in rest:
            if found is None:
                return ""
            found = next((index for index in self._children_of(found) if self.headings()[index][3].casefold() == wanted.casefold()), None)
        return self._body_of(found) if found is not None else ""


class SourceStamps:
    """When each file or folder of the guidance a process ships was last written, and its size: what tells a cache of
    that guidance it was edited. The guidance's own packages register their folders; a path under one is looked at again
    at most once every ``STEADY_SECONDS``, so an edit is seen within a second. Every session, board read and spec builds
    the practices again and asks for the same few hundred files and folders, and asking the file system each time was
    most of what a board read and a spec cost. Any other path, such as a session's own files, is looked at every time."""

    STEADY_SECONDS = 1.0

    def __init__(self) -> None:
        self._roots: tuple[str, ...] = ()
        self._seen: dict[str, tuple[float, tuple[int, int, bool] | None]] = {}
        self._lock = threading.Lock()

    def hold_steady(self, *folders: Path | str) -> None:
        """Look at what is under folders at most once every STEADY_SECONDS: the folders of guidance this process ships."""
        added = tuple(os.path.normcase(os.path.abspath(str(folder))) + os.sep for folder in folders)
        with self._lock:
            self._roots = tuple(dict.fromkeys(self._roots + added))

    def of(self, path: Path) -> tuple[int, int, bool] | None:
        """path's last-written time, its size, and whether it is a file; none when nothing is there."""
        key = os.path.normcase(os.path.abspath(path))
        steady = key.startswith(self._roots) if self._roots else False
        now = time.monotonic()
        if steady:
            seen = self._seen.get(key)
            if seen is not None and now - seen[0] < self.STEADY_SECONDS:
                return seen[1]
        try:
            status = os.stat(key)
            stamp: tuple[int, int, bool] | None = (status.st_mtime_ns, status.st_size, stat.S_ISREG(status.st_mode))
        except (FileNotFoundError, NotADirectoryError):
            stamp = None
        if steady:
            self._seen[key] = (now, stamp)
        return stamp


SOURCE_STAMPS = SourceStamps()


class ReadDocuments:
    """Every markdown file this process has read, parsed once and shared: a practice's document is read for each of its
    sections, and again by every session that makes the practice. A file is read again once its last-written time or
    size changes, so an edit is seen."""

    def __init__(self) -> None:
        self._held: dict[Path, tuple[tuple[int, int], MarkdownText]] = {}
        self._lock = threading.Lock()

    def of(self, path: Path) -> MarkdownText | None:
        """The parsed document at path; none when there is no file there."""
        stamp = SOURCE_STAMPS.of(path)
        if stamp is None or not stamp[2]:
            return None
        version = stamp[:2]
        with self._lock:
            held = self._held.get(path)
            if held is not None and held[0] == version:
                return held[1]
        document = MarkdownText(path.read_text(encoding="utf-8"))
        with self._lock:
            self._held[path] = (version, document)
        return document


READ_DOCUMENTS = ReadDocuments()


class MarkdownFile:
    """A markdown file on disk, optionally scoped to one heading."""

    def __init__(self, path: Path, heading: str = "") -> None:
        self._path = path
        self._heading = heading

    def _load(self) -> MarkdownText | None:
        return READ_DOCUMENTS.of(self._path)

    def section_exists(self) -> bool:
        if not self._heading:
            return True
        document = self._load()
        if document is None:
            return True
        wanted = self._heading.casefold()
        return any(heading.casefold() == wanted for _s, _e, _l, heading in document.headings())

    def read_section(self) -> str:
        document = self._load()
        if document is None:
            return ""
        if not self._heading:
            return document.text
        return document.slice_heading(_section_heading(self._heading))

    def read_within(self, within: tuple[str, ...]) -> str:
        """Its heading's section inside the block the headings within lead to, such as a fidelity's own Guidance in its
        ``### {fidelity}`` block; empty when the file has no such block."""
        document = self._load()
        if document is None:
            return ""
        block = document.block_under(*within)
        if not block:
            return ""
        titled = _section_heading(self._heading) if self._heading else ""
        return MarkdownText(block).slice_heading(titled)


@dataclass(frozen=True)
class AssetLocation:
    kind: LocationKind
    path: Path | None = None
    folder: Path | None = None
    section_file: Path | None = None
    section_heading: str | None = None
    label: str | None = None
    within: tuple[str, ...] = ()
    reads_file: FileFilter | None = None
    format: str | None = None

    def extract(self) -> str:
        if self.kind == "file":
            return self._extract_file()
        if self.kind == "folder":
            return self._extract_folder()
        if self.kind == "section":
            return self._extract_section()
        return ""

    def _extract_file(self) -> str:
        if self.path is None or not self.path.is_file():
            return ""
        return self.path.read_text(encoding="utf-8")

    def _extract_folder(self) -> str:
        if self.folder is None:
            return ""
        return self._merge_folder(self.folder)

    def _merge_folder(self, folder_path: Path) -> str:
        if not folder_path.is_dir():
            return ""
        parts: list[str] = []
        for path in sorted(folder_path.iterdir()):
            nested = self._folder_entry_text(path)
            if nested:
                parts.append(nested)
        return "\n\n".join(parts)

    def _folder_entry_text(self, path: Path) -> str:
        if self._skip_folder_entry(path):
            return ""
        if path.is_file():
            rel = path.relative_to(self.folder).as_posix() if self.folder else path.name
            return f"## {rel}\n\n{path.read_text(encoding='utf-8')}"
        if path.is_dir():
            return self._merge_folder(path)
        return ""

    def _skip_folder_entry(self, path: Path) -> bool:
        name = path.name
        if name.startswith(".") or name in {"__pycache__", "evals"}:
            return True
        if "faultyasset" in name.casefold():
            return True
        if path.is_dir():
            return self._skip_format_dir(name)
        return self._skip_format_file(path) or not self._read_by_owner(path)

    def _skip_format_dir(self, name: str) -> bool:
        wanted = self._format_dir_name()
        if not wanted:
            return False
        return name.casefold() in TEMPLATE_FOLDER_NAMES and name.casefold() != wanted

    def _format_dir_name(self) -> str:
        return Format(self.format).template_folder

    def _skip_format_file(self, path: Path) -> bool:
        allowed = Format(self.format).template_extension
        if not allowed:
            return False
        return path.suffix.lower() != allowed

    def _read_by_owner(self, path: Path) -> bool:
        """Whether the owner reads path of the folder for this label: every file, unless the owner filters them."""
        return self.reads_file is None or self.reads_file(self.label or "", path)

    def _extract_section(self) -> str:
        if self.section_file is None:
            return ""
        markdown_file = MarkdownFile(self.section_file, self.section_heading or "")
        if self.within:
            return markdown_file.read_within(self.within)
        if self.section_heading and not markdown_file.section_exists():
            return ""
        return markdown_file.read_section()


@dataclass(frozen=True)
class MarkdownScope:
    """Where an owner keeps its markdown and which part of it the owner reads: the folder beside its class, the slug
    its ``{slug}.md`` is named by, the format whose templates it reads, the name its own template is looked for by
    before the slug's (``template_name``), the headings its own sections are read under (``within``, such as
    ``("Fidelities", "story_map")`` for a section of one block of a longer document), and the owner's own filter of the
    files of a folder it reads (``reads_file``), and the values its code holds that its markdown names by a marker
    (``values``). An owner that knows these hands them over as its ``markdown_scope``
    property, so nothing here asks the owner for its attributes; any other class reads the markdown beside its own
    file, under the ``domain_slug`` its class declares."""

    folder: Path
    slug: str
    format: str | None = None
    template_name: str | None = None
    within: tuple[str, ...] = ()
    reads_file: FileFilter | None = None
    # The values the owner's code holds and its markdown names by a marker, such as ``{{child_band.sub_epic}}``: each
    # name with what is written in its place, so a number a check holds is typed in the code alone.
    values: tuple[tuple[str, str], ...] = ()

    def filled(self, text: str) -> str:
        """text with each marker ``{{name}}`` the owner holds a value for written as that value. Any other marker stays
        as it is: an instruction's own ``{{argument}}`` is filled later, from the call."""
        held = dict(self.values)
        return _MARKER.sub(lambda marker: held.get(marker.group(1), marker.group(0)), text) if held else text

    @classmethod
    def _beside(cls, owner_class: type) -> MarkdownScope:
        """The markdown beside owner_class's file, named by the slug the class declares, else by its folder."""
        folder = class_folder(owner_class)
        declared = getattr(owner_class, "domain_slug", None)
        return cls(folder, declared if isinstance(declared, str) and declared else folder.name)

    @classmethod
    def of(cls, owner: Owner) -> MarkdownScope:
        """The scope owner hands its markdown; the markdown beside its class when it hands none."""
        handed = getattr(type(owner), "markdown_scope", None)
        if isinstance(handed, property):
            return handed.fget(owner)
        return cls._beside(type(owner))

    def at(self, format: str | None) -> MarkdownScope:
        """This scope in another format when one is named, so a caller reads that format's template without changing
        the format other callers read the owner in."""
        return replace(self, format=format if format is not None else self.format)


class AssetLocator:
    """Finds where one label of an owner's markdown lives, from the scope the owner handed over.

    Every session and graph a process makes reads its practices' markdown again, so a location found once is kept
    with the modification times of the folders searched for it, and searched for again only when one of them changes."""

    _found: ClassVar[dict[tuple[MarkdownScope, str], tuple[tuple[int | None, ...], AssetLocation]]] = {}

    def __init__(self, scope: MarkdownScope, label: str) -> None:
        self._scope = scope
        self._label = label
        self._module_dir = scope.folder
        self._domain_slug = scope.slug
        self._search_root_path = scope.folder

    @property
    def format(self) -> str | None:
        return self._scope.format or None

    def _stamp(self, location: AssetLocation) -> AssetLocation:
        return replace(
            location,
            label=self._label,
            reads_file=self._scope.reads_file if location.kind == "folder" else None,
            format=location.format or self.format,
        )

    def locate(self) -> AssetLocation:
        key = (self._scope, self._label)
        searched = self._searched_folders_changed_at()
        held = self._found.get(key)
        if held is not None and held[0] == searched:
            return held[1]
        location = self._stamp(self._locate())
        self._found[key] = (searched, location)
        return location

    def _searched_folders_changed_at(self) -> tuple[int | None, ...]:
        """When each folder a search looks in last had an entry added, removed, or renamed; none for one not there."""
        changed_at: list[int | None] = []
        for folder in (self._module_dir, *self._template_folders()):
            stamp = SOURCE_STAMPS.of(folder)
            changed_at.append(stamp[0] if stamp is not None else None)
        return tuple(changed_at)

    def _locate(self) -> AssetLocation:
        if self._label == "templates":
            return self._locate_template_or_missing()
        return self._locate_under()

    def _locate_template_or_missing(self) -> AssetLocation:
        located = self._locate_templates()
        if located.path is not None and located.path.is_file():
            return located
        return AssetLocation(
            "file",
            path=(self._module_dir / ".no-template").resolve(),
        )

    def _locate_under(self) -> AssetLocation:
        if self._scope.within:
            return self._section_of_domain_markdown(within=self._scope.within)
        return self._located_beside() or self._section_of_domain_markdown()

    def _located_beside(self) -> AssetLocation | None:
        """The label's own folder or file beside the owner; none when the label lives only as a section."""
        folder = self._search_root_path / ("_examples" if self._label == "examples" else self._label)
        if folder.is_dir():
            return AssetLocation("folder", folder=folder.resolve())
        for name in (self._label, f"{self._label}.md"):
            candidate = self._search_root_path / name
            if candidate.is_file():
                return AssetLocation("file", path=candidate.resolve())
        first = self._first_extension_match(self._search_root_path)
        return AssetLocation("file", path=first.resolve()) if first else None

    def _section_of_domain_markdown(self, within: tuple[str, ...] = ()) -> AssetLocation:
        return AssetLocation(
            "section",
            section_file=self._canonical_domain_md().resolve(),
            section_heading=_section_heading(self._label),
            within=within,
        )

    def _first_extension_match(self, search_root: Path) -> Path | None:
        if not search_root.is_dir():
            return None
        matches = sorted(c for c in search_root.glob(f"{self._label}.*") if c.is_file())
        return matches[0] if matches else None

    def _canonical_domain_md(self) -> Path:
        for root in (self._module_dir, self._search_root_path):
            found = self._domain_md_in(root)
            if found is not None:
                return found
        return self._module_dir / f"{self._domain_slug}.md"

    def _domain_md_in(self, root: Path) -> Path | None:
        for slug in Name(self._domain_slug).spellings:
            candidate = root / f"{slug}.md"
            if candidate.is_file():
                return candidate
        return None

    def _locate_templates(self) -> AssetLocation:
        named = self._scope.template_name
        if named:
            located = self._named_template_file(named, practice=False)
            if located is not None:
                return located
        located = self._named_template_file(self._domain_slug, practice=True)
        if located is not None:
            return located
        return AssetLocation(
            "file",
            path=(self._module_dir / ".no-template").resolve(),
        )

    def _named_template_file(self, name: str, *, practice: bool) -> AssetLocation | None:
        stems = list(Name(name).spellings)
        if practice:
            stems = [
                extra
                for slug in Name(name).spellings
                for extra in (slug, f"{slug}-templates", f"{slug}-template")
            ]
        extension = Format(self.format).template_extension
        for folder in self._template_folders():
            located = self._template_in_folder(folder, stems, extension)
            if located is not None:
                return located
        return None

    def _template_folders(self) -> list[Path]:
        folders: list[Path] = []
        shared = self._module_dir / "templates"
        if self.format:
            folders.append(shared / Format(self.format).short)
            folders.append(self._module_dir / "formats" / self.format)
        folders.append(shared)
        return folders

    def _template_in_folder(self, folder: Path, stems: list[str], extension: str) -> AssetLocation | None:
        """The first template named by one of stems in folder, with extension when the format has one."""
        if not folder.is_dir():
            return None
        for stem in stems:
            candidates = [folder / f"{stem}{extension}"] if extension else sorted(folder.glob(f"{stem}.*"))
            path = next((path for path in candidates if path.is_file() and "sketch" not in path.stem.casefold()), None)
            if path is not None:
                return AssetLocation("file", path=path.resolve())
        return None


_YAML_FENCE = re.compile(r"```ya?ml\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


class YamlFields:
    """The fields of the ```yaml blocks in a markdown text, merged in order. The owner of the text applies them.

    A practice's markdown is read again for every session and graph a process makes, and parsing its YAML is the slow
    part, so each body is parsed once per process; every caller gets its own copy of the fields to change."""

    _parsed: ClassVar[dict[str, dict[str, Any]]] = {}

    def mapping(self, body: str) -> dict[str, Any]:
        if body not in self._parsed:
            self._parsed[body] = self._parse(body)
        return copy.deepcopy(self._parsed[body])

    def _parse(self, body: str) -> dict[str, Any]:
        try:
            import yaml
        except ImportError:
            yaml = None
        if yaml is not None:
            loaded = yaml.safe_load(body)
            if isinstance(loaded, dict):
                return loaded
        return FlatSettings(body).fields

    def yaml_fields(self, text: str) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        for match in _YAML_FENCE.finditer(text):
            merged.update(self.mapping(match.group(1)))
        return merged


@hosted_only
class MarkdownCollection(Generic[Owner, Entry]):
    """Listed or keyed extracts that keep the original markdown, each an entry of the kind a subclass names
    (``MarkdownCollection[Guidance, FidelityGuidance]``)."""

    def __init__(
        self,
        entries: dict[str, Entry] | list[Entry] | None = None,
        parent: Owner | None = None,
    ) -> None:
        self.parent = parent
        self._markdown = ""
        self._adopt(entries if entries is not None else {})

    def _adopt(self, entries: dict[str, Entry] | list[Entry]) -> None:
        """Hold entries, each with this collection as its parent."""
        self.entries: dict[str, Entry] | list[Entry] = entries
        for child in self:
            child.parent = self

    @property
    def markdown(self) -> str:
        return self._markdown

    @markdown.setter
    def markdown(self, text: str) -> None:
        self._markdown = text

    def __iter__(self) -> Iterator[Entry]:
        values = self.entries.values() if isinstance(self.entries, dict) else self.entries
        return iter(values)

    def __getitem__(self, name: str) -> Entry:
        return self.entries[name]

    def child(self, name: str, body: str = "") -> Entry | None:
        """The entry a ``### name`` block of this collection's markdown declares; none for a collection whose blocks
        make no entries."""
        return None

    @classmethod
    def from_markdown(cls, text: str, parent: Owner | None = None) -> MarkdownCollection:
        collection = cls(parent=parent)
        made = ((name, collection.child(name, body)) for name, body in MarkdownText(text).section_child_blocks())
        collection._adopt({name: entry for name, entry in made if entry is not None})
        collection.markdown = text
        return collection

    @classmethod
    def from_section(cls, markdown: Markdown, return_type: ReturnAnnotation, parent: Owner | None = None) -> Any:
        """The collection a property's section holds, as return_type reads it: a list type as this collection's
        entries, a type with its own ``from_markdown`` through that, keeping the section's text."""
        text = markdown.document.text
        if (get_origin(return_type) or return_type) is list:
            return cls.from_markdown(markdown.extract())
        builder = getattr(return_type, "from_markdown", None)
        if not callable(builder) or return_type is cls:
            return cls.from_markdown(text, parent=parent)
        result = markdown.built_by(builder, text, parent)
        if result is not None:
            result.markdown = text
        return result

    def attach(self, instance: Owner, name: str | None = None) -> None:
        self.parent = instance
        previous = vars(instance).get(name) if name else None
        if name is not None:
            vars(instance)[name] = self
        for attr, value in list(vars(instance).items()):
            if value is self:
                continue
            if (previous is not None and value is previous) or (name is None and type(value) is type(self)):
                vars(instance)[attr] = self



class MarkdownTypeUnresolved(TypeError):
    """A markdown property's annotations name a type its module cannot resolve, so the property cannot tell what to
    turn its section's text into. Reading the annotation as a bare string would coerce the text into the wrong shape."""

    def __init__(self, operation: Callable[..., Any], cause: BaseException) -> None:
        self.property_name = operation.__qualname__
        self.annotations = dict(getattr(operation, "__annotations__", {}) or {})
        super().__init__(f"{self.property_name}: annotations {self.annotations!r} do not resolve: {cause}")


class Markdown(Generic[Owner]):
    """One labelled section of an owner's markdown, located from the scope the owner hands over and read once."""

    def __init__(self, instance: Owner, label: str, scope: MarkdownScope) -> None:
        self._instance = instance
        self._label = label
        self._scope = scope

    _HELD_AS = "_held_markdown"

    @classmethod
    def from_label(cls, instance: Owner, label: str, scope: MarkdownScope | None = None) -> Markdown:
        """Markdown for ``label`` on ``instance``, in scope when given (``MarkdownScope.of(instance).at(format)`` reads
        another format's template), else in the scope instance reads in now."""
        return cls(instance, label, scope if scope is not None else MarkdownScope.of(instance))

    @classmethod
    def held_by(cls, owner: Owner, label: str) -> Markdown:
        """The Markdown of label on owner at the scope owner reads it in now, made the first time and kept on owner, so
        a second read answers from the text the first found. A scope owner moves to, such as another part of its
        document or another format, has a Markdown of its own, made when it is first read."""
        scope = MarkdownScope.of(owner)
        held: dict[tuple[str, MarkdownScope], Markdown] = vars(owner).setdefault(cls._HELD_AS, {})
        key = (label, scope)
        if key not in held:
            held[key] = cls(owner, label, scope)
        return held[key]

    @functools.cached_property
    def location(self) -> AssetLocation:
        """Where this section lives, located once: it depends only on the label and scope this Markdown was made
        with."""
        return AssetLocator(self._scope, self._label).locate()

    @functools.cached_property
    def document(self) -> MarkdownText:
        """The section, read once from its location."""
        return MarkdownText(self._scope.filled(self.location.extract()))

    def extract(self) -> str:
        """The section's prose, without its ```yaml settings, which belong to the owner that reads them."""
        return self.document.without_yaml

    def expand_docstring(self, docstring: str | None) -> str:
        """Plain docstring text, or the markdown section when the docstring is one word."""
        text = (docstring or "").strip()
        if not text or len(text.split()) != 1:
            return text
        extracted = type(self).from_label(self._instance, text).extract().strip()
        return extracted or text

    def html(self) -> HTML:
        return HTML.from_markdown(self.extract())

    def _coerce(self, text: str, return_type: ReturnAnnotation) -> Any:
        """text as return_type reads it: HTML, extracted markdown for a string, or the type's own ``from_markdown``;
        the text as it is for a type that reads no markdown."""
        if self._reads_html(return_type):
            return HTML.from_markdown(text)
        if self._reads_text(return_type):
            return ExtractedMarkdown(text)
        from_markdown = getattr(return_type, "from_markdown", None)
        return self.built_by(from_markdown, text, self._instance) if callable(from_markdown) else text

    def built_by(self, from_markdown: Callable[..., Any], text: str, parent: Owner) -> Any:
        """What from_markdown makes of text. A type read with the object it belongs to, such as a practice's rules,
        takes that object as its parent."""
        if "parent" in inspect.signature(from_markdown).parameters:
            return from_markdown(text, parent=parent)
        return from_markdown(text)

    def read_for(self, operation: Callable[..., Any], default: ReturnAnnotation, build: Callable[..., Any] | None = None) -> Any:
        """This section read as the type operation says it returns, default when it names none. ``build(markdown,
        return_type, parent)`` makes that object when given; else ``_coerce`` does, from the text without its YAML for
        HTML or a string. The section's YAML settings stay in its text for the object it becomes, as a rules collection
        reads where it applies from them."""
        return_type = self._return_type_of(operation, default)
        if build is not None:
            return build(self, return_type, self._instance)
        return self._coerced_as(return_type)

    def _coerced_as(self, return_type: ReturnAnnotation) -> Any:
        """The section coerced to return_type: its text without its YAML for HTML or a string, else all of it."""
        document = self.document
        return self._coerce(document.without_yaml if self._reads_plain_text(return_type) else document.text, return_type)

    def _reads_html(self, return_type: ReturnAnnotation) -> bool:
        origin = get_origin(return_type) or return_type
        return return_type is HTML or origin is HTML or get_args(return_type)[:1] == (HTML,)

    def _reads_text(self, return_type: ReturnAnnotation) -> bool:
        return return_type is str or return_type is inspect.Signature.empty or return_type is None

    def _reads_plain_text(self, return_type: ReturnAnnotation) -> bool:
        return self._reads_html(return_type) or self._reads_text(return_type)

    def _return_type_of(self, operation: Callable[..., Any], default: ReturnAnnotation) -> ReturnAnnotation:
        """The type operation's annotations say it returns; default when they name none."""
        try:
            hints = get_type_hints(operation, globalns=getattr(operation, "__globals__", None))
        except Exception as exc:  # noqa: BLE001 - every annotation that fails to resolve is raised as one named failure
            raise MarkdownTypeUnresolved(operation, exc) from exc
        return hints.get("return", default)


def operation_property(operation: Callable[..., Any], read: Callable[[Any], Any]) -> property:
    """A property made from an operation whose body is empty: its value comes from read, such as the operation's
    section of its owner's markdown or the same property of a collection's children, and it carries the operation's
    name, docstring, annotations, and copied annotations, so it installs the way the operation would."""
    def getter(owner: Any) -> Any:
        return read(owner)

    getter.__doc__ = operation.__doc__
    getter.__name__ = operation.__name__
    getter.__annotations__ = dict(getattr(operation, "__annotations__", {}))
    annotation_kinds.copy_annotations(operation, getter)
    return property(getter)


def _section_text(operation: _F, label: str) -> property:
    """A property reading its owner's section under label as the operation's return type says, from the Markdown its
    owner keeps for that label."""

    def read(owner: Any) -> Any:
        section = Markdown.held_by(owner, label)
        return section.read_for(operation, str)

    return operation_property(operation, read)


def _section_collection(operation: _F, label: str) -> property:
    """A property reading its owner's section under label as a collection, once per owner: the collection is kept on
    the owner it is read for."""

    def read(owner: Any) -> Any:
        kept = vars(owner).get(operation.__name__)
        if kept is not None:
            return kept
        section = Markdown.held_by(owner, label)
        result = section.read_for(operation, MarkdownCollection, MarkdownCollection.from_section)
        attach = getattr(result, "attach", None)
        if callable(attach):
            attach(owner, operation.__name__)
        else:
            vars(owner)[operation.__name__] = result
        return result

    return operation_property(operation, read)


def _labelled(build: Callable[[_F, str], property], operation_or_label: _F | str | None, label: str | None) -> property | Callable[[_F], property]:
    """The property build makes for an operation, under the label named, or the operation's own name."""
    if callable(operation_or_label):
        return build(operation_or_label, operation_or_label.__name__)
    return lambda inner: build(inner, str(label or operation_or_label or inner.__name__))


def markdown(operation_or_label: _F | str | None = None, *, label: str | None = None) -> property | Callable[[_F], property]:
    """``@markdown`` or ``@markdown("label")``: the operation's value is its owner's section under that label."""
    return _labelled(_section_text, operation_or_label, label)


def markdown_collection(operation_or_label: _F | str | None = None, *, label: str | None = None) -> property | Callable[[_F], property]:
    """``@markdown_collection`` or ``@markdown_collection("label")``: the operation's value is its owner's section under
    that label, read as a collection and kept on the owner."""
    return _labelled(_section_collection, operation_or_label, label)
