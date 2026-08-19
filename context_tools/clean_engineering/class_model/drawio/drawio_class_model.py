"""DrawIO diagram channel for the CleanEngineering model.

Two visual fidelities share this channel (auto-detected on parse/render):

**Modules view** (modules fidelity) - system-context style:
  - Each Module is one rounded mxCell (MODULE_STYLE).
  - Path nesting is **containment**: `powers/attack` is a child cell inside `powers`.
  - Shared base classes/terms live on the **parent** (e.g. `Effect` on `powers`), not a
    fake `powers/effect` submodule. Missing path parents are synthesized as containers.
  - Cell HTML: bold name, italic purpose, <hr>, bullet list of public seam terms.
  - Edges are one-way dependencies (A -> B means A depends on B); child->path-parent
    edges are omitted (containment already shows that).
  - No stack/tech callouts; no UML props/ops.

**Class view** (model+ fidelity) - UML class diagram:
  - Each OoadClass becomes one mxCell vertex (CLASS_STYLE).
  - Properties and operations as HTML with <hr/> section separators.
  - Relationships as mxCell edges using EDGE_STYLES.
  - Classes clustered by module / composition aggregate: related concepts sit
    in tight islands, distinct contexts sit farther apart; edges use distinct
    anchors and obstacle-avoiding orthogonal waypoints.

Parse reads either shape back into the canonical model.
"""
from __future__ import annotations

import copy
import html
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_repo = Path(__file__).resolve().parents[4]
if str(_repo) not in sys.path:
    sys.path.insert(0, str(_repo))

from context_tools.clean_engineering.class_model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
    Relationship,
)
from context_tools.clean_engineering.class_model.update_report import UpdateReport

# ---------------------------------------------------------------------------
# Class-diagram layout (mirrors drawio_tools.py)
# ---------------------------------------------------------------------------
CELL_WIDTH = 260
CELL_MIN_HEIGHT = 80
LINE_HEIGHT = 16
SECTION_PAD = 8

CLASS_STYLE = (
    "verticalAlign=top;align=left;overflow=fill;"
    "fontSize=12;fontFamily=Helvetica;html=1;whiteSpace=wrap;"
)
IMPORTED_CLASS_STYLE = (
    CLASS_STYLE
    + "dashed=1;dashPattern=8 8;strokeColor=#666666;"
)

EDGE_STYLES = {
    "inheritance": (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;"
        "endArrow=block;endSize=16;endFill=0;html=1;"
    ),
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

CLUSTER_GAP_X = 360
CLUSTER_GAP_Y = 420
INNER_COLS = 2
INNER_COL_GAP = 20
INNER_ROW_GAP = 28
COLS_PER_ROW = INNER_COLS  # used by leaf-row heuristics / gutters
COL_GAP = INNER_COL_GAP
ROW_GAP = INNER_ROW_GAP
START_X = 40
START_Y = 40
ROUTE_CLEARANCE = 24
ROUTE_LANE_STEP = 10
OVERLAP_GAP = 24

# ---------------------------------------------------------------------------
# Modules-diagram layout (system-context style)
# ---------------------------------------------------------------------------
MODULE_CELL_WIDTH = 280
MODULE_CELL_MIN_HEIGHT = 100
MODULE_LINE_HEIGHT = 16
MODULE_HEADER_HEIGHT = 48
MODULE_MAX_SEAM_BULLETS = 6
MODULE_PURPOSE_MAX_CHARS = 90
MODULE_COL_GAP = 48
MODULE_ROW_GAP = 32
MODULE_START_X = 40
MODULE_START_Y = 100
MODULE_CHILD_PAD_X = 16
MODULE_CHILD_PAD_Y = 12
MODULE_CHILD_GAP = 12
MODULE_CHILD_COLS = 2

MODULE_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#1a3a6e;strokeColor=#0e2547;"
    "fontColor=#ffffff;fontSize=12;align=left;verticalAlign=top;"
    "spacingLeft=10;spacingTop=10;strokeWidth=3;"
)
MODULE_CHILD_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
    "fontColor=#000000;fontSize=12;align=left;verticalAlign=top;"
    "spacingLeft=10;spacingTop=10;strokeWidth=2;"
)
MODULE_DEP_EDGE_STYLE = (
    "edgeStyle=orthogonalEdgeStyle;rounded=1;"
    "endArrow=classic;html=1;strokeWidth=2;fontSize=10;"
)
MODULE_TITLE_STYLE = (
    "text;html=1;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;"
)
MODULE_SUBTITLE_STYLE = (
    "text;html=1;align=center;verticalAlign=middle;fontSize=11;fontStyle=2;"
)

_MODULE_MARKER = "fillColor=#1a3a6e"
_MODULE_CHILD_MARKER = "fillColor=#dae8fc"


# ---------------------------------------------------------------------------
# Channel node types
# ---------------------------------------------------------------------------

class DrawIOOoadClass(OoadClass):
    pass


class DrawIOModule(Module):
    def create_child_class(self, source: OoadClass) -> DrawIOOoadClass:
        return DrawIOOoadClass(name=source.name, sequential_order=source.sequential_order)


class DrawIOCleanEngineeringModel(CleanEngineeringModel):

    def create_child_module(self, source: Module) -> DrawIOModule:
        return DrawIOModule(name=source.name, sequential_order=source.sequential_order)

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
        if _looks_like_modules_diagram(mxcells):
            return cls._parse_modules(mxcells)
        diagrams = list(root_el.findall("diagram"))
        if len(diagrams) > 1:
            return cls._parse_classes_multipage(diagrams)
        return cls._parse_classes(mxcells)

    @classmethod
    def _parse_modules(cls, mxcells: List[ET.Element]) -> "DrawIOCleanEngineeringModel":
        model = cls(name="", sequential_order=1)
        order = 1
        id_to_module: dict[str, Module] = {}

        for cell in mxcells:
            if cell.get("vertex") != "1":
                continue
            style = cell.get("style", "")
            if "text;" in style or style.startswith("text;"):
                # Title / subtitle - pull system name from title if present
                if cell.get("id") == "title":
                    title = html.unescape(cell.get("value", ""))
                    m = re.match(r"^(.+?)\s*[-\-]\s*Modules?", title)
                    if m:
                        model.name = m.group(1).strip()
                continue
            if not _is_module_style(style):
                continue
            value = cell.get("value", "")
            name, purpose, terms = _parse_module_html(value)
            if not name:
                continue
            cell_id = cell.get("id", "")
            module = DrawIOModule(
                name=name,
                sequential_order=order,
                description=purpose,
                seam_terms=terms,
            )
            id_to_module[cell_id] = module
            # Synthesized folder containers (id nest-*) are visual only
            if not cell_id.startswith("nest-"):
                model.modules.append(module)
            order += 1

        # Containment restores child -> real path-parent dependency when edge was omitted
        for cell in mxcells:
            if cell.get("vertex") != "1":
                continue
            child = id_to_module.get(cell.get("id", ""))
            parent = id_to_module.get(cell.get("parent", ""))
            if child is None or parent is None:
                continue
            if child not in model.modules or parent not in model.modules:
                continue
            if parent.name not in child.dependencies:
                child.dependencies.append(parent.name)

        for cell in mxcells:
            if cell.get("edge") != "1":
                continue
            src = id_to_module.get(cell.get("source", ""))
            tgt = id_to_module.get(cell.get("target", ""))
            if src is None or tgt is None:
                continue
            if src not in model.modules:
                continue
            if tgt.name not in src.dependencies:
                src.dependencies.append(tgt.name)

        return model

    @classmethod
    def _parse_classes(cls, mxcells: List[ET.Element]) -> "DrawIOCleanEngineeringModel":
        model = cls(name="", sequential_order=1)
        order = 1
        id_to_class: dict[str, OoadClass] = {}
        module = DrawIOModule(name="", sequential_order=1)

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
    def _parse_classes_multipage(
        cls, diagrams: List[ET.Element]
    ) -> "DrawIOCleanEngineeringModel":
        """One Draw.io page → one module; skip dashed «from:» import cards."""
        model = cls(name="", sequential_order=1)
        order = 1
        seen_names: set[str] = set()
        # Global id→class for edge wiring (local + imported names)
        id_to_class: dict[str, OoadClass] = {}
        id_to_name: dict[str, str] = {}

        for diagram in diagrams:
            page_name = diagram.get("name") or f"module-{order}"
            module = DrawIOModule(name=page_name, sequential_order=order)
            page_cells = list(diagram.iter("mxCell"))
            for cell in page_cells:
                if cell.get("vertex") != "1":
                    continue
                style = cell.get("style", "")
                value = cell.get("value", "")
                name, props, ops = _parse_class_html(value)
                if not name:
                    continue
                cell_id = cell.get("id", "")
                id_to_name[cell_id] = name
                if "dashed=1" in style:
                    # Imported card — name only for edge targets, not a local class.
                    continue
                plain = _plain_class_name(name)
                if plain in seen_names:
                    continue
                seen_names.add(plain)
                oclass = DrawIOOoadClass(
                    name=name,
                    sequential_order=len(module.classes) + 1,
                    properties=props,
                    operations=ops,
                )
                module.classes.append(oclass)
                id_to_class[cell_id] = oclass
            if module.classes:
                model.modules.append(module)
                order += 1

            for cell in page_cells:
                if cell.get("edge") != "1":
                    continue
                src_id = cell.get("source", "")
                tgt_id = cell.get("target", "")
                src_cls = id_to_class.get(src_id)
                if src_cls is None:
                    continue
                tgt_cls = id_to_class.get(tgt_id)
                tgt_name = (
                    tgt_cls.name
                    if tgt_cls is not None
                    else id_to_name.get(tgt_id, tgt_id)
                )
                kind = _classify_edge(cell.get("style", ""))
                already = any(
                    r.target == tgt_name and (r.kind or "association") == kind
                    for r in src_cls.relationships
                )
                if not already:
                    src_cls.relationships.append(
                        Relationship(target=tgt_name, kind=kind)
                    )

        return model

    @classmethod
    def render(
        cls,
        canonical: CleanEngineeringModel,
        previous: Optional[str] = None,
        keep_positioning: bool = False,
    ) -> str:
        if _is_modules_view(canonical):
            return cls._render_modules(canonical, previous=previous)
        return cls._render_classes(
            canonical, previous=previous, keep_positioning=keep_positioning
        )

    @classmethod
    def _render_modules(
        cls,
        canonical: CleanEngineeringModel,
        previous: Optional[str] = None,
    ) -> str:
        prev_pos = _read_positions(previous) if previous else {}

        mxfile = ET.Element("mxfile")
        mxfile.set("host", "CleanEngineering.diagram.drawio")
        diagram = ET.SubElement(mxfile, "diagram")
        diagram.set("name", "Modules Context")
        diagram.set("id", "modules-context")
        model_el = ET.SubElement(diagram, "mxGraphModel")
        _set_graph_attrs(model_el, page_width="1600", page_height="1200")
        root_el = ET.SubElement(model_el, "root")
        cell0 = ET.SubElement(root_el, "mxCell")
        cell0.set("id", "0")
        cell1 = ET.SubElement(root_el, "mxCell")
        cell1.set("id", "1")
        cell1.set("parent", "0")

        system_name = canonical.name or "System"
        forest = _containment_forest(canonical.modules)
        layout = _module_containment_layout(forest)
        max_x = max((b[0] + b[2] for b in layout.bounds.values()), default=MODULE_START_X)
        max_y = max((b[1] + b[3] for b in layout.bounds.values()), default=MODULE_START_Y)
        page_w = int(max(1600, max_x + 80))
        page_h = int(max(1200, max_y + 80))
        model_el.set("pageWidth", str(page_w))
        model_el.set("pageHeight", str(page_h))

        title = ET.SubElement(root_el, "mxCell")
        title.set("id", "title")
        title.set("value", f"{system_name} - Modules Context")
        title.set("style", MODULE_TITLE_STYLE)
        title.set("parent", "1")
        title.set("vertex", "1")
        title_geo = ET.SubElement(title, "mxGeometry")
        title_geo.set("x", "40")
        title_geo.set("y", "20")
        title_geo.set("width", str(page_w - 80))
        title_geo.set("height", "32")
        title_geo.set("as", "geometry")

        subtitle = ET.SubElement(root_el, "mxCell")
        subtitle.set("id", "subtitle")
        subtitle.set(
            "value",
            "Independent modules with one-way dependencies. "
            "Arrows point toward the depended-on module (build before). "
            "Path nesting = containment; shared base terms live on the parent.",
        )
        subtitle.set("style", MODULE_SUBTITLE_STYLE)
        subtitle.set("parent", "1")
        subtitle.set("vertex", "1")
        sub_geo = ET.SubElement(subtitle, "mxGeometry")
        sub_geo.set("x", "40")
        sub_geo.set("y", "55")
        sub_geo.set("width", str(page_w - 80))
        sub_geo.set("height", "20")
        sub_geo.set("as", "geometry")

        name_to_id = dict(layout.name_to_id)

        # Parents before children so draw.io containment resolves
        for name in layout.render_order:
            module = forest.by_name[name]
            cell_id = name_to_id[name]
            parent_id = layout.parent_id.get(name, "1")
            x, y, w, h = layout.bounds[name]
            if cell_id in prev_pos and parent_id == "1":
                x, y = prev_pos[cell_id]
            style = (
                MODULE_CHILD_STYLE
                if parent_id != "1"
                else MODULE_STYLE
            )
            _create_module_cell(
                root_el,
                module,
                cell_id=cell_id,
                x=x,
                y=y,
                width=w,
                height=h,
                parent_id=parent_id,
                style=style,
            )

        edge_counter = len(forest.by_name) + 20
        for module in canonical.modules:
            src_id = name_to_id.get(module.name)
            path_parent = _path_parent(module.name)
            for dep in module.dependencies:
                if dep == path_parent:
                    continue  # containment already shows child -> parent
                tgt_id = name_to_id.get(dep)
                if not src_id or not tgt_id:
                    continue
                edge_counter += 1
                _create_module_edge(
                    root_el,
                    src_id=src_id,
                    tgt_id=tgt_id,
                    edge_id=f"dep-{edge_counter}",
                )

        ET.indent(ET.ElementTree(mxfile), space="  ")
        return ET.tostring(mxfile, encoding="unicode", xml_declaration=False)

    @classmethod
    def _render_classes(
        cls,
        canonical: CleanEngineeringModel,
        previous: Optional[str] = None,
        keep_positioning: bool = False,
    ) -> str:
        name_to_id: dict[str, str] = {}
        id_to_oclass: Dict[str, OoadClass] = {}
        for oclass in canonical.classes:
            cell_id = _slug(oclass.name)
            name_to_id[oclass.name] = cell_id
            plain = _plain_class_name(oclass.name)
            if plain and plain != oclass.name:
                name_to_id.setdefault(plain, cell_id)
            id_to_oclass[cell_id] = oclass

        relationships = _collect_relationships(canonical.classes, name_to_id)
        id_to_module = _class_module_labels(canonical.modules)
        named_modules = [m for m in canonical.modules if m.classes]

        # One Draw.io tab per aggregate/module (drawio.md); fall back to a
        # single page when the model is not partitioned.
        if len(named_modules) < 2:
            return cls._render_classes_single_page(
                canonical,
                name_to_id,
                id_to_oclass,
                relationships,
                previous=previous,
                keep_positioning=keep_positioning,
            )

        mxfile = ET.Element("mxfile")
        mxfile.set("host", "CleanEngineering.diagram.drawio")
        for module in named_modules:
            page_name = module.name.strip()
            root_el = _add_diagram_page(mxfile, page_name)
            local_ids = [_slug(c.name) for c in module.classes]
            local_set = set(local_ids)
            import_ids = _direct_import_ids(
                local_set, relationships, id_to_module, page_name
            )
            placements = _layout_page_with_imports(
                local_ids, import_ids, id_to_oclass, relationships
            )
            for iid in import_ids:
                oclass = id_to_oclass[iid]
                from_mod = id_to_module.get(iid, "other")
                x, y, _w, _h = placements[iid]
                _create_imported_class_cell(
                    root_el,
                    oclass,
                    cell_id=iid,
                    from_module=from_mod,
                    x=int(round(x)),
                    y=int(round(y)),
                )
            for lid in local_ids:
                oclass = id_to_oclass[lid]
                x, y, _w, _h = placements[lid]
                _create_class_cell(
                    root_el,
                    oclass,
                    cell_id=lid,
                    x=int(round(x)),
                    y=int(round(y)),
                )
            _render_edges_on_page(
                root_el,
                relationships,
                placements,
                local_set | set(import_ids),
                local_ids=local_set,
            )

        ET.indent(ET.ElementTree(mxfile), space="  ")
        return ET.tostring(mxfile, encoding="unicode", xml_declaration=False)

    @classmethod
    def _render_classes_single_page(
        cls,
        canonical: CleanEngineeringModel,
        name_to_id: dict[str, str],
        id_to_oclass: Dict[str, OoadClass],
        relationships: List[Tuple[str, str, str]],
        previous: Optional[str] = None,
        keep_positioning: bool = False,
    ) -> str:
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

        prev_pos = _read_positions(previous) if previous else {}
        prev_edges = _read_edges(previous) if (keep_positioning and previous) else {}
        if keep_positioning and previous:
            placements = _layout_classes_keep_positioning(
                id_to_oclass,
                relationships,
                prev_pos,
                modules=canonical.modules,
            )
        else:
            placements = _layout_classes_clustered(
                id_to_oclass,
                relationships,
                modules=canonical.modules,
                previous_positions=prev_pos if previous else None,
            )
            placements = _resolve_class_overlaps(placements)

        for oclass in canonical.classes:
            cell_id = name_to_id[oclass.name]
            x, y, _w, _h = placements[cell_id]
            _create_class_cell(
                root_el,
                oclass,
                cell_id=cell_id,
                x=int(round(x)),
                y=int(round(y)),
            )

        kept_pairs: set[Tuple[str, str]] = set()
        if keep_positioning and prev_edges:
            for src_id, tgt_id, _kind in relationships:
                existing = prev_edges.get((src_id, tgt_id))
                if existing is None:
                    continue
                _append_copied_edge(root_el, existing)
                kept_pairs.add((src_id, tgt_id))

        page_rels = [
            (s, t, k)
            for s, t, k in relationships
            if (s, t) not in kept_pairs
        ]
        _render_edges_on_page(
            root_el, page_rels, placements, set(placements.keys())
        )

        ET.indent(ET.ElementTree(mxfile), space="  ")
        return ET.tostring(mxfile, encoding="unicode", xml_declaration=False)

    @classmethod
    def sync(cls, text: str, canonical: CleanEngineeringModel) -> UpdateReport:
        return canonical.translate_from(cls.parse(text))


# ---------------------------------------------------------------------------
# View detection
# ---------------------------------------------------------------------------

def _is_modules_view(canonical: CleanEngineeringModel) -> bool:
    """True when the model is module-boundary detail only (no typed class members)."""
    if not canonical.modules:
        return False
    # canonical.classes is a flat property aggregating all module-nested classes.
    # Check it before the m.dependencies heuristic so that H1+H2 markdown (where
    # all classes live inside modules) correctly selects the class view when any
    # class has properties/operations/typed relationships.
    for oclass in canonical.classes:
        if oclass.properties or oclass.operations:
            return False
        if any(r.kind for r in oclass.relationships):
            return False
    # Prefer modules view when any module carries deps/seam terms, or no classes yet
    if any(m.dependencies or m.seam_terms for m in canonical.modules):
        return True
    if not canonical.classes:
        return True
    # Thin term names as empty classes - still modules fidelity
    return all(
        not c.properties and not c.operations and not c.relationships
        for c in canonical.classes
    )


def _looks_like_modules_diagram(mxcells: List[ET.Element]) -> bool:
    module_cells = 0
    class_cells = 0
    for cell in mxcells:
        if cell.get("vertex") != "1":
            continue
        style = cell.get("style", "")
        value = cell.get("value", "")
        if "text;" in style or style.startswith("text;"):
            continue
        if _is_module_style(style):
            module_cells += 1
            continue
        name, props, ops = _parse_class_html(value)
        if name and (props or ops or "hr size=" in value.lower()):
            class_cells += 1
        elif name and ("•" in html.unescape(value) or "-" in html.unescape(value)):
            module_cells += 1
    if module_cells and not class_cells:
        return True
    if module_cells > class_cells:
        return True
    return False


# ---------------------------------------------------------------------------
# XML helpers
# ---------------------------------------------------------------------------

def _slug(name: str) -> str:
    return re.sub(r"\W+", "-", name).lower().strip("-")


def _plain_class_name(name: str) -> str:
    """Extract the bare identifier from a CE OOAD class name.

    Strips Markdown bold markers (**), UML stereotype annotations (<<...>>), and
    trailing ``extends Base`` clauses so that
    "**Subscriber** <<Aggregate Root>> <<Entity>> extends Customer" becomes
    "Subscriber". Used to build name aliases that let relationship targets
    (which use the plain name) resolve to the correct DrawIO cell.
    """
    # Strip bold markers
    n = re.sub(r"\*+", "", name)
    # Strip stereotype annotations like "<< Value Object >>"
    n = re.sub(r"<<[^>]+>>", "", n)
    # Strip inheritance clause: "Subscriber extends Customer" -> "Subscriber"
    n = re.sub(r"\s+extends\s+.+$", "", n, flags=re.IGNORECASE)
    return n.strip()


def _extends_base_name(name: str) -> Optional[str]:
    """Return the base type from an ``extends Base`` clause on a class heading, if any."""
    n = re.sub(r"\*+", "", name)
    n = re.sub(r"<<[^>]+>>", "", n)
    m = re.search(r"\bextends\s+([A-Z]\w*)", n, flags=re.IGNORECASE)
    return m.group(1) if m else None


def _is_module_style(style: str) -> bool:
    return (
        _MODULE_MARKER in style
        or _MODULE_CHILD_MARKER in style
        or "fillColor=#1a3a6e" in style
        or "fillColor=#dae8fc" in style
    )


def _path_parent(name: str) -> Optional[str]:
    if "/" not in name:
        return None
    return name.rsplit("/", 1)[0]


def _class_height(oclass: OoadClass) -> int:
    n_content = len(oclass.properties) + len(oclass.operations)
    return max(CELL_MIN_HEIGHT, 30 + n_content * LINE_HEIGHT + 2 * SECTION_PAD)


def _module_header_height(module: Module) -> int:
    terms = module.public_terms()
    if not terms:
        # Folder container / purpose-only header
        return MODULE_HEADER_HEIGHT + MODULE_LINE_HEIGHT
    n = min(MODULE_MAX_SEAM_BULLETS, len(terms))
    if len(terms) > MODULE_MAX_SEAM_BULLETS:
        n += 1
    return max(MODULE_CELL_MIN_HEIGHT, MODULE_HEADER_HEIGHT + n * MODULE_LINE_HEIGHT + 24)


def _module_height(module: Module) -> int:
    return _module_header_height(module)


def _set_graph_attrs(
    el: ET.Element,
    page_width: str = "1654",
    page_height: str = "1169",
) -> None:
    for k, v in [
        ("dx", "1200"), ("dy", "800"), ("grid", "1"), ("gridSize", "10"),
        ("guides", "1"), ("tooltips", "1"), ("connect", "1"), ("arrows", "1"),
        ("fold", "1"), ("page", "1"), ("pageScale", "1"),
        ("pageWidth", page_width), ("pageHeight", page_height),
        ("math", "0"), ("shadow", "0"),
    ]:
        el.set(k, v)


class _ContainmentForest:
    def __init__(
        self,
        by_name: Dict[str, Module],
        children_of: Dict[str, List[str]],
        roots: List[str],
        synthetic: set,
    ) -> None:
        self.by_name = by_name
        self.children_of = children_of
        self.roots = roots
        self.synthetic = synthetic


class _ContainmentLayout:
    def __init__(self) -> None:
        # name -> (x, y, w, h) - absolute for roots; relative for nested children
        self.bounds: Dict[str, Tuple[float, float, float, float]] = {}
        self.parent_id: Dict[str, str] = {}
        self.name_to_id: Dict[str, str] = {}
        self.render_order: List[str] = []


def _containment_forest(modules: List[Module]) -> _ContainmentForest:
    by_name: Dict[str, Module] = {m.name: m for m in modules}
    synthetic: set = set()

    # Ensure every path prefix exists (folder containers when missing)
    needed: List[str] = []
    for m in modules:
        p = _path_parent(m.name)
        while p:
            if p not in by_name:
                needed.append(p)
            p = _path_parent(p)
    for prefix in sorted(set(needed), key=lambda s: s.count("/")):
        by_name[prefix] = Module(
            name=prefix,
            sequential_order=0,
            description="nested modules",
            seam_terms=[],
        )
        synthetic.add(prefix)

    children_of: Dict[str, List[str]] = {n: [] for n in by_name}
    roots: List[str] = []
    for name in by_name:
        parent = _path_parent(name)
        if parent and parent in by_name:
            children_of[parent].append(name)
        else:
            roots.append(name)

    for parent in children_of:
        children_of[parent].sort(
            key=lambda n: (by_name[n].sequential_order or 0, n)
        )
    roots.sort(key=lambda n: (by_name[n].sequential_order or 0, n))
    return _ContainmentForest(by_name, children_of, roots, synthetic)


def _external_deps(module: Module) -> List[str]:
    """Dependencies that are not the path-parent (containment handles that)."""
    parent = _path_parent(module.name)
    return [d for d in module.dependencies if d != parent]


def _module_dep_depth(
    name: str,
    forest: _ContainmentForest,
    cache: Dict[str, int],
    visiting: Optional[set] = None,
) -> int:
    """Depth for top-level placement units (roots only)."""
    if name in cache:
        return cache[name]
    visiting = visiting or set()
    if name in visiting:
        cache[name] = 0
        return 0
    visiting.add(name)
    module = forest.by_name[name]
    dep_names = list(_external_deps(module))
    # Folder containers: depth from nested children's external deps
    if name in forest.synthetic or (
        forest.children_of.get(name) and not module.public_terms() and not module.dependencies
    ):
        for child in forest.children_of.get(name, []):
            dep_names.extend(_external_deps(forest.by_name[child]))
    # Map deps to root placement units
    root_deps: List[str] = []
    for dep in dep_names:
        if dep not in forest.by_name:
            continue
        cur = dep
        while True:
            parent = _path_parent(cur)
            if not parent or parent not in forest.by_name:
                break
            cur = parent
        if cur in forest.roots:
            root_deps.append(cur)
    depths = [
        _module_dep_depth(dep, forest, cache, visiting)
        for dep in root_deps
        if dep != name
    ]
    visiting.remove(name)
    d = 0 if not depths else 1 + max(depths)
    cache[name] = d
    return d


def _size_subtree(name: str, forest: _ContainmentForest) -> Tuple[float, float]:
    """Return (width, height) for a module cell including nested children."""
    module = forest.by_name[name]
    kids = forest.children_of.get(name, [])
    header_h = float(_module_header_height(module))
    if not kids:
        return float(MODULE_CELL_WIDTH), max(float(MODULE_CELL_MIN_HEIGHT), header_h)

    child_sizes = [_size_subtree(c, forest) for c in kids]
    cols = min(MODULE_CHILD_COLS, len(kids))
    rows = (len(kids) + cols - 1) // cols
    col_widths = [0.0] * cols
    row_heights = [0.0] * rows
    for i, (cw, ch) in enumerate(child_sizes):
        c, r = i % cols, i // cols
        col_widths[c] = max(col_widths[c], cw)
        row_heights[r] = max(row_heights[r], ch)
    grid_w = sum(col_widths) + MODULE_CHILD_GAP * (cols - 1)
    grid_h = sum(row_heights) + MODULE_CHILD_GAP * (rows - 1)
    width = max(
        float(MODULE_CELL_WIDTH),
        grid_w + 2 * MODULE_CHILD_PAD_X,
    )
    height = header_h + grid_h + 2 * MODULE_CHILD_PAD_Y
    return width, height


def _place_subtree(
    name: str,
    forest: _ContainmentForest,
    layout: _ContainmentLayout,
    abs_x: float,
    abs_y: float,
    parent_id: str,
) -> None:
    module = forest.by_name[name]
    w, h = _size_subtree(name, forest)
    if parent_id == "1":
        layout.bounds[name] = (abs_x, abs_y, w, h)
    # nested bounds filled by parent when placing children (relative)
    synthetic = name in forest.synthetic
    cell_id = f"nest-{_slug(name)}" if synthetic else (_slug(name) or name)
    layout.name_to_id[name] = cell_id
    layout.parent_id[name] = parent_id
    layout.render_order.append(name)

    kids = forest.children_of.get(name, [])
    if not kids:
        return
    header_h = float(_module_header_height(module))
    cols = min(MODULE_CHILD_COLS, len(kids))
    child_sizes = [_size_subtree(c, forest) for c in kids]
    col_widths = [0.0] * cols
    rows = (len(kids) + cols - 1) // cols
    row_heights = [0.0] * rows
    for i, (cw, ch) in enumerate(child_sizes):
        c, r = i % cols, i // cols
        col_widths[c] = max(col_widths[c], cw)
        row_heights[r] = max(row_heights[r], ch)

    for i, child in enumerate(kids):
        c, r = i % cols, i // cols
        rel_x = MODULE_CHILD_PAD_X + sum(col_widths[:c]) + MODULE_CHILD_GAP * c
        rel_y = header_h + MODULE_CHILD_PAD_Y + sum(row_heights[:r]) + MODULE_CHILD_GAP * r
        cw, ch = child_sizes[i]
        layout.bounds[child] = (rel_x, rel_y, cw, ch)
        _place_subtree(
            child,
            forest,
            layout,
            abs_x + rel_x,
            abs_y + rel_y,
            parent_id=cell_id,
        )


def _module_containment_layout(forest: _ContainmentForest) -> _ContainmentLayout:
    """Layer roots by dependency depth; nest path children inside parents."""
    layout = _ContainmentLayout()
    if not forest.roots:
        return layout
    cache: Dict[str, int] = {}
    layers: Dict[int, List[str]] = {}
    for root in forest.roots:
        d = _module_dep_depth(root, forest, cache)
        layers.setdefault(d, []).append(root)
    for d in layers:
        layers[d].sort(
            key=lambda n: (forest.by_name[n].sequential_order or 0, n)
        )

    # Column width = max root width in that layer
    layer_widths: Dict[int, float] = {}
    for d, names in layers.items():
        layer_widths[d] = max(_size_subtree(n, forest)[0] for n in names)

    x_cursor = float(MODULE_START_X)
    for d in sorted(layers):
        y = float(MODULE_START_Y)
        for name in layers[d]:
            _place_subtree(name, forest, layout, x_cursor, y, parent_id="1")
            _w, h = layout.bounds[name][2], layout.bounds[name][3]
            y += h + MODULE_ROW_GAP
        x_cursor += layer_widths[d] + MODULE_COL_GAP
    return layout


def _read_positions(previous: str) -> Dict[str, Tuple[float, float]]:
    out: Dict[str, Tuple[float, float]] = {}
    try:
        root = ET.fromstring(previous)
    except ET.ParseError:
        return out
    for cell in root.iter("mxCell"):
        if cell.get("vertex") != "1":
            continue
        cell_id = cell.get("id", "")
        geo = cell.find("mxGeometry")
        if geo is None or not cell_id:
            continue
        x = geo.get("x")
        y = geo.get("y")
        if x is None or y is None:
            continue
        try:
            out[cell_id] = (float(x), float(y))
        except ValueError:
            continue
    return out


def _read_edges(previous: str) -> Dict[Tuple[str, str], ET.Element]:
    """Index existing DrawIO edges by (source, target) so they can be reused."""
    out: Dict[Tuple[str, str], ET.Element] = {}
    try:
        root = ET.fromstring(previous)
    except ET.ParseError:
        return out
    for cell in root.iter("mxCell"):
        if cell.get("edge") != "1":
            continue
        src = cell.get("source")
        tgt = cell.get("target")
        if src and tgt:
            out[(src, tgt)] = cell
    return out


def _append_copied_edge(root_el: ET.Element, edge: ET.Element) -> None:
    root_el.append(copy.deepcopy(edge))


def _place_new_classes_clear_of_existing(
    new_placements: Dict[str, Tuple[float, float, float, float]],
    existing_placements: Dict[str, Tuple[float, float, float, float]],
) -> Dict[str, Tuple[float, float, float, float]]:
    """Shift newly laid-out classes so they do not overlap kept positions."""
    if not new_placements:
        return new_placements
    if not existing_placements:
        return new_placements
    max_right = max(x + w for x, _y, w, _h in existing_placements.values())
    min_new_x = min(x for x, _y, _w, _h in new_placements.values())
    shift_x = (max_right + CLUSTER_GAP_X) - min_new_x
    if shift_x < 0:
        shift_x = 0.0
    shifted = {
        cid: (x + shift_x, y, w, h)
        for cid, (x, y, w, h) in new_placements.items()
    }
    for cid in list(shifted):
        while any(
            _rects_overlap(shifted[cid], geo, gap=OVERLAP_GAP)
            for geo in existing_placements.values()
        ):
            x, y, w, h = shifted[cid]
            shifted[cid] = (x, y + OVERLAP_GAP, w, h)
    return shifted


def _layout_classes_keep_positioning(
    id_to_oclass: Dict[str, OoadClass],
    relationships: List[Tuple[str, str, str]],
    previous_positions: Dict[str, Tuple[float, float]],
    modules: Optional[List[Module]] = None,
) -> Dict[str, Tuple[float, float, float, float]]:
    """Keep existing class positions; layout only classes that are new."""
    placements: Dict[str, Tuple[float, float, float, float]] = {}
    new_ids: List[str] = []
    for cid, oclass in id_to_oclass.items():
        if cid in previous_positions:
            x, y = previous_positions[cid]
            placements[cid] = (
                x,
                y,
                float(CELL_WIDTH),
                float(_class_height(oclass)),
            )
        else:
            new_ids.append(cid)
    if not new_ids:
        return placements
    new_map = {cid: id_to_oclass[cid] for cid in new_ids}
    new_rels = [
        (src, tgt, kind)
        for src, tgt, kind in relationships
        if src in new_map and tgt in new_map
    ]
    new_placements = _layout_classes_clustered(
        new_map, new_rels, modules=modules
    )
    new_placements = _place_new_classes_clear_of_existing(
        new_placements, placements
    )
    placements.update(new_placements)
    return placements


def _build_module_html(module: Module) -> str:
    name_html = html.escape(module.name)
    purpose = module.description.strip() or "{one-line purpose}"
    purpose_line = purpose.splitlines()[0].strip()
    if len(purpose_line) > MODULE_PURPOSE_MAX_CHARS:
        purpose_line = purpose_line[: MODULE_PURPOSE_MAX_CHARS - 1].rstrip() + "..."
    purpose_html = html.escape(purpose_line)
    terms = module.public_terms()
    if terms:
        shown = terms[:MODULE_MAX_SEAM_BULLETS]
        bullets = "<br>".join(f"• {html.escape(t)}" for t in shown)
        if len(terms) > MODULE_MAX_SEAM_BULLETS:
            bullets += "<br>• ..."
        return (
            f'<b style="font-size: 14px;">{name_html}</b><br>'
            f"<i>{purpose_html}</i><hr>"
            f"{bullets}"
        )
    return (
        f'<b style="font-size: 14px;">{name_html}</b><br>'
        f"<i>{purpose_html}</i>"
    )


def _create_module_cell(
    root_el: ET.Element,
    module: Module,
    cell_id: str,
    x: float,
    y: float,
    width: Optional[float] = None,
    height: Optional[float] = None,
    parent_id: str = "1",
    style: str = MODULE_STYLE,
) -> ET.Element:
    cell = ET.SubElement(root_el, "mxCell")
    cell.set("id", cell_id)
    cell.set("value", _build_module_html(module))
    cell.set("style", style)
    cell.set("vertex", "1")
    cell.set("parent", parent_id)
    geo = ET.SubElement(cell, "mxGeometry")
    geo.set("x", str(int(x)))
    geo.set("y", str(int(y)))
    geo.set("width", str(int(width if width is not None else MODULE_CELL_WIDTH)))
    geo.set(
        "height",
        str(int(height if height is not None else _module_height(module))),
    )
    geo.set("as", "geometry")
    return cell


def _create_module_edge(
    root_el: ET.Element,
    src_id: str,
    tgt_id: str,
    edge_id: str,
) -> ET.Element:
    cell = ET.SubElement(root_el, "mxCell")
    cell.set("id", edge_id)
    cell.set("value", "")
    cell.set("style", MODULE_DEP_EDGE_STYLE)
    cell.set("edge", "1")
    cell.set("source", src_id)
    cell.set("target", tgt_id)
    cell.set("parent", "1")
    geo = ET.SubElement(cell, "mxGeometry")
    geo.set("relative", "1")
    geo.set("as", "geometry")
    return cell


def _parse_module_html(value: str) -> Tuple[Optional[str], str, List[str]]:
    text = html.unescape(value)
    # Prefer <b style=...>...</b>, fall back to <b>...</b>
    m = re.search(r"<b[^>]*>([^<]+)</b>", text, re.IGNORECASE)
    name = m.group(1).strip() if m else None
    if not name:
        return None, "", []

    purpose = ""
    im = re.search(r"<i[^>]*>([^<]*)</i>", text, re.IGNORECASE)
    if im:
        purpose = im.group(1).strip()

    terms: List[str] = []
    for bullet in re.findall(r"[•\-]\s*([^<]+)", text):
        term = bullet.strip()
        if term and not term.startswith("{"):
            terms.append(term)
        elif term.startswith("{") and term.endswith("}"):
            continue
        elif term:
            terms.append(term)

    # Also accept <li> items if someone pasted ul markup
    if not terms:
        for li in re.findall(r"<li[^>]*>(?:<[^>]+>)*([^<]+)", text, re.IGNORECASE):
            term = li.strip()
            if term and "stack" not in term.lower():
                terms.append(term)

    return name, purpose, terms


def _display_class_name(name: str) -> str:
    """Human-facing class title: plain name plus stereotypes, without ``extends``."""
    n = re.sub(r"\*+", "", name)
    base = _plain_class_name(name)
    stereotypes = re.findall(r"<<[^>]+>>", n)
    if stereotypes:
        return f"{base} {' '.join(s.strip() for s in stereotypes)}"
    return base


def _build_class_html(oclass: OoadClass) -> str:
    name_html = html.escape(_display_class_name(oclass.name))
    props_html = "".join(
        f"+ {html.escape(p.name)}{': ' + html.escape(p.type_hint) if p.type_hint else ''}<br/>"
        for p in oclass.properties
    ) or "<br/>"
    ops_html = "".join(
        f"{'- ' if op.name.startswith('_') else '+ '}{html.escape(op.name)}"
        f"({', '.join(op.parameters)})"
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


def _module_tab_label(module_name: str) -> str:
    """Short label for «from: …» (leading part of an H1 heading)."""
    name = module_name.strip()
    for sep in (" — ", " – ", " - ", "—", "–"):
        if sep in name:
            return name.split(sep, 1)[0].strip()
    return name


def _class_module_labels(modules: List[Module]) -> dict[str, str]:
    """Map class cell id → owning module short label for import stereotypes."""
    out: dict[str, str] = {}
    for module in modules:
        label = _module_tab_label(module.name)
        for oclass in module.classes:
            out[_slug(oclass.name)] = label
            plain = _plain_class_name(oclass.name)
            if plain:
                out.setdefault(_slug(plain), label)
    return out


def _collect_relationships(
    classes: List[OoadClass],
    name_to_id: dict[str, str],
) -> List[Tuple[str, str, str]]:
    relationships = [
        (name_to_id[c.name], name_to_id[rel.target], rel.kind or "association")
        for c in classes
        for rel in c.relationships
        if rel.target in name_to_id
    ]
    for oclass in classes:
        base = _extends_base_name(oclass.name)
        if base and base in name_to_id:
            pair = (name_to_id[oclass.name], name_to_id[base], "inheritance")
            if pair not in relationships:
                relationships.append(pair)
    return relationships


def _direct_import_ids(
    local_ids: set[str],
    relationships: List[Tuple[str, str, str]],
    id_to_module: dict[str, str],
    local_module_name: str,
) -> List[str]:
    """Foreign class ids with a direct link from this aggregate.

    Imports:
    - targets of edges that leave a local class (local → foreign)
    - foreign subtypes that inherit into a local base (foreign → local, inheritance)

    Inbound association sources stay on the other aggregate's tab.
    """
    local_label = _module_tab_label(local_module_name)
    imports: set[str] = set()
    for src, tgt, kind in relationships:
        kind_l = (kind or "association").lower()
        if src in local_ids and tgt not in local_ids:
            if id_to_module.get(tgt, "") != local_label:
                imports.add(tgt)
        elif (
            tgt in local_ids
            and src not in local_ids
            and kind_l == "inheritance"
            and id_to_module.get(src, "") != local_label
        ):
            imports.add(src)
    return sorted(imports)


def _build_imported_class_html(oclass: OoadClass, from_module: str) -> str:
    """Compact imported card: «from: Module», name, key properties only."""
    name_html = html.escape(_display_class_name(oclass.name))
    from_html = html.escape(f"«from: {from_module}»")
    key_props = oclass.properties[:4]
    props_html = "".join(
        f"+ {html.escape(p.name)}"
        f"{': ' + html.escape(p.type_hint) if p.type_hint else ''}<br/>"
        for p in key_props
    ) or "<br/>"
    return (
        f'<p style="margin:0px;margin-top:2px;text-align:center;font-size:10px;">'
        f"<i>{from_html}</i></p>"
        f'<p style="margin:0px;text-align:center;"><b>{name_html}</b></p>'
        f'<hr size="1"/>'
        f'<p style="margin:0px;margin-left:4px;font-size:10px;">{props_html}</p>'
        f'<hr size="1"/>'
        f'<p style="margin:0px;margin-left:4px;font-size:10px;"><br/></p>'
    )


def _imported_class_height(oclass: OoadClass) -> int:
    n = min(4, len(oclass.properties)) + 2
    return max(CELL_MIN_HEIGHT - 10, 30 + n * LINE_HEIGHT + 2 * SECTION_PAD)


def _create_imported_class_cell(
    root_el: ET.Element,
    oclass: OoadClass,
    cell_id: str,
    from_module: str,
    x: int,
    y: int,
) -> ET.Element:
    cell = ET.SubElement(root_el, "mxCell")
    cell.set("id", cell_id)
    cell.set("value", _build_imported_class_html(oclass, from_module))
    cell.set("style", IMPORTED_CLASS_STYLE)
    cell.set("vertex", "1")
    cell.set("parent", "1")
    geo = ET.SubElement(cell, "mxGeometry")
    geo.set("x", str(x))
    geo.set("y", str(y))
    geo.set("width", str(CELL_WIDTH))
    geo.set("height", str(_imported_class_height(oclass)))
    geo.set("as", "geometry")
    return cell


def _layout_page_with_imports(
    local_ids: List[str],
    import_ids: List[str],
    id_to_oclass: Dict[str, OoadClass],
    relationships: List[Tuple[str, str, str]],
) -> Dict[str, Tuple[float, float, float, float]]:
    """Pack locals tightly; inheritance imports above, others beside linkers."""
    local_set = set(local_ids)
    page_rels = [
        (s, t, k)
        for s, t, k in relationships
        if s in local_set and t in local_set
    ]
    local_map, _width, _height = _pack_cluster(
        local_ids,
        id_to_oclass,
        float(START_X),
        float(START_Y),
        page_rels,
        cols=3,
    )
    placements: Dict[str, Tuple[float, float, float, float]] = dict(local_map)

    if not import_ids:
        return _resolve_class_overlaps(placements)

    def _linkers_for(iid: str) -> List[Tuple[str, str]]:
        out: List[Tuple[str, str]] = []
        for s, t, k in relationships:
            kind = (k or "association").lower()
            if s == iid and t in placements:
                out.append((t, kind))
            elif t == iid and s in placements:
                out.append((s, kind))
        return out

    inheritance_parents = []  # import is base — sit above locals
    inheritance_children = []  # import is subtype — sit below local base
    for iid in import_ids:
        links = _linkers_for(iid)
        if any(k == "inheritance" for _lid, k in links):
            # child → parent: if import is source, it's the subtype.
            if any(
                s == iid and t in placements and (k or "").lower() == "inheritance"
                for s, t, k in relationships
            ):
                inheritance_children.append(iid)
            else:
                inheritance_parents.append(iid)
    beside_ids = [
        iid
        for iid in import_ids
        if iid not in inheritance_parents and iid not in inheritance_children
    ]

    if inheritance_parents:
        band_h = (
            max(
                float(_imported_class_height(id_to_oclass[i]))
                for i in inheritance_parents
            )
            + INNER_ROW_GAP * 2
        )
        placements = {
            cid: (x, y + band_h, w, h) for cid, (x, y, w, h) in placements.items()
        }
        used: List[Tuple[float, float, float, float]] = []
        for iid in inheritance_parents:
            h = float(_imported_class_height(id_to_oclass[iid]))
            links = _linkers_for(iid)
            primary = min(
                (lid for lid, _k in links),
                key=lambda lid: (placements[lid][1], placements[lid][0]),
            )
            x = placements[primary][0]
            y = float(START_Y)
            candidate = (x, y, float(CELL_WIDTH), h)
            for _ in range(12):
                if all(
                    not _rects_overlap(candidate, geo, gap=OVERLAP_GAP)
                    for geo in used
                ):
                    break
                x += CELL_WIDTH + INNER_COL_GAP
                candidate = (x, y, float(CELL_WIDTH), h)
            placements[iid] = candidate
            used.append(candidate)

    # Subtype imports sit just below their local base (base-above-derived).
    child_slots: dict[str, int] = {}
    for iid in inheritance_children:
        h = float(_imported_class_height(id_to_oclass[iid]))
        links = _linkers_for(iid)
        primary = min(
            (lid for lid, _k in links),
            key=lambda lid: (placements[lid][1], placements[lid][0]),
        )
        px, py, _pw, ph = placements[primary]
        slot = child_slots.get(primary, 0)
        child_slots[primary] = slot + 1
        x = px + slot * (CELL_WIDTH + INNER_COL_GAP)
        y = py + ph + INNER_ROW_GAP
        placements[iid] = (x, y, float(CELL_WIDTH), h)

    # Association imports: fan into a compact 2-col grid to the right of each hub.
    from collections import defaultdict

    by_hub: dict[str, List[str]] = defaultdict(list)
    orphan_imports: List[str] = []
    for iid in beside_ids:
        links = _linkers_for(iid)
        if not links:
            orphan_imports.append(iid)
            continue
        ys = sorted(placements[lid][1] for lid, _k in links)
        mid_y = ys[len(ys) // 2]
        primary = min(
            (lid for lid, _k in links),
            key=lambda lid: (
                abs(placements[lid][1] - mid_y),
                placements[lid][0],
            ),
        )
        by_hub[primary].append(iid)

    fan_cols = 2
    for hub, iids in by_hub.items():
        hx, hy, _hw, _hh = placements[hub]
        for idx, iid in enumerate(iids):
            h = float(_imported_class_height(id_to_oclass[iid]))
            col = idx % fan_cols
            row = idx // fan_cols
            x = hx + CELL_WIDTH + INNER_COL_GAP + col * (CELL_WIDTH + INNER_COL_GAP)
            y = hy + row * (h + INNER_ROW_GAP)
            candidate = (x, y, float(CELL_WIDTH), h)
            # If blocked, drop to the next free row under the hub fan.
            guard = 0
            while any(
                _rects_overlap(candidate, geo, gap=OVERLAP_GAP)
                for oid, geo in placements.items()
                if oid != iid
            ) and guard < 20:
                guard += 1
                row += 1
                y = hy + row * (h + INNER_ROW_GAP)
                candidate = (x, y, float(CELL_WIDTH), h)
            placements[iid] = candidate

    for iid in orphan_imports:
        h = float(_imported_class_height(id_to_oclass[iid]))
        placements[iid] = (
            float(START_X),
            float(START_Y),
            float(CELL_WIDTH),
            h,
        )

    return _resolve_class_overlaps(placements, prefer_move=set(import_ids))


def _add_diagram_page(mxfile: ET.Element, page_name: str) -> ET.Element:
    diagram = ET.SubElement(mxfile, "diagram")
    diagram.set("name", page_name)
    diagram.set("id", f"page-{_slug(page_name)}")
    model_el = ET.SubElement(diagram, "mxGraphModel")
    _set_graph_attrs(model_el)
    root_el = ET.SubElement(model_el, "root")
    cell0 = ET.SubElement(root_el, "mxCell")
    cell0.set("id", "0")
    cell1 = ET.SubElement(root_el, "mxCell")
    cell1.set("id", "1")
    cell1.set("parent", "0")
    return root_el


def _render_edges_on_page(
    root_el: ET.Element,
    relationships: List[Tuple[str, str, str]],
    placements: Dict[str, Tuple[float, float, float, float]],
    page_ids: set[str],
    local_ids: Optional[set[str]] = None,
) -> None:
    """Wire edges present on this page.

    When *local_ids* is set (per-aggregate tabs), only draw:
    - edges that leave a local class (local → local/import)
    - inheritance into a local base (import → local, inheritance)

    Never import↔import, and never inbound association from an import.
    """
    page_rels = [
        (s, t, k)
        for s, t, k in relationships
        if s in page_ids
        and t in page_ids
        and (
            local_ids is None
            or s in local_ids
            or (
                t in local_ids
                and (k or "").lower() == "inheritance"
            )
        )
    ]
    edge_specs: List[dict] = []
    for src_id, tgt_id, kind in page_rels:
        exit_side, entry_side = _preferred_sides(
            placements[src_id], placements[tgt_id]
        )
        edge_specs.append(
            {
                "src_id": src_id,
                "tgt_id": tgt_id,
                "kind": kind,
                "exit_side": exit_side,
                "entry_side": entry_side,
            }
        )
    _assign_distinct_anchors(edge_specs)

    def _edge_sort_key(spec: dict) -> Tuple[int, float, str]:
        s = placements[spec["src_id"]]
        t = placements[spec["tgt_id"]]
        dist = abs((s[0] + s[2] / 2) - (t[0] + t[2] / 2)) + abs(
            (s[1] + s[3] / 2) - (t[1] + t[3] / 2)
        )
        ownership = 0 if _ownership_kinds(spec["kind"]) else 1
        return (ownership, dist, spec["src_id"])

    edge_specs.sort(key=_edge_sort_key)
    used_ids = {cell.get("id", "") for cell in root_el.iter("mxCell")}
    numeric_ids = [int(i) for i in used_ids if i.isdigit()]
    edge_counter = max(numeric_ids) if numeric_ids else len(page_ids) + 10
    routed_segments: List[List[Tuple[Tuple[float, float], Tuple[float, float]]]] = []
    for lane_idx, spec in enumerate(edge_specs):
        edge_counter += 1
        exit_x, exit_y = _side_anchor(spec["exit_side"], spec["exit_frac"])
        entry_x, entry_y = _side_anchor(spec["entry_side"], spec["entry_frac"])
        obstacles = [
            geo
            for cid, geo in placements.items()
            if cid not in (spec["src_id"], spec["tgt_id"])
        ]
        waypoints = _route_waypoints(
            placements[spec["src_id"]],
            placements[spec["tgt_id"]],
            spec["exit_side"],
            spec["entry_side"],
            spec["exit_frac"],
            spec["entry_frac"],
            obstacles=obstacles,
            lane=lane_idx * ROUTE_LANE_STEP,
            avoid_segments=routed_segments,
            all_placements=placements,
        )
        _create_edge(
            root_el,
            src_id=spec["src_id"],
            tgt_id=spec["tgt_id"],
            kind=spec["kind"],
            edge_id=str(edge_counter),
            exit_x=exit_x,
            exit_y=exit_y,
            entry_x=entry_x,
            entry_y=entry_y,
            waypoints=waypoints,
        )
        routed_segments.append(
            _segments_from_route(
                placements[spec["src_id"]],
                placements[spec["tgt_id"]],
                spec["exit_side"],
                spec["entry_side"],
                spec["exit_frac"],
                spec["entry_frac"],
                waypoints,
            )
        )


def _create_edge(
    root_el: ET.Element,
    src_id: str,
    tgt_id: str,
    kind: str,
    edge_id: str,
    exit_x: Optional[float] = None,
    exit_y: Optional[float] = None,
    entry_x: Optional[float] = None,
    entry_y: Optional[float] = None,
    waypoints: Optional[List[Tuple[float, float]]] = None,
) -> ET.Element:
    style = EDGE_STYLES.get(kind, DEFAULT_EDGE_STYLE)
    anchor_parts: List[str] = []
    if exit_x is not None:
        anchor_parts.append(f"exitX={exit_x}")
    if exit_y is not None:
        anchor_parts.append(f"exitY={exit_y}")
    if exit_x is not None or exit_y is not None:
        anchor_parts.extend(["exitDx=0", "exitDy=0"])
    if entry_x is not None:
        anchor_parts.append(f"entryX={entry_x}")
    if entry_y is not None:
        anchor_parts.append(f"entryY={entry_y}")
    if entry_x is not None or entry_y is not None:
        anchor_parts.extend(["entryDx=0", "entryDy=0"])
    if anchor_parts:
        style = style.rstrip(";") + ";" + ";".join(anchor_parts) + ";"

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
    if waypoints:
        arr = ET.SubElement(geo, "Array")
        arr.set("as", "points")
        for wx, wy in waypoints:
            pt = ET.SubElement(arr, "mxPoint")
            pt.set("x", str(int(round(wx))))
            pt.set("y", str(int(round(wy))))
    return cell


def _rects_overlap(
    a: Tuple[float, float, float, float],
    b: Tuple[float, float, float, float],
    gap: float = 0.0,
) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return (
        ax < bx + bw + gap
        and ax + aw + gap > bx
        and ay < by + bh + gap
        and ay + ah + gap > by
    )


def _resolve_class_overlaps(
    placements: Dict[str, Tuple[float, float, float, float]],
    prefer_move: Optional[set[str]] = None,
) -> Dict[str, Tuple[float, float, float, float]]:
    """Push overlapping class boxes apart — prefer sideways on the same row.

    *prefer_move* ids (e.g. imports) are shifted right instead of shoving local
    packs down into long vertical spines.
    """
    prefer_move = prefer_move or set()
    ids = list(placements.keys())
    for _ in range(len(ids) * len(ids) + 1):
        moved = False
        for i, a in enumerate(ids):
            for b in ids[i + 1 :]:
                if not _rects_overlap(placements[a], placements[b], gap=OVERLAP_GAP):
                    continue
                ax, ay, aw, ah = placements[a]
                bx, by, bw, bh = placements[b]
                if a in prefer_move and b not in prefer_move:
                    placements[a] = (bx + bw + OVERLAP_GAP, ay, aw, ah)
                elif b in prefer_move and a not in prefer_move:
                    placements[b] = (ax + aw + OVERLAP_GAP, by, bw, bh)
                else:
                    same_row = abs(ay - by) <= max(ah, bh) * 0.6
                    if same_row:
                        if ax <= bx:
                            placements[b] = (ax + aw + OVERLAP_GAP, by, bw, bh)
                        else:
                            placements[a] = (bx + bw + OVERLAP_GAP, ay, aw, ah)
                    elif ay <= by:
                        placements[b] = (bx, ay + ah + OVERLAP_GAP, bw, bh)
                    else:
                        placements[a] = (ax, by + bh + OVERLAP_GAP, aw, ah)
                moved = True
        if not moved:
            break
    return placements


def _preferred_sides(
    src: Tuple[float, float, float, float],
    tgt: Tuple[float, float, float, float],
) -> Tuple[str, str]:
    sx, sy, sw, sh = src
    tx, ty, tw, th = tgt
    scx, scy = sx + sw / 2.0, sy + sh / 2.0
    tcx, tcy = tx + tw / 2.0, ty + th / 2.0
    dx, dy = tcx - scx, tcy - scy
    # Prefer vertical attachment when boxes sit on different rows so routes
    # use the inter-row highway instead of punching through a middle column.
    if abs(dy) >= max(abs(dx) * 0.6, (sh + th) * 0.25):
        if dy >= 0:
            return "bottom", "top"
        return "top", "bottom"
    if abs(dx) >= abs(dy):
        if dx >= 0:
            return "right", "left"
        return "left", "right"
    if dy >= 0:
        return "bottom", "top"
    return "top", "bottom"


def _side_anchor(side: str, frac: float) -> Tuple[float, float]:
    if side == "top":
        return frac, 0.0
    if side == "bottom":
        return frac, 1.0
    if side == "left":
        return 0.0, frac
    return 1.0, frac


def _distribute_fracs(count: int) -> List[float]:
    if count <= 1:
        return [0.5]
    return [round(0.15 + 0.7 * i / (count - 1), 3) for i in range(count)]


def _assign_distinct_anchors(edge_specs: List[dict]) -> None:
    from collections import defaultdict

    exit_groups: dict[Tuple[str, str], List[int]] = defaultdict(list)
    entry_groups: dict[Tuple[str, str], List[int]] = defaultdict(list)
    for idx, spec in enumerate(edge_specs):
        exit_groups[(spec["src_id"], spec["exit_side"])].append(idx)
        entry_groups[(spec["tgt_id"], spec["entry_side"])].append(idx)

    for idxs in exit_groups.values():
        for frac, idx in zip(_distribute_fracs(len(idxs)), idxs):
            edge_specs[idx]["exit_frac"] = frac
    for idxs in entry_groups.values():
        for frac, idx in zip(_distribute_fracs(len(idxs)), idxs):
            edge_specs[idx]["entry_frac"] = frac


def _point_on_side(
    geo: Tuple[float, float, float, float],
    side: str,
    frac: float,
) -> Tuple[float, float]:
    x, y, w, h = geo
    if side == "top":
        return x + w * frac, y
    if side == "bottom":
        return x + w * frac, y + h
    if side == "left":
        return x, y + h * frac
    return x + w, y + h * frac


def _outward_point(
    geo: Tuple[float, float, float, float],
    side: str,
    frac: float,
    clearance: float,
) -> Tuple[float, float]:
    ax, ay = _point_on_side(geo, side, frac)
    if side == "top":
        return ax, ay - clearance
    if side == "bottom":
        return ax, ay + clearance
    if side == "left":
        return ax - clearance, ay
    return ax + clearance, ay


def _polyline_hits_obstacle(
    points: List[Tuple[float, float]],
    obstacles: List[Tuple[float, float, float, float]],
    margin: float = 4.0,
) -> bool:
    from context_tools.clean_engineering.class_model.drawio.drawio_tools import (
        _line_intersects_rect,
    )

    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        for ox, oy, ow, oh in obstacles:
            if _line_intersects_rect(x1, y1, x2, y2, ox, oy, ow, oh, margin=margin):
                return True
    return False


def _dedupe_points(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    out: List[Tuple[float, float]] = []
    for pt in points:
        if not out or abs(out[-1][0] - pt[0]) > 0.5 or abs(out[-1][1] - pt[1]) > 0.5:
            out.append(pt)
    return out


def _column_gutters(placements: Dict[str, Tuple[float, float, float, float]]) -> List[float]:
    """Vertical channel x positions: page margins + midpoints between class columns."""
    if not placements:
        return [START_X - ROUTE_CLEARANCE]
    xs = sorted({int(round(geo[0])) for geo in placements.values()})
    gutters = [float(xs[0] - ROUTE_CLEARANCE)]
    for i, x in enumerate(xs):
        gutters.append(float(x + CELL_WIDTH + COL_GAP / 2.0))
    gutters.append(float(xs[-1] + CELL_WIDTH + ROUTE_CLEARANCE))
    # unique sorted
    out: List[float] = []
    for g in sorted(gutters):
        if not out or abs(out[-1] - g) > 1:
            out.append(g)
    return out


def _row_highways(placements: Dict[str, Tuple[float, float, float, float]]) -> List[float]:
    """Horizontal channel y positions through gaps between stacked class rows."""
    if not placements:
        return [START_Y - ROUTE_CLEARANCE]
    bands = sorted(
        {(int(round(geo[1])), int(round(geo[1] + geo[3]))) for geo in placements.values()}
    )
    highways = [float(bands[0][0] - ROUTE_CLEARANCE)]
    for i in range(len(bands) - 1):
        _top0, bottom = bands[i]
        top1, _bottom1 = bands[i + 1]
        if top1 > bottom:
            highways.append(float((bottom + top1) / 2.0))
    highways.append(float(bands[-1][1] + ROUTE_CLEARANCE))
    out: List[float] = []
    for y in sorted(highways):
        if not out or abs(out[-1] - y) > 1:
            out.append(y)
    return out


def _nearest(values: List[float], target: float) -> float:
    return min(values, key=lambda v: abs(v - target))


def _ownership_kinds(kind: str) -> bool:
    return (kind or "").lower() in {"composition", "aggregation"}


def _infer_clusters(
    ids: List[str],
    relationships: List[Tuple[str, str, str]],
    modules: Optional[List[Module]] = None,
) -> List[List[str]]:
    """Group classes by module/BC when available; else by composition aggregates.

    Nested owners (a composed class that itself composes others) become their
    own cluster so related lines stay local and foreign lines stay in the gaps.
    """
    id_set = set(ids)
    named_modules = [
        m
        for m in (modules or [])
        if m.name and m.name.strip() and m.classes
    ]
    if len(named_modules) >= 2:
        clusters: List[List[str]] = []
        seen: set[str] = set()
        for module in named_modules:
            members = [
                _slug(c.name)
                for c in module.classes
                if _slug(c.name) in id_set
            ]
            members = [m for m in members if m not in seen]
            if members:
                clusters.append(members)
                seen.update(members)
        leftovers = sorted(cid for cid in ids if cid not in seen)
        if leftovers:
            clusters.append(leftovers)
        return clusters

    from collections import defaultdict

    children: Dict[str, List[str]] = defaultdict(list)
    parents: Dict[str, str] = {}
    for src, tgt, kind in relationships:
        if src == tgt or not _ownership_kinds(kind):
            continue
        children[src].append(tgt)
        parents.setdefault(tgt, src)

    assigned: set[str] = set()
    clusters = []

    # Nested aggregates first (owner that is itself owned, and owns others).
    nested_roots = sorted(
        cid
        for cid in ids
        if children.get(cid) and cid in parents
    )
    for root in nested_roots:
        if root in assigned:
            continue
        members = [root]
        assigned.add(root)
        for child in sorted(children.get(root, ())):
            if child in assigned:
                continue
            # Keep further nested owners out — they get their own cluster.
            if children.get(child) and child in parents and child != root:
                continue
            members.append(child)
            assigned.add(child)
        clusters.append(members)

    # Top-level owners (not themselves composition targets).
    top_roots = sorted(
        cid
        for cid in ids
        if children.get(cid) and cid not in parents
    )
    for root in top_roots:
        if root in assigned:
            continue
        members = [root]
        assigned.add(root)
        for child in sorted(children.get(root, ())):
            if child in assigned:
                continue
            if child in nested_roots:
                continue
            members.append(child)
            assigned.add(child)
        clusters.append(members)

    # Orphans / association-only concepts — attach to the cluster they
    # associate with when that target is unique, so related lines stay local.
    leftovers = sorted(cid for cid in ids if cid not in assigned)
    cluster_of_tmp = {
        cid: index for index, members in enumerate(clusters) for cid in members
    }
    still_orphan: List[str] = []
    for cid in leftovers:
        assoc_targets = [
            tgt
            for src, tgt, kind in relationships
            if src == cid and not _ownership_kinds(kind) and tgt in cluster_of_tmp
        ] + [
            src
            for src, tgt, kind in relationships
            if tgt == cid and not _ownership_kinds(kind) and src in cluster_of_tmp
        ]
        target_clusters = {cluster_of_tmp[t] for t in assoc_targets}
        if len(target_clusters) == 1:
            clusters[next(iter(target_clusters))].append(cid)
            assigned.add(cid)
        else:
            still_orphan.append(cid)
    for cid in still_orphan:
        clusters.append([cid])

    return clusters


def _pack_cluster(
    members: List[str],
    id_to_oclass: Dict[str, OoadClass],
    origin_x: float,
    origin_y: float,
    relationships: List[Tuple[str, str, str]],
    cols: int = INNER_COLS,
) -> Tuple[Dict[str, Tuple[float, float, float, float]], float, float]:
    """Pack one package/aggregate tightly: owners above their invariants.

    Composition children sit immediately under their owner (short diamonds).
    Aggregation parts (non-repository) sit under their owner similarly.
    Remaining association peers fill the next rows. Inter-module distance is
    handled by the caller via CLUSTER_GAP_*.
    """
    if not members:
        return {}, 0.0, 0.0
    member_set = set(members)
    col_count = max(1, cols)

    from collections import defaultdict

    composition: Dict[str, List[str]] = defaultdict(list)
    aggregation: Dict[str, List[str]] = defaultdict(list)
    for src, tgt, kind in relationships:
        if src not in member_set or tgt not in member_set or src == tgt:
            continue
        k = (kind or "").lower()
        if k == "composition":
            composition[src].append(tgt)
        elif k == "aggregation" and "repository" not in src:
            # Repo◇→Aggregate is navigational; keep aggregate as visual root.
            aggregation[src].append(tgt)

    owned = {c for kids in composition.values() for c in kids}
    owned |= {c for kids in aggregation.values() for c in kids}

    def _is_repo(cid: str) -> bool:
        return "repository" in cid

    roots = [
        m
        for m in members
        if m not in owned and (composition.get(m) or aggregation.get(m))
    ]
    if not roots:
        roots = [
            m
            for m in members
            if m not in owned and not _is_repo(m)
        ] or list(members)

    def _root_score(cid: str) -> Tuple[int, int, str]:
        return (
            -(len(composition.get(cid, ())) + len(aggregation.get(cid, ()))),
            0 if "aggregate" in cid or "entity" in cid else 1,
            cid,
        )

    roots = sorted(set(roots), key=_root_score)
    placed: set[str] = set()
    placements: Dict[str, Tuple[float, float, float, float]] = {}
    cursor_y = origin_y
    max_x = origin_x

    def _place_row(cids: List[str], y: float) -> float:
        nonlocal max_x
        if not cids:
            return y
        row_cols = min(col_count, max(1, len(cids)))
        row_h = 0.0
        x = origin_x
        col = 0
        row_y = y
        for cid in cids:
            if cid in placed:
                continue
            h = float(_class_height(id_to_oclass[cid]))
            if col >= row_cols:
                x = origin_x
                row_y += row_h + INNER_ROW_GAP
                row_h = 0.0
                col = 0
            placements[cid] = (x, row_y, float(CELL_WIDTH), h)
            placed.add(cid)
            max_x = max(max_x, x + CELL_WIDTH)
            row_h = max(row_h, h)
            x += CELL_WIDTH + INNER_COL_GAP
            col += 1
        return row_y + row_h

    def _place_owner_tree(owner: str, y: float) -> float:
        nonlocal max_x
        if owner in placed:
            return y
        oh = float(_class_height(id_to_oclass[owner]))
        placements[owner] = (origin_x, y, float(CELL_WIDTH), oh)
        placed.add(owner)
        max_x = max(max_x, origin_x + CELL_WIDTH)
        kids: List[str] = []
        for kid in list(composition.get(owner, ())) + list(aggregation.get(owner, ())):
            if kid not in placed and kid in member_set:
                kids.append(kid)
        seen_k: set[str] = set()
        uniq_kids: List[str] = []
        for k in kids:
            if k not in seen_k:
                seen_k.add(k)
                uniq_kids.append(k)
        if not uniq_kids:
            # Still park repositories beside a leaf-less owner.
            repo_x = origin_x + CELL_WIDTH + INNER_COL_GAP
            bottom = y + oh
            for src, tgt, kind in relationships:
                if tgt != owner or src in placed or src not in member_set:
                    continue
                if (kind or "").lower() != "aggregation" or "repository" not in src:
                    continue
                rh = float(_class_height(id_to_oclass[src]))
                placements[src] = (repo_x, y, float(CELL_WIDTH), rh)
                placed.add(src)
                max_x = max(max_x, repo_x + CELL_WIDTH)
                bottom = max(bottom, y + rh)
                repo_x += CELL_WIDTH + INNER_COL_GAP
            return bottom
        # Repositories that aggregate this owner sit immediately to the right
        # before composition leaves, so◇ edges stay short.
        repo_x = origin_x + CELL_WIDTH + INNER_COL_GAP
        bottom = y + oh
        for src, tgt, kind in relationships:
            if tgt != owner or src in placed or src not in member_set:
                continue
            if (kind or "").lower() != "aggregation" or "repository" not in src:
                continue
            rh = float(_class_height(id_to_oclass[src]))
            placements[src] = (repo_x, y, float(CELL_WIDTH), rh)
            placed.add(src)
            max_x = max(max_x, repo_x + CELL_WIDTH)
            bottom = max(bottom, y + rh)
            repo_x += CELL_WIDTH + INNER_COL_GAP
        nested = [k for k in uniq_kids if composition.get(k) or aggregation.get(k)]
        leaves = [k for k in uniq_kids if k not in nested]
        # Beside placement: one nested child and leaves share the owner's row,
        # wrapping under when the row is full so far-right gaps stay small.
        side_kids = list(leaves)
        deep_nested = list(nested)
        if nested and not leaves:
            side_kids = [nested[0]]
            deep_nested = nested[1:]
        if side_kids:
            x = repo_x
            row_y = y
            row_h = oh
            col = int(round((x - origin_x) / (CELL_WIDTH + INNER_COL_GAP)))
            # Owner + one side slot, then wrap — avoids long same-row gaps
            # through intervening siblings (Customer→Address past Identity).
            leaf_cols = min(2, col_count)
            for kid in side_kids:
                if kid in placed:
                    continue
                if kid in nested:
                    nest_bottom = _place_owner_tree_at(kid, x, row_y)
                    bottom = max(bottom, nest_bottom)
                    max_x = max(max_x, x + CELL_WIDTH)
                    x += CELL_WIDTH + INNER_COL_GAP
                    col += 1
                    if col >= leaf_cols:
                        x = origin_x
                        row_y = bottom + INNER_ROW_GAP
                        row_h = 0.0
                        col = 0
                    continue
                kh = float(_class_height(id_to_oclass[kid]))
                if col >= leaf_cols:
                    x = origin_x
                    row_y = bottom + INNER_ROW_GAP
                    row_h = 0.0
                    col = 0
                placements[kid] = (x, row_y, float(CELL_WIDTH), kh)
                placed.add(kid)
                max_x = max(max_x, x + CELL_WIDTH)
                row_h = max(row_h, kh)
                bottom = max(bottom, row_y + row_h)
                x += CELL_WIDTH + INNER_COL_GAP
                col += 1
        nest_y = bottom + INNER_ROW_GAP
        for nest in deep_nested:
            if nest in placed:
                continue
            nest_y = _place_owner_tree(nest, nest_y) + INNER_ROW_GAP
        return max(bottom, nest_y - INNER_ROW_GAP)

    def _place_owner_tree_at(owner: str, x: float, y: float) -> float:
        """Place an owner tree rooted at (x, y); returns bottom y."""
        nonlocal max_x
        if owner in placed:
            return y
        oh = float(_class_height(id_to_oclass[owner]))
        placements[owner] = (x, y, float(CELL_WIDTH), oh)
        placed.add(owner)
        max_x = max(max_x, x + CELL_WIDTH)
        kids: List[str] = []
        for kid in list(composition.get(owner, ())) + list(aggregation.get(owner, ())):
            if kid not in placed and kid in member_set:
                kids.append(kid)
        if not kids:
            return y + oh
        nested = [k for k in kids if composition.get(k) or aggregation.get(k)]
        leaves = [k for k in kids if k not in nested]
        bottom = y + oh
        cx = x + CELL_WIDTH + INNER_COL_GAP
        for kid in leaves:
            kh = float(_class_height(id_to_oclass[kid]))
            placements[kid] = (cx, y, float(CELL_WIDTH), kh)
            placed.add(kid)
            max_x = max(max_x, cx + CELL_WIDTH)
            bottom = max(bottom, y + kh)
            cx += CELL_WIDTH + INNER_COL_GAP
        ny = bottom + INNER_ROW_GAP
        for nest in nested:
            ny = _place_owner_tree_at(nest, x, ny) + INNER_ROW_GAP
        return max(bottom, ny - INNER_ROW_GAP)
    for root in roots:
        if root in placed:
            continue
        cursor_y = _place_owner_tree(root, cursor_y) + INNER_ROW_GAP

    # Repositories sit beside their aggregate root (short white-diamond edge).
    for src, tgt, kind in relationships:
        if (kind or "").lower() != "aggregation":
            continue
        if "repository" not in src:
            continue
        if src not in member_set or src in placed or tgt not in placements:
            continue
        tx, ty, _tw, _th = placements[tgt]
        rh = float(_class_height(id_to_oclass[src]))
        rx = tx + CELL_WIDTH + INNER_COL_GAP
        candidate = (rx, ty, float(CELL_WIDTH), rh)
        guard = 0
        while any(
            _rects_overlap(candidate, geo, gap=OVERLAP_GAP)
            for oid, geo in placements.items()
        ) and guard < 8:
            guard += 1
            rx += CELL_WIDTH + INNER_COL_GAP
            candidate = (rx, ty, float(CELL_WIDTH), rh)
        placements[src] = candidate
        placed.add(src)
        max_x = max(max_x, candidate[0] + CELL_WIDTH)

    leftovers = [m for m in members if m not in placed]
    while leftovers:
        best_i = 0
        best_score = -1
        for i, cid in enumerate(leftovers):
            links = 0
            for src, tgt, kind in relationships:
                # Count associations; also repo◇→root so repos co-locate.
                if _ownership_kinds(kind) and "repository" not in src:
                    continue
                if (src == cid and tgt in placed) or (tgt == cid and src in placed):
                    links += 1
            if links > best_score:
                best_score = links
                best_i = i
        batch = [leftovers.pop(best_i)]
        # Prefer peers linked to the same neighborhood, then fill the row.
        for cid in list(leftovers):
            if len(batch) >= col_count:
                break
            linked = any(
                (src == cid and tgt in placed)
                or (tgt == cid and src in placed)
                or (src == cid and tgt in batch)
                or (tgt == cid and src in batch)
                for src, tgt, kind in relationships
                if not _ownership_kinds(kind) or "repository" in src
            )
            if linked:
                leftovers.remove(cid)
                batch.append(cid)
        while leftovers and len(batch) < col_count:
            batch.append(leftovers.pop(0))
        cursor_y = _place_row(batch, cursor_y) + INNER_ROW_GAP

    still = [m for m in members if m not in placed]
    if still:
        cursor_y = _place_row(still, cursor_y) + INNER_ROW_GAP

    width = max_x - origin_x
    height = max(0.0, cursor_y - origin_y - INNER_ROW_GAP)
    return placements, width, height


def _layout_classes_clustered(
    id_to_oclass: Dict[str, OoadClass],
    relationships: List[Tuple[str, str, str]],
    modules: Optional[List[Module]] = None,
    previous_positions: Optional[Dict[str, Tuple[float, float]]] = None,
) -> Dict[str, Tuple[float, float, float, float]]:
    """Place same-module / same-aggregate classes in tight islands.

    Distinct modules (or composition aggregates when modules are flat) sit
    farther apart so intra-context edges stay short and inter-context edges
    run in the gaps instead of tangling through unrelated boxes.
    """
    ids = list(id_to_oclass.keys())
    if previous_positions:
        trial: Dict[str, Tuple[float, float, float, float]] = {}
        complete = True
        for cid in ids:
            if cid not in previous_positions:
                complete = False
                break
            x, y = previous_positions[cid]
            h = float(_class_height(id_to_oclass[cid]))
            trial[cid] = (x, y, float(CELL_WIDTH), h)
        if complete:
            overlaps = False
            cid_list = list(trial.keys())
            for i, a in enumerate(cid_list):
                for b in cid_list[i + 1 :]:
                    if _rects_overlap(trial[a], trial[b], gap=OVERLAP_GAP):
                        overlaps = True
                        break
                if overlaps:
                    break
            if not overlaps:
                return trial

    # Detect whether clustering was module-driven (H1 sections) or inferred from
    # composition.  Module-driven clusters are peers (bounded contexts sit at the
    # same level); deriving a parent/child hierarchy between them from cross-module
    # composition edges creates unplaceable grandchild clusters.
    named_module_count = sum(
        1 for m in (modules or []) if m.name and m.name.strip() and m.classes
    )
    module_driven = named_module_count >= 2

    clusters = _infer_clusters(ids, relationships, modules=modules)
    cluster_of = {
        cid: index for index, members in enumerate(clusters) for cid in members
    }

    # Module-driven layouts follow H1 / sequential order (lifecycle bands),
    # not size — Customer → Prospect → Subscriber → Billing stay readable top-down.
    if module_driven:
        placements: Dict[str, Tuple[float, float, float, float]] = {}
        cursor_y = float(START_Y)
        for index in range(len(clusters)):
            _local, _width, height = _pack_cluster(
                clusters[index],
                id_to_oclass,
                float(START_X),
                cursor_y,
                relationships,
            )
            placements.update(_local)
            cursor_y += height + CLUSTER_GAP_Y
        return placements

    # Which clusters are owned (via composition) by another cluster?
    # Skip this hierarchy-building when clusters come from named modules — all
    # module clusters are treated as peer roots so none go unplaced.
    child_clusters: Dict[int, List[int]] = {i: [] for i in range(len(clusters))}
    parent_of_cluster: Dict[int, int] = {}
    if not module_driven:
        for src, tgt, kind in relationships:
            if not _ownership_kinds(kind):
                continue
            if src not in cluster_of or tgt not in cluster_of:
                continue
            ps, pt = cluster_of[src], cluster_of[tgt]
            if ps == pt:
                continue
            if pt not in child_clusters[ps]:
                child_clusters[ps].append(pt)
            parent_of_cluster.setdefault(pt, ps)

    roots = [i for i in range(len(clusters)) if i not in parent_of_cluster]
    # Largest root first (usually the primary aggregate / BC).
    roots.sort(key=lambda i: (-len(clusters[i]), i))
    orphans = [
        i
        for i in range(len(clusters))
        if i not in parent_of_cluster and not child_clusters[i] and i not in roots[:1]
    ]
    # roots already includes orphans; separate true parent roots from leaf orphans
    parent_roots = [i for i in roots if child_clusters[i] or len(clusters[i]) > 1]
    leaf_orphans = [i for i in roots if i not in parent_roots]

    placements: Dict[str, Tuple[float, float, float, float]] = {}
    cursor_y = float(START_Y)

    def _place_at(index: int, origin_x: float, origin_y: float) -> Tuple[float, float]:
        local, width, height = _pack_cluster(
            clusters[index], id_to_oclass, origin_x, origin_y, relationships
        )
        placements.update(local)
        return width, height

    for root_i in parent_roots:
        # Parent island centered above its owned aggregates.
        children = sorted(child_clusters[root_i])
        child_packs = []
        approx_children_width = 0.0
        for child_i in children:
            # Measure without committing — pack at 0,0 for size only.
            _local, cw, ch = _pack_cluster(
                clusters[child_i], id_to_oclass, 0.0, 0.0, relationships
            )
            child_packs.append((child_i, cw, ch))
            approx_children_width += cw
        if children:
            approx_children_width += CLUSTER_GAP_X * (len(children) - 1)

        root_w_est = min(INNER_COLS, len(clusters[root_i])) * CELL_WIDTH
        band_width = max(root_w_est, approx_children_width)
        root_x = float(START_X + max(0.0, (band_width - root_w_est) / 2.0))
        root_w, root_h = _place_at(root_i, root_x, cursor_y)

        child_y = cursor_y + root_h + CLUSTER_GAP_Y
        child_x = float(START_X + max(0.0, (band_width - approx_children_width) / 2.0))
        child_row_h = 0.0
        for child_i, cw, ch in child_packs:
            _cw, ch2 = _place_at(child_i, child_x, child_y)
            child_x += cw + CLUSTER_GAP_X
            child_row_h = max(child_row_h, ch2)
        cursor_y = child_y + child_row_h + CLUSTER_GAP_Y

    # Association-only / leftover concepts: farther band below everything.
    if leaf_orphans:
        orphan_x = float(START_X)
        orphan_y = cursor_y + CLUSTER_GAP_Y * 0.5
        row_h = 0.0
        for orphan_i in leaf_orphans:
            ow, oh = _place_at(orphan_i, orphan_x, orphan_y)
            orphan_x += ow + CLUSTER_GAP_X
            row_h = max(row_h, oh)
            # wrap orphan row
            if orphan_x > START_X + 3 * (CELL_WIDTH + CLUSTER_GAP_X):
                orphan_x = float(START_X)
                orphan_y += row_h + CLUSTER_GAP_Y
                row_h = 0.0

    return placements


def _segments_from_route(
    src: Tuple[float, float, float, float],
    tgt: Tuple[float, float, float, float],
    exit_side: str,
    entry_side: str,
    exit_frac: float,
    entry_frac: float,
    waypoints: List[Tuple[float, float]],
) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
    p1 = _point_on_side(src, exit_side, exit_frac)
    p2 = _point_on_side(tgt, entry_side, entry_frac)
    points = _dedupe_points([p1, *waypoints, p2])
    return [(points[i], points[i + 1]) for i in range(len(points) - 1)]


def _segment_pair_conflicts(
    segs_a: List[Tuple[Tuple[float, float], Tuple[float, float]]],
    segs_b: List[Tuple[Tuple[float, float], Tuple[float, float]]],
) -> bool:
    from context_tools.clean_engineering.class_model.drawio.drawio_tools import (
        _edge_segments_overlap,
    )

    for sa in segs_a:
        for sb in segs_b:
            if _edge_segments_overlap(sa, sb, proximity=10):
                return True
            crossed, _pt = _orthogonal_segments_cross(sa, sb)
            if crossed:
                return True
    return False


def _orthogonal_segments_cross(
    seg_a: Tuple[Tuple[float, float], Tuple[float, float]],
    seg_b: Tuple[Tuple[float, float], Tuple[float, float]],
    endpoint_tol: float = 2.0,
) -> Tuple[bool, Optional[Tuple[float, float]]]:
    (ax1, ay1), (ax2, ay2) = seg_a
    (bx1, by1), (bx2, by2) = seg_b
    a_horiz = abs(ay2 - ay1) < 2
    a_vert = abs(ax2 - ax1) < 2
    b_horiz = abs(by2 - by1) < 2
    b_vert = abs(bx2 - bx1) < 2
    if a_horiz and b_vert:
        y = (ay1 + ay2) / 2
        x = (bx1 + bx2) / 2
        a_lo_x, a_hi_x = sorted((ax1, ax2))
        b_lo_y, b_hi_y = sorted((by1, by2))
        if (
            a_lo_x + endpoint_tol < x < a_hi_x - endpoint_tol
            and b_lo_y + endpoint_tol < y < b_hi_y - endpoint_tol
        ):
            return True, (x, y)
    if a_vert and b_horiz:
        x = (ax1 + ax2) / 2
        y = (by1 + by2) / 2
        a_lo_y, a_hi_y = sorted((ay1, ay2))
        b_lo_x, b_hi_x = sorted((bx1, bx2))
        if (
            a_lo_y + endpoint_tol < y < a_hi_y - endpoint_tol
            and b_lo_x + endpoint_tol < x < b_hi_x - endpoint_tol
        ):
            return True, (x, y)
    return False, None


def _capped_outward_point(
    geo: Tuple[float, float, float, float],
    side: str,
    frac: float,
    clearance: float,
    highways: List[float],
) -> Tuple[float, float]:
    """Outward point that stays inside the nearest open highway band."""
    ax, ay = _point_on_side(geo, side, frac)
    x, y, w, h = geo
    if side == "bottom":
        band = min((hy for hy in highways if hy >= y + h), default=y + h + clearance)
        return ax, min(ay + clearance, band)
    if side == "top":
        band = max((hy for hy in highways if hy <= y), default=y - clearance)
        return ax, max(ay - clearance, band)
    if side == "left":
        return ax - clearance, ay
    return ax + clearance, ay


def _route_waypoints(
    src: Tuple[float, float, float, float],
    tgt: Tuple[float, float, float, float],
    exit_side: str,
    entry_side: str,
    exit_frac: float,
    entry_frac: float,
    obstacles: List[Tuple[float, float, float, float]],
    lane: float = 0.0,
    avoid_segments: Optional[
        List[List[Tuple[Tuple[float, float], Tuple[float, float]]]]
    ] = None,
    all_placements: Optional[Dict[str, Tuple[float, float, float, float]]] = None,
) -> List[Tuple[float, float]]:
    """Orthogonal channel router: prefer no/few waypoints; highway only if needed."""
    avoid_segments = avoid_segments or []
    placements = all_placements or {
        str(i): geo for i, geo in enumerate([src, tgt, *obstacles])
    }
    gutters = _column_gutters(placements)
    lane_i = int(round(lane / ROUTE_LANE_STEP)) if ROUTE_LANE_STEP else 0
    max_clear = max(12.0, min(ROUTE_CLEARANCE, ROW_GAP * 0.35))
    highways = _row_highways(placements)
    leave = _capped_outward_point(src, exit_side, exit_frac, max_clear, highways)
    approach = _capped_outward_point(tgt, entry_side, entry_frac, max_clear, highways)
    # Parallel separation: scanners use ~12px proximity; 12px lanes fit three
    # highways in a typical INNER_ROW_GAP (~44px). Do not modulo-wrap into ROW_GAP.
    lane_sep = 12.0

    exit_pt = _point_on_side(src, exit_side, exit_frac)
    entry_pt = _point_on_side(tgt, entry_side, entry_frac)

    def _is_clear(pts: List[Tuple[float, float]], check_edges: bool) -> bool:
        if _polyline_hits_obstacle(pts, obstacles, margin=3.0):
            return False
        segs = _segments_from_route(
            src, tgt, exit_side, entry_side, exit_frac, entry_frac, pts
        )
        points = [segs[0][0], *[p for seg in segs for p in seg[1:]]]
        if _polyline_hits_obstacle(points, obstacles, margin=3.0):
            return False
        if check_edges and any(
            _segment_pair_conflicts(segs, prior) for prior in avoid_segments
        ):
            return False
        return True

    # Prefer empty waypoints (one orthogonal bend via edge style) when clear.
    if _is_clear([], check_edges=True):
        return []
    # Single mid-point L when sides are opposite and span is short.
    if {exit_side, entry_side} <= {"top", "bottom"}:
        mid = [(exit_pt[0], (leave[1] + approach[1]) / 2.0)]
        if _is_clear(mid, check_edges=True):
            return mid
    if {exit_side, entry_side} <= {"left", "right"}:
        mid = [((leave[0] + approach[0]) / 2.0, exit_pt[1])]
        if _is_clear(mid, check_edges=True):
            return mid
    # Two-point elbow via leave/approach — still short when neighbors are close.
    elbow = [leave, approach]
    if _is_clear(elbow, check_edges=True):
        return elbow

    # Close endpoints: accept a short route even if it grazes another edge —
    # prefer-short-routes beats parallel-lane highways for nearby boxes.
    scx, scy = src[0] + src[2] / 2.0, src[1] + src[3] / 2.0
    tcx, tcy = tgt[0] + tgt[2] / 2.0, tgt[1] + tgt[3] / 2.0
    if abs(scx - tcx) + abs(scy - tcy) < 420:
        if _is_clear([], check_edges=False):
            return []
        if {exit_side, entry_side} <= {"top", "bottom"}:
            mid = [(exit_pt[0], (leave[1] + approach[1]) / 2.0)]
            if _is_clear(mid, check_edges=False):
                return mid
        if {exit_side, entry_side} <= {"left", "right"}:
            mid = [((leave[0] + approach[0]) / 2.0, exit_pt[1])]
            if _is_clear(mid, check_edges=False):
                return mid
        if _is_clear(elbow, check_edges=False):
            return elbow

    def _occupied_horiz_ys() -> List[float]:
        ys: List[float] = []
        for segs in avoid_segments:
            for (a, b) in segs:
                if abs(a[1] - b[1]) < 2.0 and abs(a[0] - b[0]) > 12.0:
                    ys.append((a[1] + b[1]) / 2.0)
        return ys

    def _sorted_free_ys(cands: List[float]) -> List[float]:
        occupied = _occupied_horiz_ys()

        def _score(y: float) -> Tuple[float, float]:
            if not occupied:
                return (0.0, abs(y - cands[0]))
            dist = min(abs(y - o) for o in occupied)
            penalty = 0.0 if dist >= lane_sep else (lane_sep - dist)
            return (penalty, -dist)

        uniq: List[float] = []
        for y in cands:
            if all(abs(y - e) >= 1.0 for e in uniq):
                uniq.append(y)
        return sorted(uniq, key=_score)

    def _fan_y(base: float, outward: float, count: int = 8) -> List[float]:
        order = [lane_i] + [i for i in range(count) if i != lane_i]
        vals: List[float] = []
        for step in order:
            y = base + outward * float(step) * lane_sep
            if outward > 0 and y < base - 0.5:
                continue
            if outward < 0 and y > base + 0.5:
                continue
            if all(abs(y - e) >= lane_sep - 0.5 for e in vals):
                vals.append(y)
        return vals or [base]

    def _channels(extra: float = 0.0) -> List[float]:
        xs = [gx + (lane_i - 2) * 8 for gx in gutters]
        near_left = src[0] - 16.0 - extra
        near_right = src[0] + src[2] + 16.0 + extra
        far_left = [
            gutters[0] - 40 - lane_i * 10 - extra,
            gutters[0] - 80 - lane_i * 14 - extra,
            gutters[0] - 140 - lane_i * 18 - extra,
        ]
        far_right = [
            gutters[-1] + 40 + lane_i * 10 + extra,
            gutters[-1] + 80 + lane_i * 14 + extra,
            gutters[-1] + 140 + lane_i * 18 + extra,
        ]
        # If other classes sit in the vertical span between src and tgt, keep the
        # long vertical outside their shared bounding box so sibling routes that
        # later cross that band are not blocked by a mid-band channel.
        span_top = min(src[1], tgt[1])
        span_bot = max(src[1] + src[3], tgt[1] + tgt[3])
        intervening = [
            geo
            for geo in placements.values()
            if geo != src
            and geo != tgt
            and geo[1] < span_bot
            and geo[1] + geo[3] > span_top
        ]
        if intervening:
            band_lo = min(g[0] for g in intervening) - 20.0 - extra
            band_hi = max(g[0] + g[2] for g in intervening) + 20.0 + extra
            # Prefer the outside nearest the exit so the stub does not sweep across
            # other bottom-exit anchors on the same parent.
            if exit_pt[0] >= src[0] + src[2] * 0.5:
                outside = [band_hi, band_hi + 40.0, band_lo, band_lo - 40.0]
            else:
                outside = [band_lo, band_lo - 40.0, band_hi, band_hi + 40.0]
            return outside + far_right + far_left + [near_right, near_left] + xs
        if entry_pt[0] >= exit_pt[0]:
            return far_right + [near_right] + xs + [near_left] + far_left
        return far_left + [near_left] + xs + [near_right] + far_right

    def _candidates(extra: float = 0.0) -> List[List[Tuple[float, float]]]:
        paths: List[List[Tuple[float, float]]] = []
        channels = _channels(extra)

        if exit_side in ('left', 'right') or entry_side in ('left', 'right'):
            y_vals = _sorted_free_ys(
                _fan_y(leave[1], 1.0, count=6)
                + [leave[1] - (i + 1) * lane_sep for i in range(5)]
            )
            for y in y_vals[:8]:
                for cx in channels[:8]:
                    paths.append(
                        [leave, (leave[0], y), (cx, y), (approach[0], y), approach]
                    )
                    paths.append(
                        [
                            leave,
                            (cx, leave[1]),
                            (cx, y),
                            (approach[0], y),
                            approach,
                        ]
                    )
            paths.append([leave, (approach[0], leave[1]), approach])
            paths.append([leave, approach])
            return paths

        out_exit = 1.0 if exit_side == 'bottom' else -1.0
        out_entry = -1.0 if entry_side == 'top' else 1.0
        # Minimal stub so long verticals sit in gutters, not on exit X.
        stub_y = exit_pt[1] + out_exit * 10.0
        src_ys = _sorted_free_ys(_fan_y(stub_y, out_exit, count=6))
        tgt_ys = _sorted_free_ys(
            _fan_y(entry_pt[1] + out_entry * 10.0, out_entry, count=6)
        )
        tgt_ys = [
            y
            for y in tgt_ys
            if (entry_side != 'top' or y <= entry_pt[1])
            and (entry_side != 'bottom' or y >= entry_pt[1])
        ] or [entry_pt[1] + out_entry * 10.0]
        # Keep approach highways inside the src→tgt gap so entry verticals stay short
        # and do not get crossed by wrap-around routes in the same band.
        if exit_side == 'bottom' and entry_side == 'top':
            gap_lo = exit_pt[1] + 10.0
            gap_hi = entry_pt[1] - 10.0
            in_gap = [y for y in tgt_ys if gap_lo - 0.5 <= y <= gap_hi + 0.5]
            if in_gap:
                tgt_ys = in_gap
            src_in_gap = [y for y in src_ys if gap_lo - 0.5 <= y <= gap_hi + 0.5]
            if src_in_gap:
                src_ys = src_in_gap
        src_ys = [
            y
            for y in src_ys
            if (exit_side != 'bottom' or y >= exit_pt[1])
            and (exit_side != 'top' or y <= exit_pt[1])
        ] or [stub_y]

        channel_paths: List[List[Tuple[float, float]]] = []
        gap_paths: List[List[Tuple[float, float]]] = []
        for tgt_hw in tgt_ys:
            for cx in channels[:8]:
                channel_paths.append(
                    [
                        (exit_pt[0], stub_y),
                        (cx, stub_y),
                        (cx, tgt_hw),
                        (entry_pt[0], tgt_hw),
                    ]
                )
            for src_hw in src_ys[:4]:
                for cx in channels[:6]:
                    channel_paths.append(
                        [
                            (exit_pt[0], src_hw),
                            (cx, src_hw),
                            (cx, tgt_hw),
                            (entry_pt[0], tgt_hw),
                        ]
                    )
        for src_hw in src_ys[:6]:
            gap_paths.append([(exit_pt[0], src_hw), (entry_pt[0], src_hw)])
            for tgt_hw in tgt_ys[:4]:
                if abs(tgt_hw - src_hw) >= lane_sep * 0.5:
                    gap_paths.append(
                        [
                            (exit_pt[0], src_hw),
                            (entry_pt[0], src_hw),
                            (entry_pt[0], tgt_hw),
                        ]
                    )

        if avoid_segments:
            return channel_paths + gap_paths
        return gap_paths + channel_paths

    def _search(extra: float, check_edges: bool) -> Optional[List[Tuple[float, float]]]:
        for path in _candidates(extra):
            pts = _dedupe_points(path)
            if pts and _is_clear(pts, check_edges=check_edges):
                return pts
        return None

    found = _search(0.0, check_edges=True)
    if found is not None:
        return found

    if not avoid_segments:
        found = _search(0.0, check_edges=False)
        if found is not None:
            return found
    else:
        for extra in (40.0, 100.0, 180.0, 280.0):
            found = _search(extra, check_edges=True)
            if found is not None:
                return found

    best: Optional[List[Tuple[float, float]]] = None
    best_conflicts = 10**9
    for path in _candidates(280.0):
        pts = _dedupe_points(path)
        if not pts or not _is_clear(pts, check_edges=False):
            continue
        segs = _segments_from_route(
            src, tgt, exit_side, entry_side, exit_frac, entry_frac, pts
        )
        conflicts = sum(
            1 for prior in avoid_segments if _segment_pair_conflicts(segs, prior)
        )
        if conflicts < best_conflicts:
            best = pts
            best_conflicts = conflicts
            if conflicts == 0:
                return pts
    if best is not None:
        return best

    out_exit = 1.0 if exit_side == 'bottom' else -1.0
    out_entry = -1.0 if entry_side == 'top' else 1.0
    ox = _channels(280.0)[0]
    return _dedupe_points(
        [
            (exit_pt[0], exit_pt[1] + out_exit * 10.0),
            (ox, exit_pt[1] + out_exit * 10.0),
            (ox, entry_pt[1] + out_entry * 10.0),
            (entry_pt[0], entry_pt[1] + out_entry * 10.0),
        ]
    )



def _parse_class_html(value: str) -> Tuple[Optional[str], List[Property], List[Operation]]:
    text = html.unescape(value)
    # Skip module-style cells (seam bullets + purpose italics, no UML hr size)
    if ("•" in text or "-" in text) and 'hr size="1"' not in text.lower() and "<hr size=" not in text.lower():
        if re.search(r"<i[^>]*>", text, re.IGNORECASE):
            return None, [], []

    m = re.search(r"<b[^>]*>([^<]+)</b>", text)
    name = m.group(1).strip() if m else None
    if not name:
        return None, [], []

    sections = re.split(r'<hr\s+size="1"\s*/?>', text, flags=re.IGNORECASE)
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
