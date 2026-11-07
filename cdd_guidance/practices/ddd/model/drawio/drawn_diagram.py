"""A draw.io file read back into its cells: each box with its label, place, and container, and each arrow."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from html.parser import HTMLParser

_PAGE = "1"
_BOX = ("x", "y", "width", "height")


class _LabelText(HTMLParser):
    """The words of an HTML label, one entry per run of text between tags."""

    def __init__(self, label: str) -> None:
        super().__init__(convert_charrefs=True)
        self.texts: list[str] = []
        self.feed(label)
        self.close()

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.texts.append(data.strip())


def label_texts(label: str) -> list[str]:
    """The words of an HTML label, one entry per run of text between tags."""
    return _LabelText(label).texts


class DrawnCell:
    """One `mxCell`: a box with its label and place, or an arrow between two boxes."""

    def __init__(self, element: ET.Element) -> None:
        self.cell_id = element.get("id", "")
        self.value = element.get("value", "")
        self.parent_id = element.get("parent", "")
        self.source_id = element.get("source", "")
        self.target_id = element.get("target", "")
        self.is_arrow = element.get("edge") == "1"
        geometry = element.find("mxGeometry")
        found = geometry.attrib if geometry is not None else {}
        self.box = tuple(float(found.get(key, 0)) for key in _BOX)

    @property
    def texts(self) -> list[str]:
        """The label's text, one entry per run between HTML tags."""
        return label_texts(self.value)

    def holds(self, other: "DrawnCell") -> bool:
        """True when the other box's centre lies inside this box, both placed on the page."""
        x, y, width, height = self.box
        other_x, other_y, other_width, other_height = other.box
        centre_x, centre_y = other_x + other_width / 2, other_y + other_height / 2
        return x <= centre_x <= x + width and y <= centre_y <= y + height


class DrawnDiagram:
    """The first page of a draw.io file, its cells in the order they were drawn."""

    def __init__(self, text: str) -> None:
        document = ET.fromstring(text.encode("utf-8"))
        page = document.find("diagram")
        self.page_id = page.get("id", "") if page is not None else ""
        self.cells = [DrawnCell(element) for element in document.iter("mxCell")]

    @property
    def arrows(self) -> list[DrawnCell]:
        return [cell for cell in self.cells if cell.is_arrow]

    def boxes_in(self, parent_id: str = _PAGE) -> list[DrawnCell]:
        """The boxes drawn inside that container; with no container, the boxes on the page itself."""
        return [cell for cell in self.cells if not cell.is_arrow and cell.parent_id == parent_id]

    def cell(self, cell_id: str) -> DrawnCell | None:
        return next((cell for cell in self.cells if cell.cell_id == cell_id), None)
