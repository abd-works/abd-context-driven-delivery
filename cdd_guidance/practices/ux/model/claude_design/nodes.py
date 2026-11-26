"""Claude Design screens: the prototype screens laid out on the canvas's screens page.

A mockup rendered to Claude Design is one prototype page for each screen (``screens/<slug>.dc.html``), each a page the
HTML format reads, and ``canvas.json`` placing one board for each page on a canvas page of its own. Reading the canvas
back reads each board's page and joins their screens into one UX map, so a mockup goes to Claude Design and back whole.

A screen's ``prototype`` is a ``.dc.html`` artboard the canvas owns, such as a product screen ported by the agent; the
story canvas places it and never rewrites it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from cdd_guidance.practices.ux.model.html.nodes import HtmlUxMap
from cdd_guidance.practices.ux.model.json.nodes import JsonUxMap
from cdd_guidance.practices.ux.model.nodes import Screen
from cdd_guidance.practices.ux.model.ux_map import UxMap
from harness.design_canvas.canvas import PROJECT, CanvasBoard, DesignCanvas
from harness.guidance.practice_formats import TextOrData, Written


PAGE_ID_LENGTH = 40
"""The longest page id the canvas keeps; a screen's page id is cut to it."""
CANVAS_FILE = f"{PROJECT}/canvas.json"
"""Where a canvas version keeps the file that places its boards."""

CanvasFiles = Dict[str, str]
"""A canvas version's files, each by its path in the version's folder, such as ``project/canvas.json``."""


class NotAClaudeDesignCanvas(ValueError):
    """The text read as a canvas is not a canvas.json: it places no boards."""

    def __init__(self, text: str) -> None:
        super().__init__(f"This is not a Claude Design canvas.json, which places its boards under \"boards\": {text[:80]!r}")
        self.text = text


class ClaudeDesignScreenMissing(LookupError):
    """canvas.json places a screen's board, and the canvas holds no prototype page for it to read the screen from."""

    def __init__(self, page: str) -> None:
        super().__init__(f"The canvas places the screen {page} and holds no prototype page for it; render the mockup to claude_design again to write it")
        self.page = page


class ClaudeDesignUxMap(UxMap):
    """Screen boards: each prototype screen on its own canvas page, as a plain frame (not a full-window page) sized for
    a desktop screen, so the editor stays around it. The story explorer keeps the ``screens`` page."""

    folder = "screens"
    page = "screens"
    width = 1600
    height = 1100

    def render(self, canonical: UxMap, written: Written = Written()) -> CanvasFiles:
        """canonical as a canvas: copied into a Claude Design map, which writes its own files."""
        return self.copy_of(canonical).files()

    def files(self) -> CanvasFiles:
        """The canvas of this map's screens: one prototype page for each screen, the HTML mockup of that screen, and
        canvas.json placing each on a canvas page of its own, in screen order."""
        canvas = DesignCanvas(self.scope or self.name)
        document = JsonUxMap.create().copy_of(self).document()
        for index, screen in enumerate(self.screens):
            name = self._page_name(screen)
            canvas.add_page(self.page_of(name), screen.name)
            canvas.place(name, self._board_of(name, screen.name), self._prototype_page(document, index))
        return canvas.files()

    def _page_name(self, screen: Screen) -> str:
        """The prototype page a mockup's screen is written to on the canvas: ``screens/<slug>.dc.html``."""
        return f"{self.folder}/{screen.slug}.dc.html"

    def _prototype_page(self, document: Dict[str, Any], index: int) -> str:
        """The HTML mockup of the screen at index: the map's own fields, transitions, content types and navigation, the
        screen whole and first, so the page opens on it, and every other screen by its name alone, so each link the
        screen makes to another reads back."""
        screens = document["screens"]
        named = [{"name": other["name"], "slug": other["slug"]} for place, other in enumerate(screens) if place != index]
        return HtmlUxMap.from_document({**document, "screens": [screens[index], *named]}).save()

    def parse(self, text: TextOrData, file: str = "") -> UxMap:
        """The mockup a canvas holds: each screen read from the prototype page canvas.json places for it, in the order
        the canvas places them, and the map's own fields, transitions, content types and navigation from the first
        page. text is the canvas's files by path in its version's folder, or canvas.json alone, which reads back only
        a canvas that places no screen. A screen whose page the canvas does not hold is refused
        (*ClaudeDesignScreenMissing*)."""
        files = text if isinstance(text, dict) else {CANVAS_FILE: text or ""}
        documents = [self._page_document(files, name) for name in self._placed_screens(files.get(CANVAS_FILE, ""))]
        joined = {**documents[0], "screens": [document["screens"][0] for document in documents]} if documents else {}
        return self.copy_of(JsonUxMap.from_document(joined))

    def _placed_screens(self, canvas_json: str) -> List[str]:
        """The prototype pages canvas.json places, in the order it places them."""
        try:
            canvas = json.loads(canvas_json)
        except json.JSONDecodeError as refused:
            raise NotAClaudeDesignCanvas(canvas_json) from refused
        if not isinstance(canvas, dict) or "boards" not in canvas:
            raise NotAClaudeDesignCanvas(canvas_json)
        order = canvas.get("order") or list(canvas["boards"])
        return [name for name in order if name.startswith(f"{self.folder}/")]

    def _page_document(self, files: CanvasFiles, name: str) -> Dict[str, Any]:
        page = files.get(f"{PROJECT}/{name}")
        if page is None:
            raise ClaudeDesignScreenMissing(name)
        return HtmlUxMap.create().carried_document(page)

    def content_beside(self, canvas_json: Path) -> CanvasFiles:
        """canvas.json at canvas_json, or in the project folder canvas_json names, and each prototype page in that
        folder, by path in the version's folder."""
        if canvas_json.is_dir():
            canvas_json = canvas_json / Path(CANVAS_FILE).name
        project = canvas_json.parent
        found = {CANVAS_FILE: canvas_json.read_text(encoding="utf-8")}
        for page in sorted(project.glob(f"{self.folder}/*.dc.html")):
            found[f"{PROJECT}/{page.relative_to(project).as_posix()}"] = page.read_text(encoding="utf-8")
        return found

    def reads_file(self, file: Path, text: str) -> bool:
        """Whether file is one a mockup render writes: a prototype page the HTML format reads, or a canvas.json that
        places only such pages. A screen people ported to the canvas, or a story canvas's canvas.json, is not."""
        if file.name.endswith(".dc.html"):
            return HtmlUxMap.create().reads_file(file, text)
        try:
            boards = json.loads(text).get("boards", {})
        except (json.JSONDecodeError, AttributeError):
            return False
        return all(name.startswith(f"{self.folder}/") for name in boards)

    def prototype_names(self) -> List[str]:
        """Each prototype this map's screens name once, in screen order, at its path on the canvas."""
        found: List[str] = []
        for screen in self.screens:
            if screen.prototype:
                name = f"{self.folder}/{Path(screen.prototype).name}"
                if name not in found:
                    found.append(name)
        return found

    def names(self, files: Iterable[str] = ()) -> List[str]:
        """The prototypes the screens name, then any other screen artboard already in the folder (*files*)."""
        names = self.prototype_names()
        return names + [name for name in files if name not in names]

    def title(self, name: str) -> str:
        return Path(name).name.removesuffix(".dc.html").replace("-", " ").capitalize()

    def page_of(self, name: str) -> str:
        """Each screen's own canvas page: the editor shows it alone there, so leaving Play lands on it to edit."""
        return ("screen-" + Path(name).name.removesuffix(".dc.html"))[:PAGE_ID_LENGTH]

    # Claude Design keeps at most this many pages on a canvas; a board on a page it does not keep falls back onto the
    # first page, on top of what is there.
    max_pages = 40
    shared_page = "screen-boards"
    shared_columns = 4
    # Room beside each screen on the shared page for the story panel a story canvas puts there.
    beside_room = 760
    shared_gap = 160

    def shares_a_page(self, files: Iterable[str] = (), reserved: int = 0) -> bool:
        """Whether the screens are too many for a page each beside the reserved pages, so they share one page."""
        return len(self.names(files)) + reserved > self.max_pages

    def pages(self, files: Iterable[str] = (), reserved: int = 0) -> List[dict]:
        """A page per screen; one page the screens share when a page each would pass the canvas's limit."""
        if self.shares_a_page(files, reserved):
            return [{"id": self.shared_page, "name": "Screens"}]
        return [{"id": self.page_of(name), "name": self.title(name)} for name in self.names(files)]

    def _board_of(self, name: str, title: str) -> CanvasBoard:
        """The board of the screen artboard name, titled title: alone on its own page at a desktop size."""
        return {"x": 0, "y": 0, "w": self.width, "h": self.height, "page": self.page_of(name), "title": title,
                "is_interactive": True}

    def _shared_board_of(self, name: str, title: str, place: int) -> CanvasBoard:
        """The board of the screen artboard name at place on the shared page: in rows, with room beside it."""
        column, row = place % self.shared_columns, place // self.shared_columns
        return {"x": column * (self.width + self.beside_room), "y": row * (self.height + self.shared_gap), "w": self.width,
                "h": self.height, "page": self.shared_page, "title": title, "is_interactive": True}

    def boards(self, files: Iterable[str] = (), reserved: int = 0) -> Dict[str, CanvasBoard]:
        """One board per prototype screen: alone on its own page at a desktop size, or in rows on the shared page when
        the screens share one."""
        names = self.names(files)
        if self.shares_a_page(files, reserved):
            return {name: self._shared_board_of(name, self.title(name), place) for place, name in enumerate(names)}
        return {name: self._board_of(name, self.title(name)) for name in names}
