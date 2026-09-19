"""Co-located markdown extract and HTML conversion — not assembly."""
from __future__ import annotations

import html
import inspect
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Literal, TypeVar, get_args, get_origin, get_type_hints

_F = TypeVar("_F", bound=Callable[..., Any])


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


def class_file_directory(host: Any) -> Path:
    practice = getattr(host, "practice_guidance", None)
    if practice is not None:
        host = practice
    stored = getattr(host, "module_dir", None)
    if stored is not None:
        return Path(stored)
    try:
        return Path(inspect.getfile(type(host))).resolve().parent
    except (TypeError, OSError):
        return Path(".")


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


def _active_resource(instance: Any, key: str | None) -> str | None:
    if not key:
        return None
    if key == "fidelity":
        current = getattr(getattr(instance, "fidelities", None), "current", None)
        if current is not None:
            value = getattr(current, "fidelity", None) or getattr(current, "name", None)
            return str(value) if value else None
    value = getattr(instance, key, None)
    return str(value) if value else None


def _fidelity_scope(host: Any) -> str | None:
    """Fidelity section name on Guidance hosts only — not WorkSession.name or AgentToolSet.name."""
    if getattr(host, "practice_guidance", None) is not None:
        value = getattr(host, "name", None)
        return str(value) if value else None
    for cls in type(host).__mro__:
        if cls is object:
            continue
        declared = cls.__dict__.get("name", _MISSING)
        if declared is _MISSING:
            continue
        if isinstance(declared, property):
            return None
        value = getattr(host, "name", None)
        return str(value) if value else None
    return None


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


class AssetLocator:
    def __init__(
        self,
        host: Any,
        label: str,
        *,
        group: str | None = None,
        filter_key: str | None = None,
    ) -> None:
        self._host = host
        self._label = label
        self._group = group
        self._filter_key = filter_key

    @property
    def fidelity(self) -> str | None:
        return _active_resource(self._host, "fidelity")

    @property
    def format(self) -> str | None:
        return _active_resource(self._host, "format")

    def _stamp(self, location: AssetLocation) -> AssetLocation:
        return replace(
            location,
            label=self._label,
            fidelity=location.fidelity,
            format=location.format or self.format,
        )

    def locate(self) -> AssetLocation:
        return self._stamp(self._locate())

    def _locate(self) -> AssetLocation:
        module_dir = class_file_directory(self._host)
        domain_slug = (
            getattr(self._host, "domain_slug", None)
            or getattr(self._host, "toolset_name", None)
            or module_dir.name
        )
        filter_value = _active_resource(self._host, self._filter_key) if self._filter_key else None
        if self._label == "templates":
            active_format = filter_value or _active_resource(self._host, "format")
            located = self._locate_templates(module_dir, domain_slug, active_format)
            if located.path is not None and located.path.is_file():
                return located
            return AssetLocation(
                "file",
                module_dir,
                domain_slug,
                path=(module_dir / ".no-template").resolve(),
            )
        search_root = self._search_root(module_dir, filter_value)
        return self._locate_under(search_root, module_dir, domain_slug)

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

    def _locate_under(self, search_root: Path, module_dir: Path, domain_slug: str) -> AssetLocation:
        fidelity_name = _fidelity_scope(self._host)
        if fidelity_name:
            section_file = self._canonical_domain_md(module_dir, search_root, domain_slug)
            return AssetLocation(
                "section",
                module_dir,
                domain_slug,
                section_file=section_file.resolve(),
                section_heading=_section_heading(self._label),
                fidelity=str(fidelity_name),
            )
        folder = search_root / self._label
        if folder.is_dir():
            return AssetLocation("folder", module_dir, domain_slug, folder=folder.resolve())
        for name in (self._label, f"{self._label}.md"):
            candidate = search_root / name
            if candidate.is_file():
                return AssetLocation("file", module_dir, domain_slug, path=candidate.resolve())
        first = self._first_extension_match(search_root)
        if first:
            return AssetLocation("file", module_dir, domain_slug, path=first.resolve())
        section_file = self._canonical_domain_md(module_dir, search_root, domain_slug)
        return AssetLocation(
            "section",
            module_dir,
            domain_slug,
            section_file=section_file.resolve(),
            section_heading=_section_heading(self._label),
        )

    def _first_extension_match(self, search_root: Path) -> Path | None:
        if not search_root.is_dir():
            return None
        matches = sorted(c for c in search_root.glob(f"{self._label}.*") if c.is_file())
        return matches[0] if matches else None

    def _canonical_domain_md(self, module_dir: Path, search_root: Path, domain_slug: str) -> Path:
        for root in (module_dir, search_root):
            for slug in _slug_variants(domain_slug):
                candidate = root / f"{slug}.md"
                if candidate.is_file():
                    return candidate
        return module_dir / f"{domain_slug}.md"

    def _locate_templates(
        self, module_dir: Path, domain_slug: str, active_format: str | None
    ) -> AssetLocation:
        fidelity = _active_resource(self._host, "fidelity")
        if fidelity:
            located = self._named_template_file(
                module_dir, fidelity, active_format, domain_slug, practice=False
            )
            if located is not None:
                return located
        located = self._named_template_file(
            module_dir, domain_slug, active_format, domain_slug, practice=True
        )
        if located is not None:
            return located
        return AssetLocation(
            "file",
            module_dir,
            domain_slug,
            path=(module_dir / ".no-template").resolve(),
        )

    def _named_template_file(
        self,
        module_dir: Path,
        name: str,
        active_format: str | None,
        domain_slug: str,
        *,
        practice: bool,
    ) -> AssetLocation | None:
        stems = list(_slug_variants(name))
        if practice:
            stems = [
                extra
                for slug in _slug_variants(name)
                for extra in (slug, f"{slug}-templates", f"{slug}-template")
            ]
        folders: list[Path] = []
        shared = module_dir / "templates"
        if active_format:
            alias = _FORMAT_DIR_ALIAS.get(active_format, active_format)
            folders.append(shared / alias)
            folders.append(module_dir / "formats" / active_format)
        folders.append(shared)
        ext = _FORMAT_TEMPLATE_EXT.get(active_format or "", "")
        for folder in folders:
            if not folder.is_dir():
                continue
            if ext:
                for stem in stems:
                    path = folder / f"{stem}{ext}"
                    if path.is_file() and "sketch" not in path.stem.casefold():
                        return AssetLocation(
                            "file", module_dir, domain_slug, path=path.resolve()
                        )
                continue
            for stem in stems:
                for path in sorted(folder.glob(f"{stem}.*")):
                    if path.is_file() and "sketch" not in path.stem.casefold():
                        return AssetLocation(
                            "file", module_dir, domain_slug, path=path.resolve()
                        )
        return None


_YAML_FENCE = re.compile(r"```ya?ml\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def _load_yaml_mapping(body: str) -> dict[str, Any]:
    try:
        import yaml
    except ImportError:
        yaml = None
    loaded: Any
    if yaml is not None:
        loaded = yaml.safe_load(body)
    else:
        loaded = _load_yaml_pairs(body)
    return loaded if isinstance(loaded, dict) else {}


def _load_yaml_pairs(body: str) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line or line.startswith("- "):
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip("'\"")
    return fields


def yaml_fields(text: str) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for match in _YAML_FENCE.finditer(text):
        merged.update(_load_yaml_mapping(match.group(1)))
    return merged


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


def _matching_attr(host: Any, key: str) -> str | None:
    wanted = {
        key.casefold(),
        _to_snake(key).casefold(),
        key.replace(" ", "_").replace("-", "_").casefold(),
    }
    for name in dir(host):
        if name.startswith("_"):
            continue
        if name.casefold() not in wanted:
            continue
        member = getattr(type(host), name, None)
        if callable(member) and not isinstance(member, property):
            continue
        value = getattr(host, name, None)
        if callable(value) and not isinstance(member, property):
            continue
        return name
    return None


def _assign_yaml_value(host: Any, attr: str, value: Any) -> None:
    stored = attr
    descriptor = getattr(type(host), attr, None)
    if isinstance(descriptor, property) and descriptor.fset is None:
        stored = _to_snake(attr)
    if stored in {"applies_to", "appliesTo"} or attr in {"appliesTo", "applies_to"}:
        from actions.scan.rule import AppliesTo

        if not isinstance(value, AppliesTo):
            value = AppliesTo.from_value(value)
        stored = "applies_to"
    elif stored == "default_format" and isinstance(value, str):
        value = canonical_format(value.split()[0].strip("()`"))
    elif stored == "clean_engineering" and isinstance(value, str):
        value = value.split()[0].strip("()`").replace("-", "_")
    setattr(host, stored, value)


def bind_yaml(host: Any, text: str) -> None:
    for key, value in yaml_fields(text).items():
        attr = _matching_attr(host, key)
        if attr is None:
            continue
        _assign_yaml_value(host, attr, value)


class Markdown:
    def __init__(self, host: Any, label: str) -> None:
        self._host = host
        self._label = label

    @classmethod
    def from_label(cls, host: Any, label: str) -> Markdown:
        return cls(host, label)

    def raw(self) -> str:
        location = AssetLocator(self._host, self._label).locate()
        return _extract_location(location)

    def extract(self) -> str:
        text = self.raw()
        bind_yaml(self._host, text)
        return strip_yaml_fences(text)

    def html(self) -> HTML:
        return HTML.from_markdown(self.extract())

    def coerce(self, text: str, return_type: Any) -> Any:
        origin = get_origin(return_type) or return_type
        if return_type is HTML or origin is HTML:
            return HTML.from_markdown(text)
        if return_type is str or return_type is inspect.Signature.empty or return_type is None:
            return text
        if origin is dict:
            return _templates_path_map(self)
        from actions.scan.rule import RulesCollection

        if return_type is RulesCollection:
            return RulesCollection.from_markdown(text)
        from_markdown = getattr(return_type, "from_markdown", None)
        if callable(from_markdown):
            return from_markdown(text)
        return text


def _extract_location(location: AssetLocation) -> str:
    if location.kind == "file" and location.path is not None:
        if not location.path.is_file():
            return ""
        return location.path.read_text(encoding="utf-8")
    if location.kind == "folder" and location.folder is not None:
        if location.fidelity:
            for stem in _slug_variants(location.fidelity):
                for path in sorted(location.folder.glob(f"{stem}.*")):
                    if path.is_file() and "sketch" not in path.stem.casefold():
                        return path.read_text(encoding="utf-8")
            return ""
        return _merge_folder(location.folder)
    if location.kind == "section" and location.section_file is not None:
        heading = location.section_heading or ""
        if location.fidelity:
            return _read_fidelity_subsection(location.section_file, location.fidelity, heading)
        if heading and not _section_exists(location.section_file, heading):
            return ""
        return _read_section(location.section_file, heading)
    return ""


def _merge_folder(folder_path: Path) -> str:
    if not folder_path.is_dir():
        return ""
    parts: list[str] = []
    for path in sorted(folder_path.iterdir()):
        if path.name.startswith(".") or path.name == "__pycache__":
            continue
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            parts.append(f"## {path.stem}\n\n{text}")
        elif path.is_dir():
            nested = _merge_folder(path)
            if nested:
                parts.append(nested)
    return "\n\n".join(parts)


def _markdown_headings(content: str) -> list[tuple[int, int, int, str]]:
    headings: list[tuple[int, int, int, str]] = []
    offset = 0
    fence: str | None = None
    for line in content.splitlines(keepends=True):
        bare = line.rstrip("\r\n")
        fence_match = re.match(r"^\s*(```|~~~)", bare)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
        elif fence is None:
            heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", bare)
            if heading:
                headings.append(
                    (offset, offset + len(bare), len(heading.group(1)), heading.group(2))
                )
        offset += len(line)
    return headings


def _section_exists(file_path: Path, section_heading: str) -> bool:
    if not section_heading or not file_path.is_file():
        return True
    content = file_path.read_text(encoding="utf-8")
    wanted = section_heading.casefold()
    return any(heading.casefold() == wanted for _s, _e, _l, heading in _markdown_headings(content))


def _section_heading(label: str) -> str:
    if label.casefold() in {"context", "contexts", "overview"}:
        return "Overview"
    return label.replace("_", " ").replace("-", " ").title()


def _slice_heading(content: str, heading: str) -> str:
    if not heading:
        return content
    headings = _markdown_headings(content)
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
        len(content),
    )
    return content[start:end].strip()


def _child_blocks(text: str, parent_heading: str) -> list[tuple[str, str]]:
    headings = _markdown_headings(text)
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
    index, (_start, _heading_end, level, _name) = parent
    child_level = level + 1
    blocks: list[tuple[str, str]] = []
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
            len(text),
        )
        body = text[heading_end:end].lstrip("\r\n").strip()
        blocks.append((name, body))
    return blocks


def fidelity_blocks(text: str) -> list[tuple[str, str]]:
    return [
        (name, body)
        for name, body in _child_blocks(text, "Fidelities")
        if name.casefold() != "fidelities"
    ]


def fidelity_stage(body: str) -> str:
    stage = yaml_fields(body).get("stage")
    if isinstance(stage, str) and stage.strip():
        return stage.strip().strip("`")
    match = re.search(r"(?im)^\*\*Stage:\*\*\s*`?(\S+?)`?\s*$", body)
    if match:
        return match.group(1)
    match = re.search(r"(?im)^stage:\s*`?(\S+?)`?\s*$", body)
    return match.group(1) if match else ""


def _fidelity_labeled_line(body: str, label: str) -> str:
    match = re.search(
        rf"(?im)^\*\*{re.escape(label)}:\*\*\s*(.+?)\s*$",
        body,
    )
    return match.group(1).strip().strip("`") if match else ""


def fidelity_format(body: str) -> str:
    fields = yaml_fields(body)
    token = fields.get("default_format") or fields.get("defaultFormat")
    if isinstance(token, str) and token.strip():
        return canonical_format(token.split()[0].strip("()`"))
    rest = _fidelity_labeled_line(body, "Default format")
    if not rest:
        return ""
    return canonical_format(rest.split()[0].strip("()`"))


def fidelity_clean_engineering(body: str) -> str:
    fields = yaml_fields(body)
    token = fields.get("clean_engineering") or fields.get("cleanEngineering")
    if isinstance(token, str) and token.strip():
        return token.split()[0].strip("()`").replace("-", "_")
    rest = _fidelity_labeled_line(body, "Clean Engineering")
    if not rest:
        return ""
    return rest.split()[0].strip("()`").replace("-", "_")


def _read_fidelity_block(text: str, fidelity_name: str) -> str:
    wanted = fidelity_name.casefold()
    for name, body in fidelity_blocks(text):
        if name.casefold() == wanted:
            return body
    return ""


def _read_named_subsection(text: str, heading: str) -> str:
    return _slice_heading(text, heading)


def _read_fidelity_subsection(file_path: Path, fidelity_name: str, section_heading: str) -> str:
    if not file_path.is_file():
        return ""
    text = file_path.read_text(encoding="utf-8")
    block = _read_fidelity_block(text, fidelity_name)
    if not block:
        return ""
    named = _read_named_subsection(block, _section_heading(section_heading) if section_heading else "")
    if named:
        return named
    if _section_heading(section_heading).casefold() in {"rules", "shared rules"}:
        return ""
    return ""


def _read_section(file_path: Path, section_heading: str) -> str:
    if not file_path.is_file():
        return ""
    content = file_path.read_text(encoding="utf-8")
    if not section_heading:
        return content
    return _slice_heading(content, _section_heading(section_heading))


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
    """Resolve a host format or folder alias to the output-channel key."""
    if not name:
        return ""
    folded = name.casefold()
    return _FORMAT_ALIASES.get(folded, folded)


def _format_key_for_template(path: Path, templates_folder: Path) -> str:
    parts = path.relative_to(templates_folder).parts
    if len(parts) > 1:
        folder_key = _FORMAT_ALIASES.get(parts[0].casefold())
        if folder_key:
            return folder_key
    ext = path.suffix.lstrip(".").lower()
    return _EXT_TO_FORMAT.get(ext, ext)


def _templates_path_map(markdown: Markdown) -> dict[str, str]:
    class_dir = class_file_directory(markdown._host)
    folder = class_dir / "templates"
    mapping: dict[str, str] = {}
    if not folder.is_dir():
        return mapping
    for path in sorted(folder.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        rel = path.relative_to(class_dir).as_posix()
        key = _format_key_for_template(path, folder)
        if not key:
            continue
        mapping[key] = rel
    return mapping


_MARK_ATTRS = (
    "_skill",
    "_command",
    "_rules",
    "_mcp",
    "_hook",
    "_is_agent_instructions",
    "_is_agent_tool",
    "_skill_name",
    "_command_name",
    "_hook_name",
)


def _copy_marks(src: Any, dest: Any) -> None:
    for attr in _MARK_ATTRS:
        if hasattr(src, attr):
            setattr(dest, attr, getattr(src, attr))


def _markdown_property(fn: _F, prop_label: str) -> property:
    def getter(self: Any) -> Any:
        md = Markdown.from_label(self, prop_label)
        hints = {}
        try:
            hints = get_type_hints(fn, globalns=getattr(fn, "__globals__", None))
        except Exception:
            annot = getattr(fn, "__annotations__", {}) or {}
            hints = dict(annot)
        return_type = hints.get("return", str)
        raw = md.raw()
        bind_yaml(self, raw)
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
            return text
        result = md.coerce(raw, return_type)
        bind_yaml(result, raw)
        from actions.scan.rule import RulesCollection

        if isinstance(result, RulesCollection):
            class_dir = class_file_directory(self)
            for rule in result:
                rule.bind_scanner(class_dir)
        return result

    getter.__doc__ = fn.__doc__
    getter.__name__ = fn.__name__
    _copy_marks(fn, getter)
    return property(getter)


def markdown(
    fn: _F | str | None = None, *, label: str | None = None
) -> property | Callable[[_F], property]:
    if callable(fn):
        return _markdown_property(fn, fn.__name__)

    def decorator(inner: _F) -> property:
        prop_label = label or fn or inner.__name__
        return _markdown_property(inner, str(prop_label))

    return decorator
