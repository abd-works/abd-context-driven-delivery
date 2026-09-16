"""Co-located markdown extract and HTML conversion — not assembly."""
from __future__ import annotations

import html
import inspect
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, TypeVar, get_args, get_origin, get_type_hints

from primitives.assets import AssetLocation, AssetLocator

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
            items = "".join(
                f"<li>{html.escape(re.sub(r'^\\s*[-*]\\s+', '', line))}</li>"
                for line in lines
            )
            chunks.append(f"<ul>{items}</ul>")
        else:
            chunks.append(f"<p>{html.escape(block)}</p>")
    return "\n".join(chunks)


def class_file_directory(host: Any) -> Path:
    return Path(inspect.getfile(type(host))).resolve().parent


class Markdown:
    def __init__(self, host: Any, label: str) -> None:
        self._host = host
        self._label = label

    @classmethod
    def from_label(cls, host: Any, label: str) -> Markdown:
        return cls(host, label)

    def extract(self) -> str:
        host = self._host
        class_dir = class_file_directory(host)
        name = getattr(host, "name", None)
        locator_host = _locator_host(host, class_dir, name)
        location = AssetLocator(locator_host, self._label).locate()
        return _extract_location(location)

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
        from_markdown = getattr(return_type, "from_markdown", None)
        if callable(from_markdown):
            return from_markdown(text)
        return text


def _locator_host(host: Any, class_dir: Path, name: Any) -> SimpleNamespace:
    domain_slug = (
        getattr(host, "domain_slug", None)
        or getattr(host, "toolset_name", None)
        or name
        or class_dir.name
    )
    adapter = SimpleNamespace(
        module_dir=class_dir,
        domain_slug=domain_slug,
        name=name,
        format=getattr(host, "format", None),
        fidelity=getattr(host, "fidelity", None),
    )
    return adapter


def _extract_location(location: AssetLocation) -> str:
    if location.kind == "file" and location.path is not None:
        if not location.path.is_file():
            return ""
        return location.path.read_text(encoding="utf-8")
    if location.kind == "folder" and location.folder is not None:
        return _merge_folder(location.folder)
    if location.kind == "section" and location.section_file is not None:
        heading = location.section_heading or ""
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


def _read_section(file_path: Path, section_heading: str) -> str:
    if not file_path.is_file():
        return ""
    content = file_path.read_text(encoding="utf-8")
    if not section_heading:
        return content
    headings = _markdown_headings(content)
    found = next(
        (
            (index, item)
            for index, item in enumerate(headings)
            if item[3].casefold() == section_heading.casefold()
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
    body = content[start:end]
    # Drop the heading line; callers want the section body.
    newline = body.find("\n")
    if newline >= 0:
        body = body[newline + 1 :]
    return body.strip()


def _templates_path_map(markdown: Markdown) -> dict[str, str]:
    class_dir = class_file_directory(markdown._host)
    folder = class_dir / "templates"
    mapping: dict[str, str] = {}
    if not folder.is_dir():
        return mapping
    domain = getattr(markdown._host, "domain_slug", None) or class_dir.name
    for path in sorted(folder.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        rel = path.relative_to(class_dir).as_posix()
        stem = path.stem
        key = stem
        prefix = f"{domain}-"
        if stem.startswith(prefix):
            key = stem[len(prefix) :]
        mapping[key] = rel
        mapping[stem] = rel
        mapping[path.suffix.lstrip(".")] = rel
    return mapping


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
        text = md.extract()
        if return_type is HTML:
            return md.html()
        origin = get_origin(return_type)
        if origin is not None:
            args = get_args(return_type)
            if origin is dict:
                return md.coerce(text, return_type)
            if args and args[0] is HTML:
                return md.html()
        return md.coerce(text, return_type)

    getter.__doc__ = fn.__doc__
    getter.__name__ = fn.__name__
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
