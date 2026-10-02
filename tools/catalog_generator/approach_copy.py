"""Load hand-editable approach page copy from markdown."""
from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_EMPHASIS = re.compile(r"\*([^*]+)\*")
_META = re.compile(r"^([a-z_]+):\s*(.*)$")
APPROACH_MARKDOWN = Path(__file__).resolve().parent / "markdown" / "cdd-approach.md"


@dataclass(frozen=True)
class ApproachCopy:
    subhead: str
    principles_heading: str
    library_heading: str
    stages: tuple[dict, ...]
    practices: tuple[dict, ...]


def inline_markdown_links(text: str) -> str:
    return _LINK.sub(r'<a href="\2">\1</a>', text)


def format_principle_bullet(text: str) -> str:
    escaped = html.escape(text)
    return _EMPHASIS.sub(r"<em>\1</em>", escaped)


def so_what_row(bullets: tuple[str, ...] | list[str], *, modifier: str = "") -> str:
    """Bold phrase over italic so-what; orange dots between columns."""
    parts: list[str] = []
    for index, item in enumerate(bullets):
        phrase, separator, why = item.partition(" | ")
        why_html = (
            f'<p class="approach-so__why">{format_principle_bullet(why)}</p>'
            if separator
            else ""
        )
        parts.append(
            '<li class="approach-so__item">'
            f'<p class="approach-so__phrase">{format_principle_bullet(phrase)}</p>'
            f"{why_html}</li>"
        )
        if index < len(bullets) - 1:
            parts.append(
                '<li class="approach-so__between" aria-hidden="true">'
                '<span class="approach-so__dot"></span></li>'
            )
    classes = "approach-so"
    if modifier:
        classes += f" {modifier}"
    return f'<ul class="{classes}">{"".join(parts)}</ul>'


def product_engineering_layout(bullets: tuple[str, ...] | list[str]) -> str:
    """Centered lead, three phrase/so-what columns, then a solo closing row."""
    if not bullets:
        return ""
    lead = (
        '<p class="approach-principle__lead approach-principle__lead--center">'
        f"{format_principle_bullet(bullets[0])}</p>"
    )
    rest = list(bullets[1:])
    parts: list[str] = ['<div class="approach-pe-intro">', lead]
    if len(rest) >= 3:
        parts.append(so_what_row(rest[:3], modifier="approach-so--pe-row"))
    if len(rest) > 3:
        parts.append(so_what_row(rest[3:], modifier="approach-so--solo"))
    elif rest:
        parts.append(so_what_row(rest, modifier="approach-so--solo"))
    parts.append("</div>")
    return "".join(parts)


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
                "example": meta.get("example", ""),
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
