"""A draw.io diagram as the catalog embeds it: in the diagrams.net viewer, sized to the cells it holds."""
from __future__ import annotations

import base64
import html
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

_VIEWER = "https://viewer.diagrams.net/"
# A diagram that names no page size is drawn on draw.io's default page.
_DEFAULT_PAGE_SIZE = (1080, 919)
# Space left around the cells when a diagram is framed or sized to its content.
_FRAME_MARGIN = 20
_STRONGEST_COMPRESSION = 9
# draw.io reads its compressed form as raw deflate, without a zlib header.
_RAW_DEFLATE_WINDOW = -15
# The layer and page cells every diagram holds; they have no place on the page.
_STRUCTURAL_CELLS = ("0", "1")


class DrawioDiagram:
    """One draw.io diagram. A story map is framed: its cells move to the top-left page edge and the page shrinks to fit,
    so the panel shows the map and not the empty page around it. Any other diagram keeps its cells where they are, and
    its frame grows to cover every cell."""

    def __init__(self, xml: str, name: str = "") -> None:
        self.xml = xml
        self.name = name

    @classmethod
    def load(cls, path: Path) -> DrawioDiagram:
        return cls(path.read_text(encoding="utf-8"), path.name)

    @property
    def is_story_map(self) -> bool:
        return Path(self.name).stem.replace("-", "_") == "story_map"

    @property
    def page_size(self) -> tuple[int, int]:
        try:
            model = ET.fromstring(self.xml).find(".//mxGraphModel")
        except ET.ParseError:
            return _DEFAULT_PAGE_SIZE
        if model is None:
            return _DEFAULT_PAGE_SIZE
        width, height = _DEFAULT_PAGE_SIZE
        return int(float(model.get("pageWidth") or width)), int(float(model.get("pageHeight") or height))

    @property
    def content_size(self) -> tuple[int, int]:
        """The pixel box that covers the page and every placed cell, with the frame margin around the cells."""
        page_width, page_height = self.page_size
        try:
            root = ET.fromstring(self.xml)
        except ET.ParseError:
            return page_width, page_height
        xs: list[float] = [0.0, float(page_width)]
        ys: list[float] = [0.0, float(page_height)]
        for geometry in self._placed(root, include_structural=True):
            left, top = float(geometry.get("x") or 0), float(geometry.get("y") or 0)
            xs.extend((left, left + float(geometry.get("width") or 0)))
            ys.extend((top, top + float(geometry.get("height") or 0)))
        width = int(max(xs) - min(xs) + _FRAME_MARGIN * 2)
        height = int(max(ys) - min(ys) + _FRAME_MARGIN * 2)
        return max(page_width, width), max(page_height, height)

    @property
    def framed(self) -> DrawioDiagram:
        """The diagram with its cells moved to the top-left page edge and the page resized to fit them."""
        try:
            root = ET.fromstring(self.xml)
        except ET.ParseError:
            return self
        placed = self._placed(root, include_structural=False)
        if not placed:
            return self
        left = min(float(geometry.get("x") or 0) for geometry in placed)
        top = min(float(geometry.get("y") or 0) for geometry in placed)
        right = max(float(geometry.get("x") or 0) + float(geometry.get("width") or 0) for geometry in placed)
        bottom = max(float(geometry.get("y") or 0) + float(geometry.get("height") or 0) for geometry in placed)
        for geometry in placed:
            geometry.set("x", str(int(float(geometry.get("x") or 0) + _FRAME_MARGIN - left)))
            geometry.set("y", str(int(float(geometry.get("y") or 0) + _FRAME_MARGIN - top)))
        model = root.find(".//mxGraphModel")
        if model is not None:
            model.set("pageWidth", str(int(right - left + _FRAME_MARGIN * 2)))
            model.set("pageHeight", str(int(bottom - top + _FRAME_MARGIN * 2)))
        return DrawioDiagram(ET.tostring(root, encoding="unicode"), self.name)

    def viewer_url(self, *, with_toolbar: bool) -> str:
        """The diagrams.net viewer showing the diagram: with its page navigation and zoom toolbar on a fidelity page,
        bare inside an approach panel, which sizes and zooms it itself."""
        compressor = zlib.compressobj(_STRONGEST_COMPRESSION, zlib.DEFLATED, _RAW_DEFLATE_WINDOW)
        compressed = compressor.compress(self.xml.encode("utf-8")) + compressor.flush()
        token = urllib.parse.quote(base64.b64encode(compressed).decode("ascii"), safe="")
        controls = "nav=1&layers=1&toolbar=zoom" if with_toolbar else "nav=0&layers=1&toolbar=0"
        return f"{_VIEWER}?lightbox=1&{controls}&edit=_blank#R{token}"

    @property
    def panel_html(self) -> str:
        """The diagram in an approach panel: a story map framed to its cells, any other diagram at its full size."""
        shown = self.framed if self.is_story_map else self
        width, height = shown.page_size if self.is_story_map else shown.content_size
        kind = "approach-stage-drawio--story-map" if self.is_story_map else "approach-stage-drawio--framed"
        source = html.escape(shown.viewer_url(with_toolbar=False), quote=True)
        return (
            f'<div class="approach-stage-drawio-zoom skill-drawio-wrap approach-stage-drawio {kind}" '
            f'data-page-w="{width}" data-page-h="{height}">'
            f'<div class="approach-stage-drawio__scale">'
            f'<iframe class="catalog-drawio-frame" title="{html.escape(self.name)}" '
            f'width="{width}" height="{height}" '
            f'style="width:{width}px;height:{height}px;max-width:none" '
            f'data-src="{source}"></iframe>'
            "</div></div>"
        )

    def _placed(self, root: ET.Element, *, include_structural: bool) -> list[ET.Element]:
        """The geometry of every cell placed on the page."""
        placed = []
        for cell in root.iter("mxCell"):
            if not include_structural and (cell.get("id") or "") in _STRUCTURAL_CELLS:
                continue
            geometry = cell.find("mxGeometry")
            if geometry is not None and geometry.get("x") is not None:
                placed.append(geometry)
        return placed
