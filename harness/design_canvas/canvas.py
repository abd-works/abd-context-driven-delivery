"""A Claude Design canvas as files: pages, boards, and the artboards they show.

Practices lay their own artboards out (the story map, the screens) and hand them to a ``DesignCanvas``; the canvas
owns ``canvas.json`` and where the files land: ``project/<artboard>`` beside ``project/canvas.json``.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Dict, List, Optional

PROJECT = "project"


class DesignCanvas:
    """The pages, boards and artboard files of one Claude Design canvas."""

    created_at = "2026-10-28T18:00:00Z"

    def __init__(self, title: str) -> None:
        self.title = title
        self._pages: List[dict] = []
        self._boards: Dict[str, dict] = {}
        self._order: List[str] = []
        self._files: Dict[str, str] = {}

    @property
    def launch_page(self) -> Optional[str]:
        return self._pages[0]["id"] if self._pages else None

    def add_page(self, page_id: str, name: str) -> None:
        self._pages.append({"id": page_id, "name": name})

    def add_board(self, name: str, board: dict, text: Optional[str] = None) -> None:
        """Place artboard *name* (its path under ``project/``) on a page; *text* is its file when the canvas writes it."""
        self._boards[name] = board
        self._order.append(name)
        if text is not None:
            self._files[f"{PROJECT}/{name}"] = text

    def files(self) -> Dict[str, str]:
        """Every file the canvas writes, ``canvas.json`` included, by path."""
        return {**self._files, f"{PROJECT}/canvas.json": self._canvas_json()}

    def write(self, root: str | Path) -> List[str]:
        """Write the files under *root* (the folder that holds ``project/``); returns the paths written."""
        written = []
        for path, text in self.files().items():
            target = Path(root) / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            written.append(path)
        return sorted(written)

    def _canvas_json(self) -> str:
        return json.dumps({
            "v": 3,
            "createdOnFiles": {"v": 1, "at": self.created_at},
            "title": self.title,
            "launch": {"view": "canvas", "page": self.launch_page},
            "pages": self._pages,
            "boards": self._boards,
            "order": self._order,
            "notes": {},
            "designSystems": [],
        }, indent=1, ensure_ascii=False)


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def stem(path: str) -> str:
    """A canvas file name without its folder or its .dc.html ending: the name a dc-import uses."""
    return Path(path).name.removesuffix(".dc.html")


def camel(name: str) -> str:
    head, *rest = name.split("-")
    return head + "".join(part.capitalize() for part in rest)


def artboard(title: str, width: int, height: int, body: str, style: str, root_style: str, head: str = "") -> str:
    """A static ``.dc.html`` artboard: *body* absolutely placed inside a *width* × *height* root."""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{escape(title)}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>{head}<style>{style}</style></helmet>
<div style="position: relative; width: {width}px; height: {height}px; {root_style}">
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{width},"height":{height}}}}}'>
class Component extends DCLogic {{
renderVals() {{ return {{}}; }}
}}
</script>
</body>
</html>
"""


def box(left, top, width, height, look: dict, text: str, radius: int = 6, icon: str = "") -> str:
    """A labelled card at an absolute place, drawn in *look* (fill, stroke, color, font, size, weight, extra css)."""
    return (f'<div style="position: absolute; left: {left}px; top: {top}px; width: {width}px; height: {height}px; '
            f'box-sizing: border-box; padding: 4px 8px; gap: 6px; display: flex; align-items: center; justify-content: center; '
            f'text-align: center; background: {look["fill"]}; border: 1px solid {look["stroke"]}; border-radius: {radius}px; '
            f'font-family: {look["font"]}; font-size: {look["size"]}px; font-weight: {look["weight"]}; color: {look["color"]}; '
            f'{look["extra"]}">{icon}<span>{escape(text)}</span></div>')


def thumbnail(left: int, top: int, width: int, height: int, caption: str, image: str, href: str) -> str:
    """A screen at thumbnail size that links to *href*."""
    picture = (f'<img src="{image}" alt="{escape(caption)}" style="display: block; width: 100%; height: 100%; object-fit: cover; object-position: top">' if image
               else '<span style="display: flex; height: 100%; align-items: center; justify-content: center; color: #9B9BA8; font-size: 11px">No screenshot</span>')
    return (f'<a href="{href}" aria-label="{escape(caption)}" style="position: absolute; left: {left}px; top: {top}px; display: block; '
            f'width: {width}px; height: {height}px; background: #111113; border: 1px solid #2A2A2A; '
            f'border-radius: 6px; overflow: hidden; box-sizing: border-box">{picture}</a>')
