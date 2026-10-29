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


def artboard(title: str, width: int, height: int, body: str, style: str, root_style: str, head: str = "",
             zoomable: bool = False) -> str:
    """A static ``.dc.html`` artboard: *body* absolutely placed inside a *width* × *height* root. A *zoomable* artboard
    zooms with a trackpad pinch (or ctrl + wheel) and its − / fit / + buttons."""
    if zoomable:
        return _zoomable_artboard(title, width, height, body, style, root_style, head)
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


ZOOM_BUTTON = ("font: 600 12px/1 ui-monospace, Consolas, monospace; padding: 6px 10px; border: 1px solid #2A2A2A; "
               "border-radius: 4px; background: #111113; color: #E8E8ED; cursor: pointer")


ZOOM_STEP = 5
# The canvas opens a linked artboard without the link's #hash, so a zoomable artboard also keeps the hash of a link
# clicked on it in local storage under this key plus the linked page; the linked artboard reads it from there.
LINK_KEY = "design-canvas.link:"
ZOOM_RANGE = range(20, 301, ZOOM_STEP)


def _zoomable_artboard(title: str, width: int, height: int, body: str, style: str, root_style: str, head: str) -> str:
    """The artboard fills its frame and scrolls; the map inside zooms with CSS ``zoom`` through one class per 5% step
    (the canvas fills holes in class names, not inside styles), so zooming never shrinks the frame."""
    zoom_classes = "".join(f".zoom-{level}{{zoom:{level / 100}}}" for level in ZOOM_RANGE)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{escape(title)}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>{head}<style>{style}{zoom_classes}</style></helmet>
<div style="position: relative; width: 100%; height: 100vh; overflow: auto; {root_style}">
<div class="{{{{zoomClass}}}}" style="position: relative; width: {width}px; height: {height}px">
{body}
</div>
</div>
<div style="position: fixed; top: 12px; right: 12px; display: flex; gap: 6px; z-index: 10">
<button type="button" style="{ZOOM_BUTTON}" onClick="{{{{zoomOut}}}}" aria-label="Zoom out">−</button>
<button type="button" style="{ZOOM_BUTTON}" onClick="{{{{zoomReset}}}}" aria-label="Actual size">{{{{zoomLabel}}}}</button>
<button type="button" style="{ZOOM_BUTTON}" onClick="{{{{zoomIn}}}}" aria-label="Zoom in">+</button>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{width},"height":{height}}}}}'>
const LINK_KEY = '{LINK_KEY}';
class Component extends DCLogic {{
componentDidMount() {{
this.keepLink = (event) => {{
const link = event.target && event.target.closest ? event.target.closest('a[href*="#"]') : null;
if (!link) return;
const [page, hash] = link.getAttribute('href').split('#');
try {{ window.localStorage.setItem(LINK_KEY + page, hash + '&at=' + Date.now()); }} catch (problem) {{ console.warn('canvas link target not kept', problem); }}
}};
document.addEventListener('click', this.keepLink, true);
this.pinch = (event) => {{
if (!event.ctrlKey) return;
event.preventDefault();
this.zoomTo(this.zoom() * Math.exp(-event.deltaY / 200));
}};
window.addEventListener('wheel', this.pinch, {{ passive: false }});
}}
componentWillUnmount() {{
document.removeEventListener('click', this.keepLink, true);
window.removeEventListener('wheel', this.pinch);
}}
zoom() {{
return (this.state && this.state.zoom) || 1;
}}
zoomTo(zoom) {{
this.setState({{ zoom: Math.min({ZOOM_RANGE[-1] / 100}, Math.max({ZOOM_RANGE[0] / 100}, zoom)) }});
}}
renderVals() {{
const zoom = this.zoom();
const level = Math.round(zoom * 100 / {ZOOM_STEP}) * {ZOOM_STEP};
return {{
zoomClass: 'zoom-' + level,
zoomLabel: level + '%',
zoomIn: () => this.zoomTo(zoom * 1.25),
zoomOut: () => this.zoomTo(zoom / 1.25),
zoomReset: () => this.zoomTo(1)
}};
}}
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
