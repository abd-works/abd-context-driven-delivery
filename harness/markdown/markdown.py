"""Co-located markdown extract and HTML conversion — not assembly."""
from __future__ import annotations

import html
import inspect
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Literal, TypeVar, get_args, get_origin, get_type_hints

_F = TypeVar("_F", bound=Callable[..., Any])


class MarkdownSlot(str):
    """Extracted markdown that still answers ``expand()`` and ``templates()``."""

    def expand(self) -> "MarkdownSlot":
        return self

    def __call__(self) -> "MarkdownSlot":
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


_FORMAT_TEMPLATE_EXT = {
    "python": ".py",
    "py": ".py",
    "javascript": ".js",
    "js": ".js",
    "markdown": ".md",
    "md": ".md",
    "typescript": ".ts",
    "ts": ".ts",
    "java": ".java",
}

_FORMAT_DIR_ALIAS = {
    "markdown": "md",
    "md": "md",
    "python": "py",
    "py": "py",
    "typescript": "ts",
    "ts": "ts",
    "javascript": "js",
    "js": "js",
    "java": "java",
}

LocationKind = Literal["file", "folder", "section"]
_MISSING = object()


def _slug_variants(domain_slug: str) -> list[str]:
    variants = [domain_slug]
    for alt in (domain_slug.replace("_", "-"), domain_slug.replace("-", "_")):
        if alt not in variants:
            variants.append(alt)
    return variants


def _section_heading(label: str) -> str:
    if label.casefold() in {"context", "contexts", "overview"}:
        return "Overview"
    return label.replace("_", " ").replace("-", " ").title()


class MarkdownText:
    """A markdown document: headings, slices, and child sections."""

    def __init__(self, text: str) -> None:
        self._text = text

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

    def _heading_at(self, bare: str) -> tuple[int, int, int, str] | None:
        if self._fence is not None:
            return None
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", bare)
        if heading is None:
            return None
        offset = self._offset
        return (offset, offset + len(bare), len(heading.group(1)), heading.group(2))

    def headings(self) -> list[tuple[int, int, int, str]]:
        headings: list[tuple[int, int, int, str]] = []
        self._offset = 0
        self._fence = None
        for line in self._text.splitlines(keepends=True):
            bare = line.rstrip("\r\n")
            self._fence, consumed = self._fence_update(self._fence, bare)
            if not consumed:
                recorded = self._heading_at(bare)
                if recorded is not None:
                    headings.append(recorded)
            self._offset += len(line)
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

    def fidelity_block(self, fidelity_name: str) -> str:
        wanted = fidelity_name.casefold()
        for name, body in Markdown(None, "").fidelity_blocks(self._text):
            if name.casefold() == wanted:
                return body
        return ""

    def named_subsection(self, heading: str) -> str:
        return self.slice_heading(heading)


class MarkdownFile:
    """A markdown file on disk, optionally scoped to one heading."""

    def __init__(self, path: Path, heading: str = "") -> None:
        self._path = path
        self._heading = heading

    def _load(self) -> MarkdownText | None:
        if not self._path.is_file():
            return None
        return MarkdownText(self._path.read_text(encoding="utf-8"))

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
            return document._text
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
        for stem in _slug_variants(self.fidelity):
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
        aliases = {"md", "py", "ts", "js", "java"}
        return name.casefold() in aliases and name.casefold() != wanted

    def _format_dir_name(self) -> str:
        fmt = (self.format or "").casefold()
        return _FORMAT_DIR_ALIAS.get(fmt, fmt if fmt in {"md", "py", "ts", "js", "java"} else "")

    def _skip_format_file(self, path: Path) -> bool:
        fmt = (self.format or "").casefold()
        if not fmt:
            return False
        allowed = {
            "markdown": {".md"},
            "md": {".md"},
            "python": {".py"},
            "py": {".py"},
            "typescript": {".ts"},
            "ts": {".ts"},
            "javascript": {".js"},
            "js": {".js"},
            "java": {".java"},
        }.get(fmt)
        if not allowed:
            return False
        return path.suffix.lower() not in allowed

    def _skip_fidelity_file(self, path: Path) -> bool:
        stem = path.stem.casefold().replace("_", "-")
        if self.label == "examples" and (
            "thin-slice" in stem
            or stem.startswith("scenario-")
            or (stem == "examples" and (self.fidelity or "").casefold().replace("_", "-") in {"story-map", ""})
        ):
            fidelity = (self.fidelity or "").casefold().replace("_", "-")
            if fidelity in {"story-map", ""}:
                return True
        fidelity = (self.fidelity or "").casefold().replace("_", "-")
        if fidelity not in {"story-map"}:
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


class AssetLocator:
    def __init__(
        self,
        instance: Any,
        label: str,
        *,
        group: str | None = None,
        filter_key: str | None = None,
    ) -> None:
        self._instance = instance
        self._label = label
        self._group = group
        self._filter_key = filter_key
        self._module_dir = Path(".")
        self._domain_slug = ""
        self._search_root_path = Path(".")
        self._active_format: str | None = None

    def class_file_directory(self) -> Path:
        instance = self._instance
        practice = getattr(instance, "practice_guidance", None)
        if practice is not None:
            instance = practice
        stored = getattr(instance, "module_dir", None)
        if stored is not None:
            return Path(stored)
        try:
            return Path(inspect.getfile(type(instance))).resolve().parent
        except (TypeError, OSError):
            return Path(".")

    def _active_resource(self, key: str | None) -> str | None:
        if not key:
            return None
        if key == "fidelity":
            return self._current_fidelity()
        value = getattr(self._instance, key, None)
        return str(value) if value else None

    def _current_fidelity(self) -> str | None:
        current = getattr(getattr(self._instance, "fidelities", None), "current", None)
        if current is None:
            value = getattr(self._instance, "fidelity", None)
            return str(value) if value else None
        value = getattr(current, "fidelity", None) or getattr(current, "name", None)
        return str(value) if value else None

    def _fidelity_scope(self) -> str | None:
        """Fidelity section name on Guidance only — not WorkSession.name or AgentToolSet.name."""
        if getattr(self._instance, "practice_guidance", None) is not None:
            value = getattr(self._instance, "name", None)
            return str(value) if value else None
        for cls in type(self._instance).__mro__:
            scoped = self._declared_name_scope(cls)
            if scoped is not _MISSING:
                return scoped
        return None

    def _declared_name_scope(self, cls: type) -> str | None | object:
        if cls is object:
            return _MISSING
        declared = cls.__dict__.get("name", _MISSING)
        if declared is _MISSING:
            return _MISSING
        if isinstance(declared, property):
            return None
        value = getattr(self._instance, "name", None)
        return str(value) if value else None

    @property
    def fidelity(self) -> str | None:
        return self._active_resource("fidelity")

    @property
    def format(self) -> str | None:
        return self._active_resource("format")

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
        return self._stamp(self._locate())

    def _locate(self) -> AssetLocation:
        self._module_dir = self.class_file_directory()
        self._domain_slug = self._module_dir.name
        filter_value = self._active_resource(self._filter_key) if self._filter_key else None
        if self._label == "templates":
            return self._locate_template_or_missing(filter_value)
        self._search_root_path = self._search_root(self._module_dir, filter_value)
        return self._locate_under()

    def _locate_template_or_missing(self, filter_value: str | None) -> AssetLocation:
        self._active_format = filter_value or self._active_resource("format")
        located = self._locate_templates()
        if located.path is not None and located.path.is_file():
            return located
        return AssetLocation(
            "file",
            self._module_dir,
            self._domain_slug,
            path=(self._module_dir / ".no-template").resolve(),
        )

    def _search_root(self, module_dir: Path, filter_value: str | None) -> Path:
        root = module_dir
        if self._group:
            root = root / self._group
        if not filter_value:
            return root
        as_dir = root / filter_value
        if as_dir.is_dir():
            return as_dir
        return root

    def _locate_under(self) -> AssetLocation:
        fidelity_name = self._fidelity_scope()
        if fidelity_name:
            return AssetLocation(
                "section",
                self._module_dir,
                self._domain_slug,
                section_file=self._canonical_domain_md().resolve(),
                section_heading=_section_heading(self._label),
                fidelity=str(fidelity_name),
            )
        folder = self._search_root_path / self._label
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
        for slug in _slug_variants(self._domain_slug):
            candidate = root / f"{slug}.md"
            if candidate.is_file():
                return candidate
        return None

    def _locate_templates(self) -> AssetLocation:
        fidelity = self._active_resource("fidelity")
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
        stems = list(_slug_variants(name))
        if practice:
            stems = [
                extra
                for slug in _slug_variants(name)
                for extra in (slug, f"{slug}-templates", f"{slug}-template")
            ]
        self._template_stems = stems
        self._template_ext = _FORMAT_TEMPLATE_EXT.get(self._active_format or "", "")
        for folder in self._template_folders():
            located = self._template_in_folder(folder)
            if located is not None:
                return located
        return None

    def _template_folders(self) -> list[Path]:
        folders: list[Path] = []
        shared = self._module_dir / "templates"
        if self._active_format:
            alias = _FORMAT_DIR_ALIAS.get(self._active_format, self._active_format)
            folders.append(shared / alias)
            folders.append(self._module_dir / "formats" / self._active_format)
        folders.append(shared)
        return folders

    def _template_in_folder(self, folder: Path) -> AssetLocation | None:
        if not folder.is_dir():
            return None
        if self._template_ext:
            return self._template_with_ext(folder)
        return self._template_any_ext(folder)

    def _template_with_ext(self, folder: Path) -> AssetLocation | None:
        for stem in self._template_stems:
            path = folder / f"{stem}{self._template_ext}"
            if path.is_file() and "sketch" not in path.stem.casefold():
                return AssetLocation(
                    "file", self._module_dir, self._domain_slug, path=path.resolve()
                )
        return None

    def _template_any_ext(self, folder: Path) -> AssetLocation | None:
        for stem in self._template_stems:
            for path in sorted(folder.glob(f"{stem}.*")):
                if path.is_file() and "sketch" not in path.stem.casefold():
                    return AssetLocation(
                        "file", self._module_dir, self._domain_slug, path=path.resolve()
                    )
        return None


_YAML_FENCE = re.compile(r"```ya?ml\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


class YamlBinder:
    """Parse YAML fences and assign matching fields onto an instance."""

    def __init__(self, instance: Any | None = None) -> None:
        self._instance = instance

    def mapping(self, body: str) -> dict[str, Any]:
        try:
            import yaml
        except ImportError:
            yaml = None
        if yaml is not None:
            loaded = yaml.safe_load(body)
            if isinstance(loaded, dict):
                return loaded
        return self.pairs(body)

    def pairs(self, body: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for raw in body.splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or ":" not in line or line.startswith("- "):
                continue
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip().strip("'\"")
        return fields

    def _wanted_names(self, key: str) -> set[str]:
        folded = key.casefold()
        snake = _to_snake(key).casefold()
        wanted = {
            folded,
            snake,
            key.replace(" ", "_").replace("-", "_").casefold(),
        }
        if folded.endswith("s") and len(folded) > 1:
            wanted.add(folded[:-1])
            wanted.add(snake[:-1] if snake.endswith("s") else snake)
            return wanted
        wanted.add(f"{folded}s")
        wanted.add(f"{snake}s")
        return wanted

    def matching_attr(self, key: str) -> str | None:
        wanted = self._wanted_names(key)
        for name in dir(self._instance):
            if self._is_matching_value(name, wanted):
                return name
        return None

    def _is_matching_value(self, name: str, wanted: set[str]) -> bool:
        if name.startswith("_") or name.casefold() not in wanted:
            return False
        member = getattr(type(self._instance), name, None)
        if callable(member) and not isinstance(member, property):
            return False
        value = getattr(self._instance, name, None)
        if callable(value) and not isinstance(member, property):
            return False
        return True

    def assign(self, attr: str, value: Any) -> None:
        stored = attr
        descriptor = getattr(type(self._instance), attr, None)
        if isinstance(descriptor, property) and descriptor.fset is None:
            leftovers = getattr(self._instance, "yaml", None)
            if isinstance(leftovers, dict):
                leftovers[_to_snake(attr)] = self.as_string(value)
            return
        if stored == "default_format" and isinstance(value, str):
            value = canonical_format(value.split()[0].strip("()`"))
        elif stored == "clean_engineering" and isinstance(value, str):
            value = value.split()[0].strip("()`").replace("-", "_")
        setattr(self._instance, stored, value)

    def as_string(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, bool):
            return "true" if value else "false"
        if value is None:
            return ""
        if isinstance(value, dict):
            return ",".join(f"{k}={self.as_string(v)}" for k, v in value.items())
        return str(value)

    def merge_map(self, leftovers: dict[str, str]) -> None:
        if not leftovers:
            return
        current = getattr(self._instance, "yaml", None)
        if isinstance(current, dict):
            current.update(leftovers)

    def yaml_fields(self, text: str) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        for match in _YAML_FENCE.finditer(text):
            merged.update(self.mapping(match.group(1)))
        return merged

    def bind_yaml_mapping(self, fields: dict[str, Any]) -> None:
        leftovers: dict[str, str] = {}
        for key, value in fields.items():
            attr = self.matching_attr(key)
            if attr is None:
                leftovers[_to_snake(key)] = self.as_string(value)
                continue
            current = getattr(self._instance, attr, None)
            if isinstance(value, dict) and _is_bindable(current):
                YamlBinder(current).bind_yaml_mapping(value)
                continue
            self.assign(attr, value)
        self.merge_map(leftovers)

    def bind_yaml(self, text: str) -> None:
        self.bind_yaml_mapping(self.yaml_fields(text))


def strip_yaml_fences(text: str) -> str:
    return _YAML_FENCE.sub("", text).strip()


def _to_snake(key: str) -> str:
    token = key.strip().replace(" ", "_").replace("-", "_")
    chars: list[str] = []
    for index, char in enumerate(token):
        if char.isupper() and index and token[index - 1] != "_":
            chars.append("_")
        chars.append(char.lower())
    return "".join(chars).replace("__", "_")


def _is_bindable(current: Any) -> bool:
    return current is not None and not isinstance(
        current, (str, int, float, bool, list, tuple, bytes, dict)
    )


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
        self.yaml: dict[str, str] = {}
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
            YamlBinder(entry).bind_yaml(body)
            entries[name] = entry
        collection = cls(entries, parent=parent)
        collection.markdown = text
        return collection

    @classmethod
    def coerce(cls, markdown: Markdown, return_type: Any, parent: Any = None) -> Any:
        text = markdown.raw()
        origin = get_origin(return_type) or return_type
        if origin is list:
            return cls.from_list(markdown)
        builder = getattr(return_type, "from_markdown", None)
        if callable(builder) and return_type is not cls:
            try:
                result = builder(text, parent=parent)
            except TypeError:
                result = builder(text)
            holder = cls(parent=parent)
            holder.markdown = text
            holder.keep_extract(result)
            return result
        return cls.from_markdown(text, parent=parent)

    @classmethod
    def from_list(cls, markdown: Markdown) -> MarkdownCollection:
        collection = cls.from_markdown(markdown.extract())
        # EXTEND: one entry per section bullet or folder file
        return collection

    def bind(self, instance: Any, name: str | None = None) -> None:
        self.parent = instance
        previous = vars(instance).get(name) if name else None
        if name is not None:
            vars(instance)[name] = self
        for attr, value in list(vars(instance).items()):
            if value is self:
                continue
            if value is previous or (name is None and type(value) is type(self)):
                vars(instance)[attr] = self

    def keep_extract(self, result: Any) -> None:
        if result is None:
            return
        result.markdown = self._markdown

    def as_property(self, fn: _F) -> property:
        prop_label = self._label if hasattr(self, "_label") else fn.__name__
        return self._collection_property(fn, prop_label)

    def _collection_property(self, fn: _F, prop_label: str) -> property:
        def getter(owner: Any) -> Any:
            name = fn.__name__
            bound = vars(owner).get(name)
            if bound is not None:
                return bound
            md = Markdown.from_label(owner, prop_label)
            hints = md._return_hints(fn)
            return_type = hints.get("return", MarkdownCollection)
            raw = md.raw()
            YamlBinder(owner).bind_yaml(raw)
            result = MarkdownCollection.coerce(md, return_type, parent=owner)
            YamlBinder(result).bind_yaml(raw)
            bind = getattr(result, "bind", None)
            if callable(bind):
                bind(owner, name)
            else:
                vars(owner)[name] = result
            class_dir = AssetLocator(owner, prop_label).class_file_directory()
            for entry in result or ():
                bind_scanner = getattr(entry, "bind_scanner", None)
                if callable(bind_scanner):
                    bind_scanner(class_dir)
            return result

        getter.__doc__ = fn.__doc__
        getter.__name__ = fn.__name__
        getter.__annotations__ = dict(getattr(fn, "__annotations__", {}))
        _copy_marks(fn, getter)
        return property(getter)

    def markdown_collection(
        self, fn: _F | str | None = None, *, label: str | None = None
    ) -> property | Callable[[_F], property]:
        if callable(fn):
            return self.as_property(fn)

        def decorator(inner: _F) -> property:
            holder = MarkdownCollection()
            holder._label = str(label or fn or inner.__name__)
            return holder.as_property(inner)

        return decorator


class Markdown:
    def __init__(self, instance: Any, label: str) -> None:
        self._instance = instance
        self._label = label

    @classmethod
    def from_label(cls, instance: Any, label: str) -> Markdown:
        return cls(instance, label)

    def raw(self) -> str:
        location = AssetLocator(self._instance, self._label).locate()
        return location.extract()

    def extract(self) -> str:
        text = self.raw()
        YamlBinder(self._instance).bind_yaml(text)
        return strip_yaml_fences(text)

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
        origin = get_origin(return_type) or return_type
        if return_type is HTML or origin is HTML:
            return HTML.from_markdown(text)
        if return_type is str or return_type is inspect.Signature.empty or return_type is None:
            return MarkdownSlot(text)
        if origin is dict:
            return self.templates_path_map()
        from harness.guidance.rule import RulesCollection

        if return_type is RulesCollection:
            return RulesCollection.from_markdown(text, parent=self._instance)
        from_markdown = getattr(return_type, "from_markdown", None)
        if callable(from_markdown):
            return from_markdown(text)
        return text

    def _format_key_for_template(self, path: Path) -> str:
        parts = path.relative_to(self._templates_folder).parts
        if len(parts) > 1:
            folder_key = _FORMAT_ALIASES.get(parts[0].casefold())
            if folder_key:
                return folder_key
        ext = path.suffix.lstrip(".").lower()
        return _EXT_TO_FORMAT.get(ext, ext)

    def templates_path_map(self) -> dict[str, str]:
        class_dir = AssetLocator(self._instance, self._label).class_file_directory()
        self._templates_folder = class_dir / "templates"
        mapping: dict[str, str] = {}
        if not self._templates_folder.is_dir():
            return mapping
        for path in sorted(self._templates_folder.rglob("*")):
            if not path.is_file() or path.name.startswith("."):
                continue
            rel = path.relative_to(class_dir).as_posix()
            key = self._format_key_for_template(path)
            if not key:
                continue
            mapping[key] = rel
        return mapping

    def as_property(self, fn: _F) -> property:
        prop_label = self._label
        def getter(owner: Any) -> Any:
            md = Markdown.from_label(owner, prop_label)
            hints = md._return_hints(fn)
            return_type = hints.get("return", str)
            raw = md.raw()
            YamlBinder(owner).bind_yaml(raw)
            text = strip_yaml_fences(raw)
            if return_type is HTML:
                return HTML.from_markdown(text)
            origin = get_origin(return_type)
            if origin is not None:
                args = get_args(return_type)
                if origin is dict:
                    return md.coerce(text, return_type)
                if args and args[0] is HTML:
                    return HTML.from_markdown(text)
            if return_type is str or return_type is inspect.Signature.empty or return_type is None:
                return MarkdownSlot(text)
            result = md.coerce(raw, return_type)
            YamlBinder(result).bind_yaml(raw)
            from harness.guidance.rule import RulesCollection

            if isinstance(result, RulesCollection):
                class_dir = AssetLocator(owner, prop_label).class_file_directory()
                for rule in result:
                    rule.bind_scanner(class_dir)
            return result

        getter.__doc__ = fn.__doc__
        getter.__name__ = fn.__name__
        getter.__annotations__ = dict(getattr(fn, "__annotations__", {}))
        _copy_marks(fn, getter)
        return property(getter)

    def _return_hints(self, fn: Callable[..., Any]) -> dict[str, Any]:
        try:
            return get_type_hints(fn, globalns=getattr(fn, "__globals__", None))
        except Exception:
            annot = getattr(fn, "__annotations__", {}) or {}
            return dict(annot)

    def fidelity_blocks(self, text: str) -> list[tuple[str, str]]:
        return [
            (name, body)
            for name, body in MarkdownText(text).child_blocks("Fidelities")
            if name.casefold() != "fidelities"
        ]

    def fidelity_stage(self, body: str) -> str:
        stage = YamlBinder().yaml_fields(body).get("stage")
        if isinstance(stage, str) and stage.strip():
            return stage.strip().strip("`")
        match = re.search(r"(?im)^\*\*Stage:\*\*\s*`?(\S+?)`?\s*$", body)
        if match:
            return match.group(1)
        match = re.search(r"(?im)^stage:\s*`?(\S+?)`?\s*$", body)
        return match.group(1) if match else ""

    def _fidelity_labeled_line(self, body: str, label: str) -> str:
        match = re.search(
            rf"(?im)^\*\*{re.escape(label)}:\*\*\s*(.+?)\s*$",
            body,
        )
        return match.group(1).strip().strip("`") if match else ""

    def fidelity_format(self, body: str) -> str:
        fields = YamlBinder().yaml_fields(body)
        token = fields.get("default_format") or fields.get("defaultFormat")
        if isinstance(token, str) and token.strip():
            return canonical_format(token.split()[0].strip("()`"))
        rest = self._fidelity_labeled_line(body, "Default format")
        if not rest:
            return ""
        return canonical_format(rest.split()[0].strip("()`"))

    def fidelity_clean_engineering(self, body: str) -> str:
        fields = YamlBinder().yaml_fields(body)
        token = fields.get("clean_engineering") or fields.get("cleanEngineering")
        if isinstance(token, str) and token.strip():
            return token.split()[0].strip("()`").replace("-", "_")
        rest = self._fidelity_labeled_line(body, "Clean Engineering")
        if not rest:
            return ""
        return rest.split()[0].strip("()`").replace("-", "_")


_EXT_TO_FORMAT = {
    "md": "markdown",
    "py": "python",
    "ts": "typescript",
    "js": "javascript",
    "java": "java",
    "drawio": "drawio",
    "html": "html",
    "json": "json",
}

_FORMAT_ALIASES = {
    "md": "markdown",
    "markdown": "markdown",
    "py": "python",
    "python": "python",
    "ts": "typescript",
    "typescript": "typescript",
    "js": "javascript",
    "javascript": "javascript",
    "java": "java",
    "drawio": "drawio",
    "miro": "miro",
    "html": "html",
    "json": "json",
}


def canonical_format(name: str | None) -> str:
    """Resolve a format or folder alias to the output-channel key."""
    if not name:
        return ""
    folded = name.casefold()
    return _FORMAT_ALIASES.get(folded, folded)


_MARK_ATTRS = (
    "_skill",
    "_command",
    "_rules",
    "_mcp",
    "_hook",
    "_is_agent_instructions",
    "_is_agent_tool",
    "_is_toolset_collection",
    "_skill_name",
    "_command_name",
    "_hook_name",
)


def _copy_marks(src: Any, dest: Any) -> None:
    for attr in _MARK_ATTRS:
        if hasattr(src, attr):
            setattr(dest, attr, getattr(src, attr))


def markdown(
    fn: _F | str | None = None, *, label: str | None = None
) -> property | Callable[[_F], property]:
    if callable(fn):
        return Markdown.from_label(None, fn.__name__).as_property(fn)

    def decorator(inner: _F) -> property:
        prop_label = label or fn or inner.__name__
        return Markdown.from_label(None, str(prop_label)).as_property(inner)

    return decorator


markdownCollection = MarkdownCollection().markdown_collection
