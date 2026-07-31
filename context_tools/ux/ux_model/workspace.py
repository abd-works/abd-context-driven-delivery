"""Workspace - parsed UX artifacts scanners consume."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from .ux_map import UxMap


@dataclass
class Workspace:
    """Everything a scanner needs, already parsed."""

    root: Path
    ux_map: UxMap
    story_references: List[str] = field(default_factory=list)
    object_references: List[str] = field(default_factory=list)

    @classmethod
    def load(cls, root: Path) -> "Workspace":
        """Discover and parse UX artifacts under *root* (epic / sub-epic folder).

        Expects colocated layout: `ux-map.json` / `<goal>.html` at root;
        IA + sketch + context under `.context/`.
        """
        from context_tools.ux.diagram.drawio.nodes import DrawioUxMap
        from context_tools.ux.document.json.nodes import JsonUxMap
        from context_tools.ux.document.markdown.nodes import MarkdownUxMap
        from context_tools.ux.web.html.nodes import HtmlUxMap

        root = Path(root).resolve()
        ux_map: UxMap = (
            JsonUxMap.from_workspace(root)
            or HtmlUxMap.from_workspace(root)
            or DrawioUxMap.from_workspace(root)
            or MarkdownUxMap.from_workspace(root)
            or UxMap()
        )
        return cls(
            root=root,
            ux_map=ux_map,
            story_references=ux_map.story_references.as_list(),
            object_references=ux_map.object_references.as_list(),
        )

    def has_ux_map(self) -> bool:
        return bool(self.ux_map and self.ux_map.screens)

    def has_story_references(self) -> bool:
        return bool(self.story_references or self.ux_map.story_references)

    def has_object_references(self) -> bool:
        return bool(self.object_references or self.ux_map.object_references)
