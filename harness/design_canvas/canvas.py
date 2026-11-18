"""A Claude Design canvas as files: pages, boards, and the artboards they show.

Practices lay their own artboards out (the story map, the screens) and hand them to a ``DesignCanvas``; the canvas
owns ``canvas.json`` and where the files land: ``project/<artboard>`` beside ``project/canvas.json``.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, TypedDict

from harness.design_canvas.look import CardLook


PROJECT = "project"
# The date canvas.json gives for its files. It is fixed, so regenerating a canvas whose boards did not change writes
# the same canvas.json, and a version shows only the changes people or the generator made.
FILES_CREATED_AT = "2026-10-28T18:00:00Z"
# How round a card's corners are.
CARD_RADIUS = 6


class CanvasBoard(TypedDict, total=False):
    """Where canvas.json places one artboard: its place and size on the canvas, the page it is on, its title, and
    whether it runs and fills its frame."""

    x: int
    y: int
    w: int
    h: int
    page: str
    title: str
    is_interactive: bool
    expand: str


class DesignCanvas:
    """The pages, boards and artboard files of one Claude Design canvas, and the files its project folder already
    holds: the artboards people edited there, the stylesheets they link, and the images they show."""

    def __init__(self, title: str, project: Optional[Path] = None) -> None:
        self.title = title
        # The canvas's project folder (``<version>/project``) when it is already on disk; none for a canvas drawn fresh.
        self.project = Path(project) if project is not None else None
        self._pages: List[dict] = []
        self._boards: Dict[str, CanvasBoard] = {}
        self._order: List[str] = []
        self._files: Dict[str, str] = {}

    @property
    def launch_page(self) -> Optional[str]:
        return self._pages[0]["id"] if self._pages else None

    def add_page(self, page_id: str, name: str) -> None:
        self._pages.append({"id": page_id, "name": name})

    def add_board(self, name: str, board: CanvasBoard, text: Optional[str] = None) -> None:
        """Place artboard *name* (its path under ``project/``) on a page; *text* is its file when the canvas writes it."""
        self._boards[name] = board
        self._order.append(name)
        if text is not None:
            self._files[f"{PROJECT}/{name}"] = text

    def placed(self, name: str) -> CanvasBoard:
        """Where the canvas placed artboard *name*: its place and size, its page and its title."""
        return self._boards[name]

    def artboards_in(self, folder: str) -> List[str]:
        """The artboards already in folder of the project, as ``folder/<name>.dc.html``, in name order."""
        found = self.project / folder if self.project is not None else None
        if found is None or not found.is_dir():
            return []
        return [f"{folder}/{path.name}" for path in sorted(found.glob("*.dc.html"))]

    def holds(self, name: str) -> bool:
        """True when the project already holds the file name, a path under ``project/``."""
        return self.project is not None and (self.project / name).is_file()

    def size_of(self, name: str) -> Optional[int]:
        """The bytes in the project's file name; none when the project does not hold it."""
        return (self.project / name).stat().st_size if self.holds(name) else None

    def stylesheets_linked_by(self, names: List[str]) -> List[str]:
        """The stylesheets the project's artboards names link, each once, in the order they are first linked."""
        found: List[str] = []
        for name in names:
            if not self.holds(name):
                continue
            for href in re.findall(r'<link rel="stylesheet" href="([^"]+)"', (self.project / name).read_text(encoding="utf-8")):
                if href not in found:
                    found.append(href)
        return found

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
            "createdOnFiles": {"v": 1, "at": FILES_CREATED_AT},
            "title": self.title,
            "launch": {"view": "canvas", "page": self.launch_page},
            "pages": self._pages,
            "boards": self._boards,
            "order": self._order,
            "notes": {},
            "designSystems": [],
        }, indent=1, ensure_ascii=False)


def stem(path: str) -> str:
    """A canvas file name without its folder or its .dc.html ending: the name a dc-import uses."""
    return Path(path).name.removesuffix(".dc.html")


# A static artboard page: its body absolutely placed inside a root of its size.
_STATIC_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
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
# A pinch or ctrl + wheel of this many pixels zooms by a factor of e, so a trackpad pinch feels even at any zoom.
PINCH_PIXELS_PER_E = 200
# Each press of + or − zooms by this factor.
ZOOM_BUTTON_FACTOR = 1.25


# The − / fit / + buttons every zoomable artboard shows in its top right corner; fit shows the zoom it is at, and a press
# on it fits the whole artboard into its frame, or goes back to actual size once it already fits.
ZOOM_CONTROLS = f"""<div style="position: fixed; top: 12px; right: 12px; display: flex; gap: 6px; z-index: 10">
<button type="button" style="{ZOOM_BUTTON}" onClick="{{{{zoomOut}}}}" aria-label="Zoom out">−</button>
<button type="button" style="{ZOOM_BUTTON}" onClick="{{{{zoomFit}}}}" aria-label="Fit to window" title="Fit to window; press again for actual size">{{{{zoomLabel}}}}</button>
<button type="button" style="{ZOOM_BUTTON}" onClick="{{{{zoomIn}}}}" aria-label="Zoom in">+</button>
</div>
"""
# The script every zoomable artboard runs: it keeps the hash of a link clicked on it, zooms on a pinch, and answers the
# zoom class and label its buttons show.
ZOOM_COMPONENT = f"""const LINK_KEY = '{LINK_KEY}';
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
this.zoomTo(this.zoom() * Math.exp(-event.deltaY / {PINCH_PIXELS_PER_E}));
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
// The zoom that shows the whole artboard in its frame, never larger than actual size.
fitted() {{
return Math.min(1, Math.min(window.innerWidth / __WIDTH__, window.innerHeight / __HEIGHT__));
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
zoomIn: () => this.zoomTo(zoom * {ZOOM_BUTTON_FACTOR}),
zoomOut: () => this.zoomTo(zoom / {ZOOM_BUTTON_FACTOR}),
zoomFit: () => this.zoomTo(Math.abs(zoom - this.fitted()) < 0.01 ? 1 : this.fitted())
}};
}}
}}
"""


# A zoomable artboard page: it fills its frame and scrolls, and the map inside zooms with CSS ``zoom`` through one class
# per 5% step (the canvas fills holes in class names, not inside styles), so zooming never shrinks the frame.
_ZOOMABLE_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
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
{controls}</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{width},"height":{height}}}}}'>
{component}</script>
</body>
</html>
"""
_ZOOM_CLASSES = "".join(f".zoom-{level}{{zoom:{level / 100}}}" for level in ZOOM_RANGE)


class Artboard(NamedTuple):
    """A ``.dc.html`` artboard: *body* absolutely placed inside a *width* × *height* root, with its styles and what its
    head adds. A *zoomable* artboard zooms with a trackpad pinch (or ctrl + wheel) and its − / fit / + buttons."""

    title: str
    width: int
    height: int
    body: str
    style: str
    root_style: str
    head: str = ""
    zoomable: bool = False

    @property
    def text(self) -> str:
        """The artboard's file text."""
        fields = {**self._asdict(), "title": html.escape(self.title)}
        if self.zoomable:
            component = ZOOM_COMPONENT.replace("__WIDTH__", str(self.width)).replace("__HEIGHT__", str(self.height))
            return _ZOOMABLE_PAGE.format(**fields, zoom_classes=_ZOOM_CLASSES, controls=ZOOM_CONTROLS, component=component)
        return _STATIC_PAGE.format(**fields)


class Place(NamedTuple):
    """Where a card or a thumbnail sits on an artboard: its top left corner and its size, in pixels."""

    left: int
    top: int
    width: int
    height: int

    def card(self, look: CardLook, text: str, icon: str = "") -> str:
        """A labelled card here, drawn in *look* (fill, stroke, color, font, size, weight, extra css), with *icon* before
        its text."""
        return (f'<div style="position: absolute; left: {self.left}px; top: {self.top}px; width: {self.width}px; height: {self.height}px; '
                f'box-sizing: border-box; padding: 4px 8px; gap: 6px; display: flex; align-items: center; justify-content: center; '
                f'text-align: center; background: {look["fill"]}; border: 1px solid {look["stroke"]}; border-radius: {CARD_RADIUS}px; '
                f'font-family: {look["font"]}; font-size: {look["size"]}px; font-weight: {look["weight"]}; color: {look["color"]}; '
                f'{look["extra"]}">{icon}<span>{html.escape(text)}</span></div>')

    def thumbnail(self, caption: str, image: str, href: str) -> str:
        """A screen here at thumbnail size, captioned, that links to *href*; *image* is its screenshot, empty when there
        is none."""
        label = html.escape(caption)
        picture = (f'<img src="{image}" alt="{label}" style="display: block; width: 100%; height: 100%; object-fit: cover; object-position: top">' if image
                   else '<span style="display: flex; height: 100%; align-items: center; justify-content: center; color: #9B9BA8; font-size: 11px">No screenshot</span>')
        return (f'<a href="{href}" aria-label="{label}" style="position: absolute; left: {self.left}px; top: {self.top}px; display: block; '
                f'width: {self.width}px; height: {self.height}px; background: #111113; border: 1px solid #2A2A2A; '
                f'border-radius: 6px; overflow: hidden; box-sizing: border-box">{picture}</a>')
