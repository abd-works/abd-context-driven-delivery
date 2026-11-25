"""A screen's artboard on a story canvas (``project/screens/<slug>.dc.html``), read for the UX graph rules: whether it
is a ported prototype or only a picture, the props it declares and the ones its logic reads, and the scenarios it
names. The canvas a UX map's screens are ported to is found from the map's own file (*PortedCanvas*)."""

from __future__ import annotations

import html
import json
import re
from functools import cached_property
from pathlib import Path
from typing import Optional

from harness.design_canvas.versions import CanvasVersions

# What draws a picture: an image, or a background image.
_PICTURE = re.compile(r"<img\b|background(?:-image)?\s*:[^;\"']*url\(", re.IGNORECASE)
# What a screen that works has besides pictures: components, other artboards, and controls a person uses.
_WORKING = re.compile(r"<(?:x-import|dc-import|input|button|select|textarea|a)\b", re.IGNORECASE)
_LOGIC = re.compile(r"<script\b([^>]*\btype=\"text/x-dc\"[^>]*)>([\s\S]*?)</script>")
_DATA_PROPS = re.compile(r"data-props='([^']*)'")
# Where a story canvas keeps its versions, beside the UX map it ports.
_CANVAS_FILE = "canvas.json"
_PROJECT = "project"


class ScreenArtboard:
    """One artboard's text, read as the canvas runs it."""

    def __init__(self, text: str) -> None:
        self.text = text

    @classmethod
    def at(cls, path: Path) -> "ScreenArtboard":
        return cls(path.read_text(encoding="utf-8", errors="replace"))

    @cached_property
    def template(self) -> str:
        """The x-dc template the canvas draws, without its helmet and comments."""
        opened, closed = self.text.find("<x-dc>"), self.text.rfind("</x-dc>")
        inner = self.text[opened + len("<x-dc>"):closed] if 0 <= opened < closed else ""
        return re.sub(r"<!--[\s\S]*?-->", "", re.sub(r"<helmet>[\s\S]*?</helmet>", "", inner))

    @cached_property
    def logic(self) -> str:
        """The DCLogic script the canvas runs the template with."""
        found = _LOGIC.search(self.text)
        return found.group(2) if found else ""

    @cached_property
    def declared_props(self) -> set[str]:
        """The props its data-props declares, which the explorer and the editor hand it."""
        return set(self._data_props)

    @cached_property
    def preview_size(self) -> Optional[tuple[int, int]]:
        """The screen's own width and height, as its data-props' ``$preview`` states them; none when it states none."""
        preview = self._data_props.get("$preview")
        if not isinstance(preview, dict):
            return None
        width, height = preview.get("width"), preview.get("height")
        return (width, height) if isinstance(width, int) and isinstance(height, int) else None

    @cached_property
    def _data_props(self) -> dict:
        found = _LOGIC.search(self.text)
        declared = _DATA_PROPS.search(found.group(1)) if found else None
        if declared is None:
            return {}
        try:
            props = json.loads(html.unescape(declared.group(1)))
        except json.JSONDecodeError:
            return {}
        return props if isinstance(props, dict) else {}

    @property
    def shows_only_a_picture(self) -> bool:
        """Whether it shows a screenshot and nothing that works: no component, no other artboard, no control, and no
        text of its own."""
        words = html.unescape(re.sub(r"\{\{[^}]*\}\}", " ", re.sub(r"<[^>]+>", " ", self.template))).strip()
        return bool(_PICTURE.search(self.template)) and not _WORKING.search(self.template) and not words

    def reads_prop(self, name: str) -> bool:
        """Whether its logic reads the prop name: ``props.name``, ``props['name']``, or taken apart from the props."""
        if re.search(rf"\bprops\s*(?:\.\s*{re.escape(name)}\b|\[\s*['\"]{re.escape(name)}['\"]\s*\])", self.logic):
            return True
        return any(re.search(rf"\b{re.escape(name)}\b", taken.group(1))
                   for taken in re.finditer(r"\{([^{}]*)\}\s*=\s*(?:this\.)?props\b", self.logic))

    def names(self, text: str) -> bool:
        """Whether it names text, as written, as a JavaScript string writes it, or as HTML writes it."""
        return any(form in self.text for form in (text, json.dumps(text, ensure_ascii=False)[1:-1], html.escape(text)))

    @property
    def loads_fixtures(self) -> bool:
        """Whether it builds its states from the stories' fixtures (``fromFixture``), so every scenario the fixtures
        bundle holds loads on it."""
        return "fromFixture(" in self.logic


class PortedCanvas:
    """The project folder of the canvas version a UX map's screens are ported to: the folder of the canvas.json the map
    was read from, else the latest version of the design canvas kept in the map's folder or a folder above it, up to
    the folder the graph reads from."""

    def __init__(self, project: Path) -> None:
        self.project = project

    @classmethod
    def of_map_file(cls, map_file: Path, top: Path) -> Optional["PortedCanvas"]:
        if map_file.name == _CANVAS_FILE:
            return cls(map_file.parent)
        folder = map_file.parent
        while True:
            latest = CanvasVersions.in_practice_root(folder).latest
            if latest is not None:
                return cls(latest.folder / _PROJECT)
            if folder == top or folder.parent == folder or top not in folder.parents:
                return None
            folder = folder.parent

    def artboard(self, prototype: str) -> Optional[ScreenArtboard]:
        """The artboard at prototype, a path in the project folder; none when the canvas holds none there."""
        path = self.project / prototype
        return ScreenArtboard.at(path) if prototype and path.is_file() else None

    def fixtures_name(self, text: str) -> bool:
        """Whether the canvas's fixtures bundle names text, as JavaScript writes a string."""
        bundle = self.project / "fixtures" / "canvas-fixtures.js"
        if not bundle.is_file():
            return False
        held = bundle.read_text(encoding="utf-8", errors="replace")
        return text in held or json.dumps(text, ensure_ascii=False)[1:-1] in held
