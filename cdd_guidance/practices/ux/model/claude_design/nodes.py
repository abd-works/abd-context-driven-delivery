"""Claude Design screens: the prototype screens laid out on the canvas's screens page.

A screen's ``prototype`` is a ``.dc.html`` artboard the canvas owns; people edit it there,
so render places it and never rewrites it. Render returns the board entries as JSON.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List

from cdd_guidance.practices.ux.model.ux_map import UxMap


class ClaudeDesignUxMap(UxMap):
    """Screen boards: each prototype screen on its own canvas page, as a plain frame (not a full-window page) sized for
    a desktop screen, so the editor stays around it. The story explorer keeps the ``screens`` page."""

    folder = "screens"
    page = "screens"
    width = 1600
    height = 1100

    def render(self, ux_map: UxMap) -> str:
        return json.dumps(self.boards(ux_map.screens), indent=1, ensure_ascii=False)

    def parse(self, content: str) -> UxMap:
        raise NotImplementedError("Claude Design screens are placed from the UX map; they are not read back.")

    @classmethod
    def prototype_names(cls, screens: Iterable) -> List[str]:
        """Each prototype once, in screen order, at its path on the canvas."""
        found: List[str] = []
        for screen in screens:
            if screen.prototype:
                name = f"{cls.folder}/{Path(screen.prototype).name}"
                if name not in found:
                    found.append(name)
        return found

    @classmethod
    def names(cls, screens: Iterable, files: Iterable[str] = ()) -> List[str]:
        """The prototypes the screens name, then any other screen artboard already in the folder (*files*)."""
        names = cls.prototype_names(screens)
        return names + [name for name in files if name not in names]

    @staticmethod
    def title(name: str) -> str:
        return Path(name).name.removesuffix(".dc.html").replace("-", " ").capitalize()

    @staticmethod
    def page_of(name: str) -> str:
        """Each screen's own canvas page: the editor shows it alone there, so leaving Play lands on it to edit."""
        return ("screen-" + Path(name).name.removesuffix(".dc.html"))[:40]

    @classmethod
    def pages(cls, screens: Iterable, files: Iterable[str] = ()) -> List[dict]:
        return [{"id": cls.page_of(name), "name": cls.title(name)} for name in cls.names(screens, files)]

    @classmethod
    def boards(cls, screens: Iterable, files: Iterable[str] = ()) -> Dict[str, dict]:
        """One board per screen, alone on its own page at a desktop size."""
        return {name: {"x": 0, "y": 0, "w": cls.width, "h": cls.height, "page": cls.page_of(name), "title": cls.title(name),
                       "is_interactive": True}
                for name in cls.names(screens, files)}
