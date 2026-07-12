from __future__ import annotations

import re
from pathlib import Path

from .asset_location import AssetLocation


def read_file(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")


def _section_exists(file_path: Path, section_heading: str) -> bool:
    if not section_heading:
        return True
    content = read_file(file_path)
    pattern = re.compile(
        rf"^#{{1,6}}\s+{re.escape(section_heading)}\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    return pattern.search(content) is not None


def read_section(file_path: Path, section_heading: str) -> str:
    content = read_file(file_path)
    if not section_heading:
        return content
    pattern = re.compile(
        rf"^(#{{1,6}})\s+{re.escape(section_heading)}\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    match = pattern.search(content)
    if not match:
        return content
    level = len(match.group(1))
    start = match.start()
    rest = content[match.end() :]
    next_pattern = re.compile(rf"^#{{1,{level}}}\s+\S", re.MULTILINE)
    next_match = next_pattern.search(rest)
    end = match.end() + next_match.start() if next_match else len(content)
    return content[start:end].strip()


def merge_folder(folder_path: Path) -> str:
    if not folder_path.is_dir():
        return ""
    parts: list[str] = []
    for md_file in sorted(folder_path.glob("*.md")):
        parts.append(f"## {md_file.stem}\n\n{md_file.read_text(encoding='utf-8')}")
    if not parts:
        for child in sorted(path for path in folder_path.iterdir() if path.is_dir()):
            parts.append(child.name)
    return "\n\n".join(parts)


def collect_subsections(file_path: Path, section_heading: str) -> dict[str, str]:
    section_text = read_section(file_path, section_heading)
    pattern = re.compile(r"^(#{2,6})\s+(.+?)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(section_text))
    if not matches:
        return {section_heading: section_text}
    parent_level = len(matches[0].group(1))
    items: dict[str, str] = {}
    for index, match in enumerate(matches):
        level = len(match.group(1))
        if level <= parent_level and index > 0:
            continue
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


def merge_collection(items: dict[str, str]) -> str:
    return "\n\n".join(f"## {name}\n\n{content}" for name, content in items.items())


def extract_single(location: AssetLocation) -> str:
    if location.kind == "file" and location.path is not None:
        if not location.path.is_file():
            return ""
        return read_file(location.path)
    if location.kind == "folder" and location.folder is not None:
        return merge_folder(location.folder)
    if location.kind == "section" and location.section_file is not None:
        heading = location.section_heading or ""
        if heading and not _section_exists(location.section_file, heading):
            return ""
        return read_section(location.section_file, heading)
    return ""


def extract_collection(location: AssetLocation) -> dict[str, str]:
    if location.kind == "folder" and location.folder is not None:
        if not location.folder.is_dir():
            return {}
        return {
            path.name: read_file(path)
            for path in sorted(location.folder.iterdir())
            if path.is_file()
        }
    if location.kind == "file" and location.path is not None:
        if not location.path.is_file():
            return {}
        content = read_file(location.path)
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
        return collect_subsections(location.section_file, heading)
    return {}
