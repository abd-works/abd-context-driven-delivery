"""Claude Design screens: the prototype screens laid out on the canvas's screens page.

A screen's ``prototype`` is a ``.dc.html`` artboard the canvas owns; people edit it there,
so render places it and never rewrites it. Render returns the board entries as JSON.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List

from cdd_guidance.practices.ux.model.ux_map import UxMap


class ClaudeDesignScreensNotReadable(NotImplementedError):
    """Claude Design screens are placed from the UX map and edited on the canvas; they are never read back into one."""


class ClaudeDesignUxMap(UxMap):
    """Screen boards: each prototype screen on its own canvas page, as a plain frame (not a full-window page) sized for
    a desktop screen, so the editor stays around it. The story explorer keeps the ``screens`` page."""

    folder = "screens"
    page = "screens"
    width = 1600
    height = 1100

    def render(self, canonical: UxMap) -> str:
        """canonical's screens placed on the canvas: copied into a Claude Design map, which places its own."""
        return self.copy_of(canonical).save()

    def save(self) -> str:
        return json.dumps(self.boards(), indent=1, ensure_ascii=False)

    def parse(self, content: str) -> UxMap:
        raise ClaudeDesignScreensNotReadable("Claude Design screens are placed from the UX map; they are not read back.")

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

    @staticmethod
    def title(name: str) -> str:
        return Path(name).name.removesuffix(".dc.html").replace("-", " ").capitalize()

    @staticmethod
    def page_of(name: str) -> str:
        """Each screen's own canvas page: the editor shows it alone there, so leaving Play lands on it to edit."""
        return ("screen-" + Path(name).name.removesuffix(".dc.html"))[:40]

    def pages(self, files: Iterable[str] = ()) -> List[dict]:
        return [{"id": self.page_of(name), "name": self.title(name)} for name in self.names(files)]

    def boards(self, files: Iterable[str] = ()) -> Dict[str, dict]:
        """One board per screen, alone on its own page at a desktop size."""
        return {name: {"x": 0, "y": 0, "w": self.width, "h": self.height, "page": self.page_of(name), "title": self.title(name),
                       "is_interactive": True}
                for name in self.names(files)}
