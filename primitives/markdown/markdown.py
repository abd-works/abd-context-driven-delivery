"""Co-located markdown extract and HTML conversion — not assembly."""
from __future__ import annotations

import html
import inspect
import re
from pathlib import Path
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
    return Path(inspect.getfile(type(host))).resolve().parent


class Markdown:
    def __init__(self, host: Any, label: str) -> None:
        self._host = host
        self._label = label

    @classmethod
    def from_label(cls, host: Any, label: str) -> Markdown:
        return cls(host, label)

    def extract(self) -> str:
        location = AssetLocator(self._host, self._label).locate()
        text = _extract_location(location)
        if self._label in {"context", "contexts"}:
            text = _preamble_before_h2(text)
        return text

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


def _h2_blocks(text: str) -> list[tuple[str, str]]:
    pattern = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    blocks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((match.group(1).strip(), text[match.end() : end].strip()))
    return blocks


def fidelity_blocks(text: str) -> list[tuple[str, str]]:
    marker = re.search(r"^##\s+Fidelities\s*$", text, re.MULTILINE | re.IGNORECASE)
    if not marker:
        return []
    tail = text[marker.end() :]
    if not re.search(r"^##\s+", tail, re.MULTILINE):
        return []
    return [
        (name, body)
        for name, body in _h2_blocks(tail)
        if name.casefold() != "fidelities"
    ]


def _read_fidelity_block(text: str, fidelity_name: str) -> str:
    wanted = fidelity_name.casefold()
    for name, body in fidelity_blocks(text):
        if name.casefold() == wanted:
            return body
    return ""


def _read_named_subsection(text: str, heading: str) -> str:
    pattern = re.compile(rf"^###\s+{re.escape(heading)}\s*$", re.MULTILINE | re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        return ""
    rest = text[match.end() :]
    next_h = re.search(r"^###\s+\S", rest, re.MULTILINE)
    chunk = rest[: next_h.start()] if next_h else rest
    return chunk.strip()


def _read_fidelity_subsection(file_path: Path, fidelity_name: str, section_heading: str) -> str:
    if not file_path.is_file():
        return ""
    text = file_path.read_text(encoding="utf-8")
    block = _read_fidelity_block(text, fidelity_name)
    if not block:
        return ""
    named = _read_named_subsection(block, section_heading)
    return named or block


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


def _preamble_before_h2(text: str) -> str:
    match = re.search(r"^##\s+\S", text, re.MULTILINE)
    if not match:
        return text.strip()
    return text[: match.start()].strip()


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
        result = md.coerce(text, return_type)
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
