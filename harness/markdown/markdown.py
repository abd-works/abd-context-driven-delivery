"""Co-located markdown extract and HTML conversion — not assembly."""
from __future__ import annotations

import copy
import functools
import threading
import html
import inspect
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, ClassVar, Literal, TypeVar, get_args, get_origin, get_type_hints

from harness.annotations.class_folder import class_folder
from harness.annotations.name import Name
from harness.annotations.annotation import annotation_kinds, hosted_only
from harness.markdown.format import TEMPLATE_FOLDER_NAMES, Format
from harness.markdown.front_matter import FlatSettings

# The seam other modules import from the package: a class's markdown read typed, the scope an owner hands it, and the
# annotations that make a property read it. The classes that locate and read one file stay behind *Markdown*.
__all__ = [
    "HTML",
    "Markdown",
    "MarkdownCollection",
    "MarkdownScope",
    "MarkdownText",
    "MarkdownTypeUnresolved",
    "markdown",
    "markdownCollection",
]

_F = TypeVar("_F", bound=Callable[..., Any])


class ExtractedMarkdown(str):
    """Extracted markdown that still answers ``expand()`` and ``templates()``."""

    def expand(self) -> "ExtractedMarkdown":
        return self

    def __call__(self) -> "ExtractedMarkdown":
        return self


class HTML:
    def __init__(self, text: str) -> None:
        self.text = text

    @classmethod
    def from_markdown(cls, text: str) -> HTML:
        return cls(_markdown_to_html(text))

    def __str__(self) -> str:
        return self.text

    def __contains__(self, item: object) -> bool:
        return str(item) in self.text

    def __eq__(self, other: object) -> bool:
        if isinstance(other, HTML):
            return self.text == other.text
        return self.text == other


def _markdown_to_html(text: str) -> str:
    body = re.sub(r"^#{1,6}\s+.*$", "", text, flags=re.MULTILINE).strip()
    if not body:
        return ""
    chunks: list[str] = []
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        if all(re.match(r"^\s*[-*]\s+", line) for line in lines):
            bullet = re.compile(r"^\s*[-*]\s+")
            items = "".join(
                f"<li>{html.escape(bullet.sub('', line))}</li>"
                for line in lines
            )
            chunks.append(f"<ul>{items}</ul>")
        else:
            chunks.append(f"<p>{html.escape(block)}</p>")
    return "\n".join(chunks)


LocationKind = Literal["file", "folder", "section"]


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

    def child_blocks(self, parent_heading: str) -> list[tuple[str, str]]:
        headings = self.headings()
        parent = next(
            (
                (index, item)
                for index, item in enumerate(headings)
                if item[3].casefold() == parent_heading.casefold()
            ),
            None,
        )
        if parent is None:
            return []
        self._parent_headings = headings
        self._parent_index = parent[0]
        self._parent_level = parent[1][2]
        return self._blocks_under()

    def _blocks_under(self) -> list[tuple[str, str]]:
        child_level = self._parent_level + 1
        blocks: list[tuple[str, str]] = []
        headings = self._parent_headings
        index = self._parent_index
        level = self._parent_level
        for child_index in range(index + 1, len(headings)):
            start, heading_end, next_level, name = headings[child_index]
            if next_level <= level:
                break
            if next_level != child_level:
                continue
            end = next(
                (
                    headings[later][0]
                    for later in range(child_index + 1, len(headings))
                    if headings[later][2] <= child_level
                ),
                len(self._text),
            )
            body = self._text[heading_end:end].lstrip("\r\n").strip()
            blocks.append((name, body))
        return blocks

    def section_child_blocks(self) -> list[tuple[str, str]]:
        headings = self.headings()
        if not headings:
            return []
        return self.child_blocks(headings[0][3])

    def fidelity_blocks(self) -> list[tuple[str, str]]:
        """Each ``### fidelity`` block under a practice document's ``## Fidelities``, by name, in document order."""
        return [(name, body) for name, body in self.child_blocks("Fidelities") if name.casefold() != "fidelities"]

    def fidelity_block(self, fidelity_name: str) -> str:
        wanted = fidelity_name.casefold()
        for name, body in self.fidelity_blocks():
            if name.casefold() == wanted:
                return body
        return ""

    def named_subsection(self, heading: str) -> str:
        return self.slice_heading(heading)


class ReadDocuments:
    """Every markdown file this process has read, parsed once and shared: a practice's document is read for each of its
    sections, and again by every session that makes the practice. A file is read again once its last-written time or
    size changes, so an edit is seen."""

    def __init__(self) -> None:
        self._held: dict[Path, tuple[tuple[int, int], MarkdownText]] = {}
        self._lock = threading.Lock()

    def of(self, path: Path) -> MarkdownText | None:
        """The parsed document at path; none when there is no file."""
        try:
            status = path.stat()
        except (FileNotFoundError, NotADirectoryError):
            return None
        version = (status.st_mtime_ns, status.st_size)
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
        return READ_DOCUMENTS.of(self._path) if self._path.is_file() else None

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

    def read_fidelity_subsection(self, fidelity_name: str) -> str:
        document = self._load()
        if document is None:
            return ""
        block = document.fidelity_block(fidelity_name)
        if not block:
            return ""
        titled = _section_heading(self._heading) if self._heading else ""
        named = MarkdownText(block).named_subsection(titled)
        if named:
            return named
        if titled.casefold() in {"rules", "shared rules"}:
            return ""
        return ""


@dataclass(frozen=True)
class AssetLocation:
    kind: LocationKind
    module_dir: Path
    domain_slug: str
    path: Path | None = None
    folder: Path | None = None
    section_file: Path | None = None
    section_heading: str | None = None
    label: str | None = None
    fidelity: str | None = None
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

    def _extract_fidelity_file(self) -> str:
        if self.folder is None or not self.fidelity:
            return ""
        for stem in Name(self.fidelity).spellings:
            text = self._first_stem_text(stem)
            if text:
                return text
        return ""

    def _first_stem_text(self, stem: str) -> str:
        if self.folder is None:
            return ""
        for path in sorted(self.folder.glob(f"{stem}.*")):
            if path.is_file() and "sketch" not in path.stem.casefold():
                return path.read_text(encoding="utf-8")
        return ""

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
        return self._skip_format_file(path) or self._skip_fidelity_file(path)

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

    def _skip_fidelity_file(self, path: Path) -> bool:
        stem = Name(path.stem).kebab
        fidelity = Name(self.fidelity or "").kebab
        whole_map_example = "thin-slice" in stem or stem.startswith("scenario-") or stem == "examples"
        if self.label == "examples" and fidelity in {"story-map", ""} and whole_map_example:
            return True
        if fidelity != "story-map":
            return False
        if "scenario" in stem or stem == "thin-slice":
            return True
        if path.suffix.lower() == ".md" and "story-map" not in stem and stem != "examples":
            return True
        return False

    def _extract_section(self) -> str:
        if self.section_file is None:
            return ""
        markdown_file = MarkdownFile(self.section_file, self.section_heading or "")
        if self.fidelity:
            return markdown_file.read_fidelity_subsection(self.fidelity)
        if self.section_heading and not markdown_file.section_exists():
            return ""
        return markdown_file.read_section()


@dataclass(frozen=True)
class MarkdownScope:
    """Where an owner keeps its markdown and which part of it the owner reads: the folder beside its class, the slug
    its ``{slug}.md`` is named by, the fidelity and format whose assets (templates, examples) it reads, and whether its
    own sections are subsections of that fidelity's block in the practice document, as a fidelity's are. An owner that
    knows these hands them over as its ``markdown_scope`` property, so nothing here asks the owner for its attributes;
    any other class reads the markdown beside its own file, under the ``domain_slug`` its class declares."""

    folder: Path
    slug: str
    fidelity: str | None = None
    format: str | None = None
    in_fidelity_block: bool = False

    @classmethod
    def beside(cls, owner_class: type) -> MarkdownScope:
        """The markdown beside owner_class's file, named by the slug the class declares, else by its folder."""
        folder = class_folder(owner_class)
        declared = getattr(owner_class, "domain_slug", None)
        return cls(folder, declared if isinstance(declared, str) and declared else folder.name)

    @classmethod
    def of(cls, owner: Any) -> MarkdownScope:
        """The scope owner hands its markdown; the markdown beside its class when it hands none."""
        handed = getattr(type(owner), "markdown_scope", None)
        if isinstance(handed, property):
            return handed.fget(owner)
        return cls.beside(type(owner))

    def at(self, fidelity: str | None = None, format: str | None = None) -> MarkdownScope:
        """This scope at another fidelity or format when one is named, so a caller reads another fidelity's assets
        without changing the owner other callers read."""
        return replace(
            self,
            fidelity=fidelity if fidelity is not None else self.fidelity,
            format=format if format is not None else self.format,
        )


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
    def fidelity(self) -> str | None:
        return self._scope.fidelity or None

    @property
    def format(self) -> str | None:
        return self._scope.format or None

    def _stamp(self, location: AssetLocation) -> AssetLocation:
        fidelity = location.fidelity
        if location.kind == "folder":
            fidelity = fidelity or self.fidelity
        return replace(
            location,
            label=self._label,
            fidelity=fidelity,
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
            try:
                changed_at.append(folder.stat().st_mtime_ns)
            except OSError:
                changed_at.append(None)
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
            self._module_dir,
            self._domain_slug,
            path=(self._module_dir / ".no-template").resolve(),
        )

    def _locate_under(self) -> AssetLocation:
        fidelity_name = self.fidelity if self._scope.in_fidelity_block else None
        if fidelity_name:
            return AssetLocation(
                "section",
                self._module_dir,
                self._domain_slug,
                section_file=self._canonical_domain_md().resolve(),
                section_heading=_section_heading(self._label),
                fidelity=str(fidelity_name),
            )
        folder_name = "_examples" if self._label == "examples" else self._label
        folder = self._search_root_path / folder_name
        if folder.is_dir():
            return AssetLocation("folder", self._module_dir, self._domain_slug, folder=folder.resolve())
        for name in (self._label, f"{self._label}.md"):
            candidate = self._search_root_path / name
            if candidate.is_file():
                return AssetLocation("file", self._module_dir, self._domain_slug, path=candidate.resolve())
        first = self._first_extension_match(self._search_root_path)
        if first:
            return AssetLocation("file", self._module_dir, self._domain_slug, path=first.resolve())
        return AssetLocation(
            "section",
            self._module_dir,
            self._domain_slug,
            section_file=self._canonical_domain_md().resolve(),
            section_heading=_section_heading(self._label),
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
        fidelity = self.fidelity
        if fidelity:
            located = self._named_template_file(fidelity, practice=False)
            if located is not None:
                return located
        located = self._named_template_file(self._domain_slug, practice=True)
        if located is not None:
            return located
        return AssetLocation(
            "file",
            self._module_dir,
            self._domain_slug,
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
                return AssetLocation("file", self._module_dir, self._domain_slug, path=path.resolve())
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
class MarkdownCollection:
    """Listed or keyed extracts that keep the original markdown."""

    def __init__(
        self,
        entries: dict[str, Any] | list[Any] | None = None,
        parent: Any = None,
    ) -> None:
        self.entries: dict[str, Any] | list[Any] = entries if entries is not None else {}
        self.parent = parent
        self._markdown = ""
        for child in self:
            child.parent = self

    @property
    def markdown(self) -> str:
        return self._markdown

    @markdown.setter
    def markdown(self, text: str) -> None:
        self._markdown = text

    def __iter__(self):
        values = self.entries.values() if isinstance(self.entries, dict) else self.entries
        return iter(values)

    def __getitem__(self, name: str) -> Any:
        return self.entries[name]

    @classmethod
    def child(cls, name: str, body: str = "") -> Any:
        return None

    @classmethod
    def from_markdown(cls, text: str, parent: Any = None) -> MarkdownCollection:
        entries: dict[str, Any] = {}
        for name, body in MarkdownText(text).section_child_blocks():
            entry = cls.child(name, body)
            if entry is None:
                continue
            entries[name] = entry
        collection = cls(entries, parent=parent)
        collection.markdown = text
        return collection

    @classmethod
    def from_section(cls, markdown: Markdown, return_type: Any, parent: Any = None) -> Any:
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

    def attach(self, instance: Any, name: str | None = None) -> None:
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

    def __init__(self, fn: Callable[..., Any], cause: BaseException) -> None:
        self.property_name = fn.__qualname__
        self.annotations = dict(getattr(fn, "__annotations__", {}) or {})
        super().__init__(f"{self.property_name}: annotations {self.annotations!r} do not resolve: {cause}")


class Markdown:
    """One labelled section of an owner's markdown, located from the scope the owner hands over and read once."""

    def __init__(self, instance: Any, label: str, *, fidelity: str | None = None, format: str | None = None) -> None:
        self._instance = instance
        self._label = label
        self._fidelity = fidelity
        self._format = format

    _HELD_AS = "_held_markdown"

    @classmethod
    def from_label(cls, instance: Any, label: str, *, fidelity: str | None = None, format: str | None = None) -> Markdown:
        """Markdown for ``label`` on ``instance``, at the fidelity and format named here when given, else at the
        instance's current ones."""
        return cls(instance, label, fidelity=fidelity, format=format)

    @classmethod
    def held_by(cls, owner: Any, label: str) -> Markdown:
        """The Markdown of label on owner at the scope owner reads it in now, made the first time and kept on owner, so
        a second read answers from the text the first found. A scope owner moves to, such as another fidelity or
        format, has a Markdown of its own, made when it is first read."""
        scope = MarkdownScope.of(owner)
        held: dict[tuple[str, MarkdownScope], Markdown] = vars(owner).setdefault(cls._HELD_AS, {})
        key = (label, scope)
        if key not in held:
            held[key] = cls(owner, label, fidelity=scope.fidelity, format=scope.format)
        return held[key]

    @functools.cached_property
    def location(self) -> AssetLocation:
        """Where this section lives, located once: it depends only on the instance, label, fidelity and format this
        Markdown was made with."""
        scope = MarkdownScope.of(self._instance).at(fidelity=self._fidelity, format=self._format)
        return AssetLocator(scope, self._label).locate()

    @functools.cached_property
    def document(self) -> MarkdownText:
        """The section, read once from its location."""
        return MarkdownText(self.location.extract())

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

    def coerce(self, text: str, return_type: Any) -> Any:
        """text as return_type reads it: HTML, extracted markdown for a string, or the type's own ``from_markdown``;
        the text as it is for a type that reads no markdown."""
        if self._reads_html(return_type):
            return HTML.from_markdown(text)
        if self._reads_text(return_type):
            return ExtractedMarkdown(text)
        from_markdown = getattr(return_type, "from_markdown", None)
        return self.built_by(from_markdown, text, self._instance) if callable(from_markdown) else text

    def built_by(self, from_markdown: Callable[..., Any], text: str, parent: Any) -> Any:
        """What from_markdown makes of text. A type read with the object it belongs to, such as a practice's rules,
        takes that object as its parent."""
        if "parent" in inspect.signature(from_markdown).parameters:
            return from_markdown(text, parent=parent)
        return from_markdown(text)

    def read_into(self, return_type: Any, build: Callable[..., Any] | None = None) -> Any:
        """This section read as return_type. ``build(markdown, return_type, parent)`` makes that object when given;
        else ``coerce`` does, from the text without its YAML for HTML or a string. The section's YAML settings
        stay in its text for the object it becomes, as a rules collection reads where it applies from them."""
        raw = self.document.text
        if build is None and self._reads_plain_text(return_type):
            return self.coerce(self.document.without_yaml, return_type)
        return build(self, return_type, self._instance) if build is not None else self.coerce(raw, return_type)

    def _reads_html(self, return_type: Any) -> bool:
        origin = get_origin(return_type) or return_type
        return return_type is HTML or origin is HTML or get_args(return_type)[:1] == (HTML,)

    def _reads_text(self, return_type: Any) -> bool:
        return return_type is str or return_type is inspect.Signature.empty or return_type is None

    def _reads_plain_text(self, return_type: Any) -> bool:
        return self._reads_html(return_type) or self._reads_text(return_type)

    def return_type_of(self, fn: Callable[..., Any], default: Any) -> Any:
        """The type fn's annotations say it returns; default when they name none."""
        try:
            hints = get_type_hints(fn, globalns=getattr(fn, "__globals__", None))
        except Exception as exc:  # noqa: BLE001 - every annotation that fails to resolve is raised as one named failure
            raise MarkdownTypeUnresolved(fn, exc) from exc
        return hints.get("return", default)


class OperationProperty:
    """A property made from an operation whose body is empty: its value comes from the reader it is given, such as the
    operation's section of its owner's markdown or the same property of a collection's children, and it carries the
    operation's name, docstring, annotations, and copied annotations, so it installs the way the operation would."""

    def __init__(self, operation: Callable[..., Any]) -> None:
        self._operation = operation

    def reading(self, read: Callable[[Any], Any]) -> property:
        """A property whose getter is read, wrapped to look like the operation."""
        def getter(owner: Any) -> Any:
            return read(owner)

        getter.__doc__ = self._operation.__doc__
        getter.__name__ = self._operation.__name__
        getter.__annotations__ = dict(getattr(self._operation, "__annotations__", {}))
        annotation_kinds.copy_annotations(self._operation, getter)
        return property(getter)


def _section_text(operation: _F, label: str) -> property:
    """A property reading its owner's section under label as the operation's return type says, from the Markdown its
    owner keeps for that label."""

    def read(owner: Any) -> Any:
        section = Markdown.held_by(owner, label)
        return section.read_into(section.return_type_of(operation, str))

    return OperationProperty(operation).reading(read)


def _section_collection(operation: _F, label: str) -> property:
    """A property reading its owner's section under label as a collection, once per owner: the collection is kept on
    the owner it is read for."""

    def read(owner: Any) -> Any:
        kept = vars(owner).get(operation.__name__)
        if kept is not None:
            return kept
        section = Markdown.held_by(owner, label)
        result = section.read_into(section.return_type_of(operation, MarkdownCollection), MarkdownCollection.from_section)
        attach = getattr(result, "attach", None)
        if callable(attach):
            attach(owner, operation.__name__)
        else:
            vars(owner)[operation.__name__] = result
        return result

    return OperationProperty(operation).reading(read)


def _labelled(build: Callable[[_F, str], property], fn: _F | str | None, label: str | None) -> property | Callable[[_F], property]:
    """The property build makes for an operation, under the label named, or the operation's own name."""
    if callable(fn):
        return build(fn, fn.__name__)
    return lambda inner: build(inner, str(label or fn or inner.__name__))


def markdown(fn: _F | str | None = None, *, label: str | None = None) -> property | Callable[[_F], property]:
    """``@markdown`` or ``@markdown("label")``: the operation's value is its owner's section under that label."""
    return _labelled(_section_text, fn, label)


def markdownCollection(fn: _F | str | None = None, *, label: str | None = None) -> property | Callable[[_F], property]:
    """``@markdownCollection`` or ``@markdownCollection("label")``: the operation's value is its owner's section under
    that label, read as a collection and kept on the owner."""
    return _labelled(_section_collection, fn, label)
