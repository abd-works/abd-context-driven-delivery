"""A draw.io file as a practice reads and writes it: its pages, each page's cells, and what one cell says.

A ``.drawio`` file is an ``<mxfile>`` of ``<diagram>`` pages, each holding an ``<mxGraphModel>`` whose ``<root>`` holds
the cells (``<mxCell>``): vertices with an ``<mxGeometry>`` box, and edges joining two of them. A cell that links
somewhere sits inside a ``<UserObject>`` that carries its id, its words and its links. Every practice that draws a
diagram reads and writes it through these classes, as every practice that draws a board uses harness/whiteboard.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional
from xml.etree import ElementTree as ET

from harness.markdown.format import Format, SourceDocument
from harness.whiteboard import Box

# The two cells every draw.io page starts with: the root and the layer every other cell is drawn on.
_PAGE_CELLS = ("0", "1")
_HEADER = "<?xml version='1.0' encoding='utf-8'?>\n"
# The fields of a page's root cell that keep the document the drawing was drawn from, and the tags draw.io writes a cell
# carrying fields of its own in. draw.io shows a root cell's fields as the diagram's data and draws none of them.
_KEPT_FORMAT = "cddSourceFormat"
_KEPT_TEXT = "cddSourceDocument"
_HOLDERS = ("UserObject", "object")


class UnreadableDrawio(ValueError):
    """Text that is not a draw.io document, so no practice reads a diagram from it: it is not XML, or it holds no
    graph model."""


class CellStyle:
    """One cell's draw.io style, ``key=value;`` pairs after an optional first word that names what the cell draws, such
    as ``subepic:2;rounded=1;``: the one reader of a style every practice asks."""

    def __init__(self, text: str) -> None:
        self.text = text or ""

    def value(self, key: str) -> str:
        """The value the style sets for key, such as ``0.3`` for ``exitX`` in ``exitX=0.3;``; empty when it sets none."""
        found = re.search(f"(?:^|;){re.escape(key)}=([^;]*)", self.text)
        return found.group(1) if found else ""

    def number(self, key: str) -> Optional[float]:
        """A number the style sets for key, such as ``exitX=0.3``; none when it sets no number."""
        found = re.fullmatch(r"-?[0-9.]+", self.value(key))
        return float(found.group(0)) if found else None

    def __contains__(self, key: str) -> bool:
        return re.search(f"(?:^|;){re.escape(key)}=", self.text) is not None

    @property
    def role(self) -> str:
        """The first word of the style, before any ``:``, which names what a practice's cell draws, such as ``story``
        for ``story:user;rounded=1;``; empty for a style that starts with a key."""
        head = self.text.split(";", 1)[0]
        return "" if "=" in head else head.split(":", 1)[0]

    @property
    def role_detail(self) -> str:
        """What the first word says after its ``:``, such as ``user`` for ``story:user;``; empty when it says nothing."""
        head = self.text.split(";", 1)[0]
        return head.split(":", 1)[1] if ":" in head and "=" not in head else ""


class DrawioCell:
    """One cell of a page: its id, its words, its style, the box a vertex is drawn in, the cells an edge joins, and the
    link it carries; a linked cell is read from the ``UserObject`` round it, as if its id and words were on the cell."""

    def __init__(self, element: ET.Element, holder: Optional[ET.Element] = None) -> None:
        # The <mxCell> itself, and the <UserObject> round it when it links somewhere.
        self.element = element
        self._holder = holder

    @property
    def id(self) -> str:
        return (self._holder if self._holder is not None else self.element).get("id", "")

    @property
    def label(self) -> str:
        return self._holder.get("label", "") if self._holder is not None else self.element.get("value", "")

    @property
    def style(self) -> CellStyle:
        return CellStyle(self.element.get("style", ""))

    @property
    def link(self) -> str:
        return self._holder.get("link", "") if self._holder is not None else ""

    @property
    def source(self) -> str:
        return self.element.get("source", "")

    @property
    def target(self) -> str:
        return self.element.get("target", "")

    @property
    def is_vertex(self) -> bool:
        return self.element.get("vertex") == "1"

    @property
    def is_edge(self) -> bool:
        return self.element.get("edge") == "1"

    @property
    def geometry(self) -> Dict[str, str]:
        """The cell's mxGeometry fields as the file writes them, such as ``{"x": "40", "width": "152"}``; none for a cell
        with no geometry. A drawing a person moved keeps their numbers as they wrote them."""
        geometry = self.element.find("mxGeometry")
        return dict(geometry.attrib) if geometry is not None else {}

    @property
    def box(self) -> Optional[Box]:
        """The box the cell's mxGeometry places it in; none for a cell with no geometry."""
        geometry = self.element.find("mxGeometry")
        if geometry is None:
            return None
        return Box(*(float(geometry.get(side, "0") or 0) for side in ("x", "y", "width", "height")))


class DrawioPage:
    """One diagram page of a draw.io file: its name, and the cells on it, each read once."""

    def __init__(self, name: str, root: ET.Element) -> None:
        self.name = name
        # The page's <root>, or any element its cells are found under, such as a whole document read as one page.
        self._root = root

    @property
    def element(self) -> ET.Element:
        """The element the page's cells are found under, for a reader that walks the page's XML itself."""
        return self._root

    @property
    def cells(self) -> List[DrawioCell]:
        """Every cell on the page, a linked one read with the UserObject round it, in the order the file holds them."""
        found: List[DrawioCell] = []
        wrapped = set()
        for element in self._root.iter():
            if element.tag == "UserObject":
                cell = element.find("mxCell")
                if cell is not None:
                    wrapped.add(id(cell))
                    found.append(DrawioCell(cell, element))
            elif element.tag == "mxCell" and id(element) not in wrapped:
                found.append(DrawioCell(element))
        return found

    def cell(self, cell_id: str) -> Optional[DrawioCell]:
        """The cell called cell_id; none when the page has no such cell."""
        return next((cell for cell in self.cells if cell.id == cell_id), None)

    def boxes(self) -> Dict[str, Box]:
        """The box each vertex is drawn in, by its id."""
        return {cell.id: cell.box for cell in self.cells if cell.is_vertex and cell.id and cell.box is not None}

    def positions(self) -> Dict[str, tuple[float, float]]:
        """Where each vertex whose geometry places it sits, by its id; a vertex whose geometry names no corner is left
        for a layout to place."""
        found: Dict[str, tuple[float, float]] = {}
        for cell in self.cells:
            geometry = cell.geometry
            if not (cell.is_vertex and cell.id and geometry):
                continue
            try:
                found[cell.id] = (float(geometry["x"]), float(geometry["y"]))
            except (KeyError, ValueError):
                continue
        return found

    def add(self, cell_id: str, label: str, style: str, box: Box, link: Optional[Dict[str, str]] = None) -> DrawioCell:
        """A vertex drawn in box on this page's layer; with link, inside a UserObject that carries its id, its words, and
        the link's fields (``link``, and any others a practice writes, such as ``entry``)."""
        attributes = {"id": cell_id, "value": label, "style": style, "vertex": "1", "parent": "1"}
        holder = self._root
        user = None
        if link:
            fields = dict(link)
            user = ET.SubElement(self._root, "UserObject", attrib={"label": attributes.pop("value"), "link": fields.pop("link", ""), "id": attributes.pop("id"), **fields})
            holder = user
        element = ET.SubElement(holder, "mxCell", attrib=attributes)
        ET.SubElement(element, "mxGeometry", attrib={"x": str(box.x), "y": str(box.y), "width": str(box.w), "height": str(box.h), "as": "geometry"})
        return DrawioCell(element, user)


class DrawioFile:
    """A draw.io document: its pages, read from a file's text or added one by one, and written back as the text of a
    ``.drawio`` file."""

    def __init__(self, document: Optional[ET.Element] = None) -> None:
        self._document = document if document is not None else ET.Element("mxfile", attrib={"host": "app.diagrams.net"})

    @classmethod
    def from_text(cls, text: str) -> DrawioFile:
        """The document text holds: an ``<mxfile>``, or a bare ``<mxGraphModel>`` read as one page. Text that is not
        XML, or holds no graph model, raises *UnreadableDrawio*."""
        try:
            document = ET.fromstring(text.strip())
        except ET.ParseError as error:
            raise UnreadableDrawio(f"Not valid draw.io XML: {error}") from error
        if document.tag not in ("mxfile", "mxGraphModel") or (document.tag == "mxfile" and document.find(".//mxGraphModel") is None):
            raise UnreadableDrawio(f"A draw.io document is an <mxfile> or an <mxGraphModel>, not <{document.tag}>")
        return cls(document)

    @property
    def pages(self) -> List[DrawioPage]:
        """Each page that holds a graph model, in file order; a bare graph model is one page with no name."""
        if self._document.tag == "mxGraphModel":
            return [DrawioPage("", self._document)]
        found = ((diagram.get("name") or "", diagram.find("mxGraphModel/root")) for diagram in self._document.findall("diagram"))
        return [DrawioPage(name, root) for name, root in found if root is not None]

    def page(self, name: str) -> Optional[DrawioPage]:
        """The page called name; none when the document has none."""
        return next((page for page in self.pages if page.name == name), None)

    @property
    def whole(self) -> DrawioPage:
        """Every cell of the document read as one page, whatever page it is on."""
        return DrawioPage("", self._document)

    def add_page(self, name: str, page_id: str) -> DrawioPage:
        """A new page called name, holding the root cell and the layer every cell is drawn on."""
        diagram = ET.SubElement(self._document, "diagram", attrib={"name": name, "id": page_id})
        root = ET.SubElement(ET.SubElement(diagram, "mxGraphModel"), "root")
        ET.SubElement(root, "mxCell", attrib={"id": _PAGE_CELLS[0]})
        ET.SubElement(root, "mxCell", attrib={"id": _PAGE_CELLS[1], "parent": _PAGE_CELLS[0]})
        return DrawioPage(name, root)

    @property
    def kept_document(self) -> Optional[SourceDocument]:
        """The document this drawing was drawn from, kept on a page's root cell (``keep``); none when it keeps none."""
        for holder in self._document.iter():
            if holder.tag in _HOLDERS and holder.get(_KEPT_TEXT) is not None:
                return SourceDocument(Format(holder.get(_KEPT_FORMAT, "")), holder.get(_KEPT_TEXT, ""))
        return None

    def keep(self, document: SourceDocument) -> None:
        """Keep document on the first page's root cell, as fields draw.io keeps with the diagram and draws nowhere: the
        root cell goes inside a UserObject that carries the document's format and text, as draw.io writes a cell with
        fields of its own. A drawing with no page keeps nothing."""
        pages = self.pages
        if not pages:
            return
        root = pages[0].element
        holder = next((element for element in root if element.tag in _HOLDERS and element.get("id") == _PAGE_CELLS[0]), None)
        if holder is None:
            holder = self._root_cell_held(root)
        holder.set(_KEPT_FORMAT, str(document.format))
        holder.set(_KEPT_TEXT, document.text)

    def _root_cell_held(self, root: ET.Element) -> ET.Element:
        """The UserObject the page's root cell is moved into, carrying its id; a page with no root cell gains one."""
        cell = next((element for element in root if element.tag == "mxCell" and element.get("id") == _PAGE_CELLS[0]), None)
        at = list(root).index(cell) if cell is not None else 0
        if cell is not None:
            root.remove(cell)
            del cell.attrib["id"]
        holder = ET.Element("UserObject", attrib={"label": "", "id": _PAGE_CELLS[0]})
        holder.append(cell if cell is not None else ET.Element("mxCell"))
        root.insert(at, holder)
        return holder

    def save(self) -> str:
        """The document as the text of a ``.drawio`` file."""
        return _HEADER + ET.tostring(self._document, encoding="unicode")


class KeepsDocumentInDrawing:
    """What a practice's draw.io format mixes in, ahead of its model, to keep the document a drawing was drawn from:
    the render writes it into the drawing (``keeping``) and a render of the drawing back into that document's format
    writes over it (``document_kept_in``), so the prose the drawing cannot show comes back."""

    def document_kept_in(self, text: str) -> Optional[SourceDocument]:
        """The document text, a drawing, keeps; none for a drawing that keeps none, or text that is no drawing."""
        try:
            return DrawioFile.from_text(text).kept_document
        except UnreadableDrawio:
            return None

    def keeping(self, rendered: object, document: SourceDocument) -> object:
        """rendered, a drawing, keeping document; anything that is no drawing as it is."""
        if not isinstance(rendered, str) or not rendered.strip():
            return rendered
        try:
            drawing = DrawioFile.from_text(rendered)
        except UnreadableDrawio:
            return rendered
        drawing.keep(document)
        return drawing.save()
