"""Load hand-editable approach page copy from markdown."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_META = re.compile(r"^([a-z_]+):\s*(.*)$")


@dataclass(frozen=True)
class ApproachCopy:
    subhead: str
    principles_heading: str
    library_heading: str
    stages: tuple[dict, ...]
    practices: tuple[dict, ...]


def inline_markdown_links(text: str) -> str:
    return _LINK.sub(r'<a href="\2">\1</a>', text)


def load_approach_copy(path: str | Path) -> ApproachCopy:
    text = Path(path).read_text(encoding="utf-8")
    h2_parts = re.split(r"(?m)^## ", text)
    intro = h2_parts[0]
    subhead = re.sub(r"(?m)^#\s+Approach\s*", "", intro).strip()
    stages: tuple[dict, ...] = ()
    practices: tuple[dict, ...] = ()
    principles_heading = "Context Driven Delivery Practices"
    library_heading = ""
    for part in h2_parts[1:]:
        title, _, body = part.partition("\n")
        title = title.strip()
        if title == "Stages":
            stages = tuple(_parse_stages(body))
        elif title == "Library":
            library_heading = body.strip()
        else:
            principles_heading = title
            practices = tuple(_parse_practices(body))
    return ApproachCopy(
        subhead=subhead,
        principles_heading=principles_heading,
        library_heading=library_heading,
        stages=stages,
        practices=practices,
    )


def _parse_stages(body: str) -> list[dict]:
    stages: list[dict] = []
    for title, rest in _h3_chunks(body):
        meta, remainder = _take_meta(rest)
        items = tuple(
            item.strip() for item in meta.get("items", "").split("|") if item.strip()
        )
        paras = tuple(p.strip() for p in re.split(r"\n\s*\n", remainder) if p.strip())
        stages.append(
            {
                "id": meta.get("id", _slug(title)),
                "label": title,
                "detail_title": title,
                "items": items,
                "item_fams": ("sdd", "uxd", "arc"),
                "shape": meta.get("shape", "square"),
                "scope_name": meta.get("scope_name", title),
                "scope_width": meta.get("scope_width", ""),
                "paras": paras,
                "board_key": meta.get("board_key", ""),
            }
        )
    return stages


def _parse_practices(body: str) -> list[dict]:
    practices: list[dict] = []
    for title, rest in _h3_chunks(body):
        meta, remainder = _take_meta(rest)
        bullets, caption = _bullets_and_caption(remainder)
        caption_html = inline_markdown_links(caption) if caption else ""
        paras = bullets + ((caption_html,) if caption_html else ())
        practices.append(
            {
                "slug": meta.get("slug", _slug(title)),
                "title": title,
                "kind": meta.get("kind", "tickets"),
                "summary": bullets[0] if bullets else "",
                "bullets": bullets,
                "paras": paras,
                "caption": caption_html,
            }
        )
    return practices


def _h3_chunks(body: str) -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []
    for chunk in re.split(r"(?m)^### ", body):
        if not chunk.strip():
            continue
        title, _, rest = chunk.partition("\n")
        chunks.append((title.strip(), rest))
    return chunks


def _take_meta(text: str) -> tuple[dict[str, str], str]:
    meta: dict[str, str] = {}
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            index += 1
            if meta:
                break
            continue
        match = _META.match(stripped)
        if match:
            meta[match.group(1)] = match.group(2).strip()
            index += 1
            continue
        break
    remainder = "\n".join(lines[index:]).strip()
    return meta, remainder


def _bullets_and_caption(text: str) -> tuple[tuple[str, ...], str]:
    bullets: list[str] = []
    leftover: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
        else:
            leftover.append(line)
    caption = "\n".join(leftover).strip()
    return tuple(bullets), caption


def _slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
