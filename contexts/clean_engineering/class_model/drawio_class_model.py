"""DrawIO diagram channel for the CleanEngineering model.

Renders a UML class diagram using the same HTML-in-mxCell format as
drawio-domain-sync (drawio_tools.py) so the two systems produce compatible
diagrams.

Cell layout:
  - Each OoadClass becomes one mxCell vertex (CLASS_STYLE).
  - Properties and operations rendered as HTML inside the cell value using
    <hr/> section separators (name | properties | operations).
  - Relationships rendered as mxCell edges using EDGE_STYLES.
  - Classes laid out left-to-right, 5 per row, with gap between rows.

Parse reads class names and properties/operations back from the HTML.
"""
from __future__ import annotations

import html
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Tuple

_repo = Path(__file__).resolve().parents[3]
if str(_repo) not in sys.path:
    sys.path.insert(0, str(_repo))

from contexts.clean_engineering.class_model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
    Relationship,
)
from contexts.clean_engineering.class_model.update_report import UpdateReport

# ---------------------------------------------------------------------------
# Layout constants (mirrors drawio_tools.py)
# ---------------------------------------------------------------------------
CELL_WIDTH = 260
CELL_MIN_HEIGHT = 80
LINE_HEIGHT = 16
SECTION_PAD = 8

CLASS_STYLE = (
    "verticalAlign=top;align=left;overflow=fill;"
    "fontSize=12;fontFamily=Helvetica;html=1;whiteSpace=wrap;"
)

EDGE_STYLES = {
    "inheritance": "endArrow=block;endSize=16;endFill=0;html=1;",
    "composition": (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;"
        "endArrow=none;html=1;startArrow=diamondThin;startFill=1;startSize=14;"
    ),
    "aggregation": (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;"
        "endArrow=none;html=1;startArrow=diamondThin;startFill=0;startSize=14;"
    ),
    "association": (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;endArrow=open;endSize=12;html=1;"
    ),
}
DEFAULT_EDGE_STYLE = EDGE_STYLES["association"]

COLS_PER_ROW = 5
COL_GAP = 20
ROW_GAP = 60
START_X = 40
START_Y = 40


# ---------------------------------------------------------------------------
# Channel node types
# ---------------------------------------------------------------------------

class DrawIOOoadClass(OoadClass):
    pass


class DrawIOCleanEngineeringModel(CleanEngineeringModel):

    def create_child_class(self, source: OoadClass) -> DrawIOOoadClass:
        return DrawIOOoadClass(name=source.name, sequential_order=source.sequential_order)

    # ------------------------------------------------------------------
    # Uniform callable surface
    # ------------------------------------------------------------------

    @classmethod
    def parse(cls, text: str) -> "DrawIOCleanEngineeringModel":
        model = cls(name="", sequential_order=1)
        try:
            root_el = ET.fromstring(text)
        except ET.ParseError:
            return model

        mxcells = list(root_el.iter("mxCell"))
        order = 1
        id_to_class: dict[str, OoadClass] = {}
        module = Module(name="", sequential_order=1)

        for cell in mxcells:
            if cell.get("vertex") != "1":
                continue
            value = cell.get("value", "")
            name, props, ops = _parse_class_html(value)
            if not name:
                continue
            oclass = DrawIOOoadClass(
                name=name,
                sequential_order=order,
                properties=props,
                operations=ops,
            )
            module.classes.append(oclass)
            id_to_class[cell.get("id", "")] = oclass
            order += 1
        if module.classes:
            model.modules.append(module)

        # Parse edges as relationships
        for cell in mxcells:
            if cell.get("edge") != "1":
                continue
            src_id = cell.get("source", "")
            tgt_id = cell.get("target", "")
            src_cls = id_to_class.get(src_id)
            if src_cls is None:
                continue
            tgt_cls = id_to_class.get(tgt_id)
            tgt_name = tgt_cls.name if tgt_cls else tgt_id
            kind = _classify_edge(cell.get("style", ""))
            src_cls.relationships.append(Relationship(target=tgt_name, kind=kind))

        return model

    @classmethod
    def render(cls, canonical: CleanEngineeringModel, previous: Optional[str] = None) -> str:
        mxfile = ET.Element("mxfile")
        mxfile.set("host", "CleanEngineering.diagram.drawio")
        diagram = ET.SubElement(mxfile, "diagram")
        diagram.set("name", "CleanEngineering Model")
        diagram.set("id", "CleanEngineering-model")
        model_el = ET.SubElement(diagram, "mxGraphModel")
        _set_graph_attrs(model_el)
        root_el = ET.SubElement(model_el, "root")
        cell0 = ET.SubElement(root_el, "mxCell")
        cell0.set("id", "0")
        cell1 = ET.SubElement(root_el, "mxCell")
        cell1.set("id", "1")
        cell1.set("parent", "0")

        name_to_id: dict[str, str] = {}

        # Place classes in a grid
        for idx, oclass in enumerate(canonical.classes):
            col = idx % COLS_PER_ROW
            row = idx // COLS_PER_ROW
            x = START_X + col * (CELL_WIDTH + COL_GAP)
            y = START_Y + row * (_class_height(oclass) + ROW_GAP)
            cell_id = _slug(oclass.name)
            name_to_id[oclass.name] = cell_id
            _create_class_cell(root_el, oclass, cell_id=cell_id, x=x, y=y)

        # Add relationship edges
        edge_counter = [len(canonical.classes) + 10]

        for oclass in canonical.classes:
            src_id = name_to_id.get(oclass.name)
            for rel in oclass.relationships:
                tgt_id = name_to_id.get(rel.target)
                if src_id and tgt_id:
                    edge_counter[0] += 1
                    _create_edge(
                        root_el,
                        src_id=src_id,
                        tgt_id=tgt_id,
                        kind=rel.kind or "association",
                        edge_id=str(edge_counter[0]),
                    )

        ET.indent(ET.ElementTree(mxfile), space="  ")
        return ET.tostring(mxfile, encoding="unicode", xml_declaration=False)

    @classmethod
    def sync(cls, text: str, canonical: CleanEngineeringModel) -> UpdateReport:
        return canonical.translate_from(cls.parse(text))


# ---------------------------------------------------------------------------
# XML helpers
# ---------------------------------------------------------------------------

def _slug(name: str) -> str:
    return re.sub(r"\W+", "-", name).lower()


def _class_height(oclass: OoadClass) -> int:
    n_content = len(oclass.properties) + len(oclass.operations)
    return max(CELL_MIN_HEIGHT, 30 + n_content * LINE_HEIGHT + 2 * SECTION_PAD)


def _set_graph_attrs(el: ET.Element) -> None:
    for k, v in [
        ("dx", "1200"), ("dy", "800"), ("grid", "1"), ("gridSize", "10"),
        ("guides", "1"), ("tooltips", "1"), ("connect", "1"), ("arrows", "1"),
        ("fold", "1"), ("page", "1"), ("pageScale", "1"),
        ("pageWidth", "1654"), ("pageHeight", "1169"), ("math", "0"), ("shadow", "0"),
    ]:
        el.set(k, v)


def _build_class_html(oclass: OoadClass) -> str:
    name_html = html.escape(oclass.name)
    props_html = "".join(
        f"+ {html.escape(p.name)}{': ' + html.escape(p.type_hint) if p.type_hint else ''}<br/>"
        for p in oclass.properties
    ) or "<br/>"
    ops_html = "".join(
        f"{'- ' if op.name.startswith('_') else '+ '}{html.escape(op.name)}"
        f"({''.join(op.parameters)})"
        f"{': ' + html.escape(op.return_type) if op.return_type else ''}<br/>"
        for op in oclass.operations
    ) or "<br/>"
    return (
        f'<p style="margin:0px;margin-top:4px;text-align:center;"><b>{name_html}</b></p>'
        f'<hr size="1"/>'
        f'<p style="margin:0px;margin-left:4px;font-size:10px;">{props_html}</p>'
        f'<hr size="1"/>'
        f'<p style="margin:0px;margin-left:4px;font-size:10px;">{ops_html}</p>'
    )


def _create_class_cell(
    root_el: ET.Element,
    oclass: OoadClass,
    cell_id: str,
    x: int,
    y: int,
) -> ET.Element:
    cell = ET.SubElement(root_el, "mxCell")
    cell.set("id", cell_id)
    cell.set("value", _build_class_html(oclass))
    cell.set("style", CLASS_STYLE)
    cell.set("vertex", "1")
    cell.set("parent", "1")
    geo = ET.SubElement(cell, "mxGeometry")
    geo.set("x", str(x))
    geo.set("y", str(y))
    geo.set("width", str(CELL_WIDTH))
    geo.set("height", str(_class_height(oclass)))
    geo.set("as", "geometry")
    return cell


def _create_edge(
    root_el: ET.Element,
    src_id: str,
    tgt_id: str,
    kind: str,
    edge_id: str,
) -> ET.Element:
    style = EDGE_STYLES.get(kind, DEFAULT_EDGE_STYLE)
    cell = ET.SubElement(root_el, "mxCell")
    cell.set("id", edge_id)
    cell.set("value", "")
    cell.set("style", style)
    cell.set("edge", "1")
    cell.set("source", src_id)
    cell.set("target", tgt_id)
    cell.set("parent", "1")
    geo = ET.SubElement(cell, "mxGeometry")
    geo.set("relative", "1")
    geo.set("as", "geometry")
    return cell


def _parse_class_html(value: str) -> Tuple[Optional[str], List[Property], List[Operation]]:
    text = html.unescape(value)
    m = re.search(r"<b>([^<]+)</b>", text)
    name = m.group(1).strip() if m else None
    if not name:
        return None, [], []

    sections = re.split(r'<hr\s+size="1"\s*/?>', text)
    props: List[Property] = []
    ops: List[Operation] = []

    def _items(sec: str) -> List[str]:
        return [
            line.strip() for line in re.findall(r"[+\-]\s*([^<]+)", sec)
            if line.strip()
        ]

    if len(sections) >= 3:
        for raw in _items(sections[1]):
            if ":" in raw:
                n, t = raw.split(":", 1)
                props.append(Property(name=n.strip(), type_hint=t.strip()))
            else:
                props.append(Property(name=raw))
        for raw in _items(sections[2]):
            m2 = re.match(r"(_?\w+)\(([^)]*)\)(?::\s*(.+))?", raw)
            if m2:
                params = [p.strip() for p in m2.group(2).split(",") if p.strip()]
                ops.append(Operation(
                    name=m2.group(1),
                    parameters=params,
                    return_type=(m2.group(3) or "").strip(),
                ))

    return name, props, ops


def _classify_edge(style: str) -> str:
    if "endFill=0" in style and "endArrow=block" in style:
        return "inheritance"
    if "startFill=1" in style and "diamondThin" in style:
        return "composition"
    if "startFill=0" in style and "diamondThin" in style:
        return "aggregation"
    return "association"
