"""Upload a story map to a Miro board via the REST API.

Each shape is placed at an exact board coordinate (no canvas-composer chunking,
no Miro-side stacking offsets). Positions are derived by scaling the SVG-coordinate
layout produced by MiroStoryMap.render_api_shapes().

Coordinate maths
----------------
SVG layout  : top-left origin, x grows right, y grows down, units are logical pixels.
Miro board  : centre origin (canvas_center), x grows right, y grows down, units are board px.

For a shape whose SVG top-left is (sx, sy) and size is (sw, sh):
    miro_centre_x = (sx + sw / 2) * scale + origin_x
    miro_centre_y = (sy + sh / 2) * scale + origin_y

Usage
-----
    from context_tools.stories.diagram.miro.api import MiroApiClient
    from context_tools.stories.diagram.miro.uploader import MiroUploader
    from context_tools.stories.diagram.miro.nodes import MiroStoryMap
    from context_tools.stories.document.markdown.nodes import MarkdownStoryMap

    canonical = MarkdownStoryMap().parse(open("story-map.md").read())
    client = MiroApiClient()          # reads MIRO_TOKEN env var or ~/.miro-token
    uploader = MiroUploader(client)
    result = uploader.upload(canonical, board_id="uXjVHuiSsAA=")
    print(result["shape_count"], "shapes created")
"""
from __future__ import annotations

import time
from typing import Dict, List, Optional

from .api import MiroApiClient
from .nodes import MiroStoryMap

_STORY_MAP_FILLS = frozenset({
    "#e1d5e7",  # epic
    "#d5e8d4",  # subepic d0
    "#c9dcc8",  # subepic d1
    "#bdd0bc",  # subepic d2
    "#b1c4b0",  # subepic d3
    "#fff2cc",  # story
    "#dae8fc",  # actor
})


class MiroUploader:
    """Create and optionally clear story-map shapes on a Miro board."""

    def __init__(self, client: MiroApiClient, delay_ms: int = 350) -> None:
        """
        ``delay_ms``: milliseconds to sleep between API calls (default 350 ms keeps
        well within Miro's 200 req/min rate limit).
        """
        self.client = client
        self.delay_ms = delay_ms

    def upload(
        self,
        canonical: MiroStoryMap,
        board_id: str,
        scale: float = 1.5,
        origin_x: float = 0.0,
        origin_y: float = 6000.0,
        on_progress: Optional[callable] = None,
    ) -> Dict[str, object]:
        """Upload all story map shapes and return a result summary.

        Returns::

            {
                "board_id": str,
                "shape_count": int,
                "scale": float,
                "origin": {"x": float, "y": float},
                "ids": {semantic_id: miro_id, ...},
            }

        ``on_progress(done, total)`` is called after each successful shape
        creation if provided (useful for progress reporting).
        """
        shapes = MiroStoryMap().render_api_shapes(canonical)
        total = len(shapes)
        id_map: Dict[str, str] = {}

        for idx, shape in enumerate(shapes):
            cx = (shape["x"] + shape["w"] / 2) * scale + origin_x
            cy = (shape["y"] + shape["h"] / 2) * scale + origin_y
            w = shape["w"] * scale
            h = shape["h"] * scale
            font_size = max(8, round(shape.get("font_size", 12) * scale * 0.5))

            result = self.client.create_shape(
                board_id=board_id,
                x=cx, y=cy, w=w, h=h,
                fill=shape["fill"],
                stroke=shape["stroke"],
                stroke_width=shape["stroke_width"],
                content=shape["content"],
                rx=shape.get("rx", 0),
                font_size=font_size,
            )
            id_map[shape["id"]] = result["id"]

            if on_progress is not None:
                on_progress(idx + 1, total)

            if self.delay_ms > 0 and idx < total - 1:
                time.sleep(self.delay_ms / 1000)

        return {
            "board_id": board_id,
            "shape_count": len(id_map),
            "scale": scale,
            "origin": {"x": origin_x, "y": origin_y},
            "ids": id_map,
        }

    def clear(self, board_id: str, miro_ids: List[str]) -> int:
        """Delete a list of shapes by Miro ID. Returns the count deleted."""
        count = 0
        for mid in miro_ids:
            self.client.delete_shape(board_id, mid)
            count += 1
            if self.delay_ms > 0 and count < len(miro_ids):
                time.sleep(self.delay_ms / 1000)
        return count

    def clear_story_map(self, board_id: str) -> int:
        """Delete all story-map shapes from the board (identified by fill colour).

        Uses list_shapes pagination. Returns the count deleted.
        Caution: only works for shapes created via the REST API (not canvas-composer).
        """
        to_delete: List[str] = []
        for shape in self.client.list_shapes(board_id):
            style = shape.get("style", {})
            fill = style.get("fillColor", "").lower()
            if fill in _STORY_MAP_FILLS:
                to_delete.append(shape["id"])
        return self.clear(board_id, to_delete)
