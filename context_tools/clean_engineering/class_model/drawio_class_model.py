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
  - Classes laid out left-to-right, 5 per row.

Parse reads either shape back into the canonical model.
"""
from __future__ import annotations

import html
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_repo = Path(__file__).resolve().parents[3]
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
    def render(cls, canonical: CleanEngineeringModel, previous: Optional[str] = None) -> str:
        if _is_modules_view(canonical):
            return cls._render_modules(canonical, previous=previous)
        return cls._render_classes(canonical, previous=previous)

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

        name_to_id: dict[str, str] = {}
        prev_pos = _read_positions(previous) if previous else {}

        for idx, oclass in enumerate(canonical.classes):
            col = idx % COLS_PER_ROW
            row = idx // COLS_PER_ROW
            cell_id = _slug(oclass.name)
            name_to_id[oclass.name] = cell_id
            if cell_id in prev_pos:
                x, y = prev_pos[cell_id]
            else:
                x = START_X + col * (CELL_WIDTH + COL_GAP)
                y = START_Y + row * (_class_height(oclass) + ROW_GAP)
            _create_class_cell(root_el, oclass, cell_id=cell_id, x=x, y=y)

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
# View detection
# ---------------------------------------------------------------------------

def _is_modules_view(canonical: CleanEngineeringModel) -> bool:
    """True when the model is module-boundary detail only (no typed class members)."""
    if not canonical.modules:
        return False
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
