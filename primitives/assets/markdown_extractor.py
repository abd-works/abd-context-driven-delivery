"""Markdown extraction helpers for asset collection.
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""
from __future__ import annotations

import re
from pathlib import Path

from .assets import AssetLocation


def _read_file(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")


def _markdown_headings(content: str) -> list[tuple[int, int, int, str]]:
    """Headings with offsets, excluding heading-looking lines in fenced code."""
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
    if not section_heading:
        return True
    content = _read_file(file_path)
    return any(
        heading.casefold() == section_heading.casefold()
        for _start, _end, _level, heading in _markdown_headings(content)
    )


def _read_section(file_path: Path, section_heading: str) -> str:
    content = _read_file(file_path)
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
        return content
    index, (start, _heading_end, level, _heading) = found
    end = next(
        (position for position, _e, next_level, _h in headings[index + 1 :] if next_level <= level),
        len(content),
    )
    return content[start:end].strip()


def _merge_folder(
    folder_path: Path,
    fidelity: str | None = None,
    *,
    _root: Path | None = None,
) -> str:
    from .assets import keep_template_file

    if not folder_path.is_dir():
        return ""
    root = _root or folder_path
    parts: list[str] = []
    for path in sorted(folder_path.iterdir()):
        if path.name.startswith(".") or path.name == "__pycache__":
            continue
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(root).as_posix()
            if not keep_template_file(rel, text, fidelity):
                continue
            parts.append(f"## {path.stem}\n\n{text}")
        elif path.is_dir():
            nested = _merge_folder(path, fidelity, _root=root)
            if nested:
                parts.append(nested)
    return "\n\n".join(parts)


def _collect_subsections(file_path: Path, section_heading: str) -> dict[str, str]:
    section_text = _read_section(file_path, section_heading)
    parent_heading = re.match(r"^(#{1,6})\s+", section_text)
    parent_level = len(parent_heading.group(1)) if parent_heading else 0
    pattern = re.compile(r"^(#{2,6})\s+(.+?)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(section_text))
    if not matches:
        return {section_heading: section_text}
    items: dict[str, str] = {}
    for match in matches:
        level = len(match.group(1))
        if level != parent_level + 1:
            continue
        name = match.group(2).strip()
        start = match.start()
        rest = section_text[match.end() :]
        next_pattern = re.compile(rf"^#{{{1},{level}}}\s+\S", re.MULTILINE)
        next_match = next_pattern.search(rest)
        end = match.end() + next_match.start() if next_match else len(section_text)
        items[name] = section_text[start:end].strip()
    return items


def _merge_collection(items: dict[str, str]) -> str:
    return "\n\n".join(f"## {name}\n\n{content}" for name, content in items.items())


def _extract_single(location: AssetLocation) -> str:
    if location.kind == "file" and location.path is not None:
        if not location.path.is_file():
            return ""
        return _read_file(location.path)
    if location.kind == "folder" and location.folder is not None:
        return _merge_folder(location.folder, location.fidelity)
    if location.kind == "section" and location.section_file is not None:
        heading = location.section_heading or ""
        if heading and not _section_exists(location.section_file, heading):
            return ""
        return _read_section(location.section_file, heading)
    return ""


def _h2_block(text: str, heading: str) -> str:
    """Return the ``## heading`` block through the next ``#`` / ``##``, or empty."""
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.start()
    rest = text[match.end() :]
    next_match = re.compile(r"^#{1,2}\s+\S", re.MULTILINE).search(rest)
    end = match.end() + next_match.start() if next_match else len(text)
    return text[start:end].strip()


def _contexts_preamble(text: str) -> str:
    """Text from the start of ``# Contexts`` through the first ``##`` heading."""
    match = re.compile(r"^##\s+\S", re.MULTILINE).search(text)
    if not match:
        return text.strip()
    return text[: match.start()].rstrip()


# H2 titles that name a kit fidelity. Sibling sections drop; Shared rules /
# Language companion / Hierarchy shape stay. Same rule for Stories, CE, DDD, UX, BDD.
_FIDELITY_H2_NAMES = frozenset(
    {
        "scaffold",
        "story_map",
        "scenarios",
        "acceptance_tests",
        "modules",
        "model",
        "code",
        "specification",
        "behavior",
        "development",
        "bounded_context",
        "building_blocks",
        "tactics",
        "ia",
        "mockup",
        "front_end_code",
    }
)


def _h2_slug(heading: str) -> str:
    cleaned = re.sub(r"<!--.*?-->", "", heading).strip()
    return cleaned.lower().replace(" ", "_").replace("-", "_")


def _iter_h2_blocks(text: str) -> list[tuple[str, str]]:
    headings = _markdown_headings(text)
    blocks: list[tuple[str, str]] = []
    for index, (start, _end, level, heading) in enumerate(headings):
        if level != 2:
            continue
        end = next(
            (
                position
                for position, _e, next_level, _h in headings[index + 1 :]
                if next_level <= level
            ),
            len(text),
        )
        blocks.append((heading.strip(), text[start:end].strip()))
    return blocks


def thin_contexts_for_fidelity(text: str, fidelity: str | None) -> str:
    """Keep preamble + shared H2s + ``## {fidelity}`` when that heading exists.

    Drops sibling fidelity H2s (``## model`` when fidelity is ``modules``, etc.).
    Unset fidelity, or a kit with no matching ``## {fidelity}``, leaves ``text``
    unchanged. Does not require ``## Shared rules``.
    """
    if not fidelity or not str(fidelity).strip():
        return text
    name = str(fidelity).strip()
    blocks = _iter_h2_blocks(text)
    if not any(_h2_slug(heading) == name for heading, _ in blocks):
        return text
    parts = [_contexts_preamble(text)]
    for heading, block in blocks:
        slug = _h2_slug(heading)
        if slug in _FIDELITY_H2_NAMES and slug != name:
            continue
        parts.append(block)
    return "\n\n".join(part for part in parts if part).strip()


_FORMAT_FOLDER_ALIAS = {
    "markdown": "md",
    "python": "py",
    "typescript": "ts",
    "javascript": "js",
    "java": "java",
}


_FORMAT_FILE_EXT = {
    "markdown": ".md",
    "python": ".py",
    "typescript": ".ts",
    "javascript": ".js",
    "java": ".java",
    "drawio": ".drawio",
}


def thin_examples_by_format(items: dict[str, str], format_name: str | None) -> dict[str, str]:
    """Keep example files for the active format.

    Prefer ``/{alias}/`` paths (Stories). If none, keep by suffix (CE shopping-cart
    ``examples.md`` / ``examples.py``). ``examples.md`` is skipped only as a
    folder-index next to ``/{alias}/`` trees.
    """
    if not format_name or not str(format_name).strip():
        return items
    alias = _FORMAT_FOLDER_ALIAS.get(str(format_name).strip(), str(format_name).strip())
    needle = f"/{alias}/"
    filtered: dict[str, str] = {}
    for rel, content in items.items():
        posix = rel.replace("\\", "/")
        name = posix.rsplit("/", 1)[-1]
        if name.lower() == "examples.md":
            continue
        if needle in f"/{posix}":
            filtered[rel] = content
    if filtered:
        return filtered
    ext = _FORMAT_FILE_EXT.get(str(format_name).strip())
    if not ext:
        return items
    by_ext: dict[str, str] = {}
    for rel, content in items.items():
        if Path(rel.replace("\\", "/")).suffix.lower() == ext:
            by_ext[rel] = content
    return by_ext if by_ext else items


_STORY_MAP_EXAMPLE_STEMS = frozenset({"story-map"})
_CE_GENERATE_FIDELITIES = frozenset({"modules", "model", "code", "specification"})


def thin_examples_by_fidelity(
    items: dict[str, str], fidelity: str | None
) -> dict[str, str]:
    """Keep example files whose stem matches the active fidelity.

    ``story_map`` → ``story-map`` only. ``scenarios`` → ``scenario-*``.
    CE generate fidelities (``modules`` / ``model`` / ``code``) drop ``evals/``
    (repair fixtures) and keep shopping-cart. Unset fidelity, or no matching
    names, leaves ``items`` unchanged so we never empty the slot.
    """
    if not items or not fidelity or not str(fidelity).strip():
        return items
    name = str(fidelity).strip()
    filtered: dict[str, str] = {}
    for rel, content in items.items():
        posix = rel.replace("\\", "/")
        stem = Path(posix).stem
        if name == "story_map" and stem in _STORY_MAP_EXAMPLE_STEMS:
            filtered[rel] = content
        elif name == "scenarios" and stem.startswith("scenario"):
            filtered[rel] = content
        elif name in _CE_GENERATE_FIDELITIES:
            if "/evals/" in f"/{posix}" or posix.startswith("evals/"):
                continue
            filtered[rel] = content
    return filtered if filtered else items


def _extract_collection(location: AssetLocation) -> dict[str, str]:
    if location.kind == "folder" and location.folder is not None:
        if not location.folder.is_dir():
            return {}
        items: dict[str, str] = {}
        for path in sorted(location.folder.rglob("*")):
            if not path.is_file():
                continue
            if path.name.startswith(".") or "__pycache__" in path.parts:
                continue
            rel = path.relative_to(location.folder).as_posix()
            content = _read_file(path)
            from .assets import keep_template_file

            if not keep_template_file(rel, content, location.fidelity):
                continue
            items[rel] = content
        return items
    if location.kind == "file" and location.path is not None:
        if not location.path.is_file():
            return {}
        content = _read_file(location.path)
        pattern = re.compile(r"^(#)\s+(.+?)\s*$", re.MULTILINE)
        matches = list(pattern.finditer(content))
        if not matches:
            return {location.path.stem: content}
        items: dict[str, str] = {}
        for index, match in enumerate(matches):
            name = match.group(2).strip()
            start = match.start()
            rest = content[match.end() :]
            next_match = pattern.search(rest)
            end = match.end() + next_match.start() if next_match else len(content)
            items[name] = content[start:end].strip()
        return items
    if location.kind == "section" and location.section_file is not None:
        heading = location.section_heading or ""
        if heading and not _section_exists(location.section_file, heading):
            return {}
        return _collect_subsections(location.section_file, heading)
    return {}
