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
    """Screens page layout: one board per prototype screen, four to a row under the story explorer. Boards are plain
    canvas frames, not full-window pages, so the editor stays around them; they are sized for a desktop screen."""

    folder = "screens"
    page = "screens"
    width = 1600
    height = 1100
    column_pitch = 1680
    row_pitch = 1280
    top = 1100
    per_row = 4

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
    def boards(cls, screens: Iterable, files: Iterable[str] = ()) -> Dict[str, dict]:
        """The prototypes the screens name, then any other screen artboard already in the folder (*files*)."""
        names = cls.prototype_names(screens)
        names += [name for name in files if name not in names]
        boards: Dict[str, dict] = {}
        for index, name in enumerate(names):
            boards[name] = {
                "x": (index % cls.per_row) * cls.column_pitch,
                "y": cls.top + (index // cls.per_row) * cls.row_pitch,
                "w": cls.width,
                "h": cls.height,
                "page": cls.page,
                "title": Path(name).name.removesuffix(".dc.html").replace("-", " ").capitalize(),
                "is_interactive": True,
            }
        return boards
