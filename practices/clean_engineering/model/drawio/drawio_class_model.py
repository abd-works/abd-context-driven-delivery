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
from practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass, Operation, Property, Relationship
from practices.clean_engineering.model.diagram.diagram_node import (
    ContainmentForest,
    DiagramClass,
    is_modules_view,
    module_tab_label,
    path_parent,
)
from practices.clean_engineering.model.diagram.geometry import CELL_WIDTH, Geometry, MODULE_CELL_MIN_HEIGHT, MODULE_CELL_WIDTH
from practices.clean_engineering.model.drawio.diagram_node import (
    DrawIOClass,
    DrawIOModule,
    ImportedClass,
    MODULE_CHILD_STYLE,
    MODULE_STYLE,
    Page,
)
from practices.clean_engineering.model.update_report import UpdateReport
EDGE_STYLES = {'inheritance': 'edgeStyle=orthogonalEdgeStyle;rounded=1;endArrow=block;endSize=16;endFill=0;html=1;', 'composition': 'edgeStyle=orthogonalEdgeStyle;rounded=1;endArrow=none;html=1;startArrow=diamondThin;startFill=1;startSize=14;', 'aggregation': 'edgeStyle=orthogonalEdgeStyle;rounded=1;endArrow=none;html=1;startArrow=diamondThin;startFill=0;startSize=14;', 'association': 'edgeStyle=orthogonalEdgeStyle;rounded=1;endArrow=open;endSize=12;html=1;'}
DEFAULT_EDGE_STYLE = EDGE_STYLES['association']
CLUSTER_GAP_X = 360
CLUSTER_GAP_Y = 420
INNER_COLS = 2
INNER_COL_GAP = 20
INNER_ROW_GAP = 28
COLS_PER_ROW = INNER_COLS
COL_GAP = INNER_COL_GAP
ROW_GAP = INNER_ROW_GAP
START_X = 40
START_Y = 40
ROUTE_CLEARANCE = 24
ROUTE_LANE_STEP = 10
OVERLAP_GAP = 24
MODULE_COL_GAP = 48
MODULE_ROW_GAP = 32
MODULE_START_X = 40
MODULE_START_Y = 100
MODULE_CHILD_PAD_X = 16
MODULE_CHILD_PAD_Y = 12
MODULE_CHILD_GAP = 12
MODULE_CHILD_COLS = 2
MODULE_DEP_EDGE_STYLE = 'edgeStyle=orthogonalEdgeStyle;rounded=1;endArrow=classic;html=1;strokeWidth=2;fontSize=10;'
MODULE_TITLE_STYLE = 'text;html=1;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;'
MODULE_SUBTITLE_STYLE = 'text;html=1;align=center;verticalAlign=middle;fontSize=11;fontStyle=2;'
_MODULE_MARKER = 'fillColor=#1a3a6e'
_MODULE_CHILD_MARKER = 'fillColor=#dae8fc'

class DrawIOCleanEngineeringModel(CleanEngineeringModel):

    def __init__(self, name: str='', sequential_order: int=1) -> None:
        super().__init__(name, sequential_order)
        self.previous = None
        self.keep_positioning = False
        self._page_width = '1654'
        self._page_height = '1169'
        self._id_to_oclass: Dict[str, OoadClass] = {}
        self._relationships: List[Tuple[str, str, str]] = []
        self._modules: List[Module] = []
        self._previous_positions: Optional[Dict[str, Tuple[float, float]]] = None
        self._import_ids: List[str] = []
        self._page_ids: set = set()
        self._local_ids = None
        self._id_to_module: dict[str, str] = {}
        self._local_module_name = ''
        self._placements: Dict[str, Tuple[float, float, float, float]] = {}
        self._cell_id = ''
        self._cell_x = 0.0
        self._cell_y = 0.0
        self._cell_width = None
        self._cell_height = None
        self._cell_parent_id = '1'
        self._cell_style = ''
        self._from_module = ''
        self._edge_src_id = ''
        self._edge_tgt_id = ''
        self._edge_kind = ''
        self._edge_id = ''
        self._exit_x = None
        self._exit_y = None
        self._entry_x = None
        self._entry_y = None
        self._waypoints: List[Tuple[float, float]] = []
        self._forest: Optional[ContainmentForest] = None
        self._layout: Optional[_ContainmentLayout] = None
        self._abs_x = 0.0
        self._abs_y = 0.0
        self._prefer_move: set[str] = set()
        self._name_to_id: dict[str, str] = {}
        self._origin_x = 0.0
        self._origin_y = 0.0
        self._pack_cols = INNER_COLS
        self._route_src = None
        self._route_tgt = None
        self._exit_side = ''
        self._entry_side = ''
        self._exit_frac = 0.5
        self._entry_frac = 0.5
        self._obstacles: list = []
        self._route_lane = 0
        self._avoid_segments: list = []
        self._all_placements: dict = {}
        self._anchor_side = ''
        self._anchor_frac = 0.5
        self._clearance = 0.0
        self._highways: List[float] = []
        self._hit_margin = 3.0
        self._endpoint_tol = 2.0
        self._proximity = 10
        self._other_segment = None
        self._ccw_third = (0.0, 0.0)
        self._fan_outward = 1.0
        self._fan_count = 6

    def load_module(self, source: Module) -> DrawIOModule:
        loaded = DrawIOModule(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        loaded.classes = list(source.classes)
        return loaded

    def load_class(self, source: OoadClass) -> DrawIOClass:
        loaded = DrawIOClass(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        return loaded

    def _imported_class(self, source: OoadClass, from_module: str = '') -> ImportedClass:
        loaded = ImportedClass(
            name=source.name,
            sequential_order=source.sequential_order,
            from_module=from_module,
        )
        loaded.update_self(source)
        return loaded

    def parse(self, text: str) -> 'DrawIOCleanEngineeringModel':
        model = DrawIOCleanEngineeringModel(name='', sequential_order=1)
        try:
            root_el = ET.fromstring(text)
        except ET.ParseError:
            return model
        mxcells = list(root_el.iter('mxCell'))
        if self._looks_like_modules_diagram(mxcells):
            return self._parse_modules(mxcells)
        diagrams = list(root_el.findall('diagram'))
        if len(diagrams) > 1:
            return self._parse_classes_multipage(diagrams)
        return self._parse_classes(mxcells)

    def _parse_modules(self, mxcells: List[ET.Element]) -> 'DrawIOCleanEngineeringModel':
        model = DrawIOCleanEngineeringModel(name='', sequential_order=1)
        order = 1
        id_to_module: dict[str, Module] = {}
        for cell in mxcells:
            if cell.get('vertex') != '1':
                continue
            style = cell.get('style', '')
            if 'text;' in style or style.startswith('text;'):
                if cell.get('id') == 'title':
                    title = html.unescape(cell.get('value', ''))
                    m = re.match('^(.+?)\\s*[-\\-]\\s*Modules?', title)
                    if m:
                        model.name = m.group(1).strip()
                continue
            if not self._is_module_style(style):
                continue
            value = cell.get('value', '')
            name, purpose, terms = DrawIOModule(name='', sequential_order=0).parse_html(value)
            if not name:
                continue
            cell_id = cell.get('id', '')
            module = DrawIOModule(name=name, sequential_order=order, description=purpose, seam_terms=terms)
            id_to_module[cell_id] = module
            if not cell_id.startswith('nest-'):
                model.modules.append(module)
            order += 1
        for cell in mxcells:
            if cell.get('vertex') != '1':
                continue
            child = id_to_module.get(cell.get('id', ''))
            parent = id_to_module.get(cell.get('parent', ''))
            if child is None or parent is None:
                continue
            if child not in model.modules or parent not in model.modules:
                continue
            if parent.name not in child.dependencies:
                child.dependencies.append(parent.name)
        for cell in mxcells:
            if cell.get('edge') != '1':
                continue
            src = id_to_module.get(cell.get('source', ''))
            tgt = id_to_module.get(cell.get('target', ''))
            if src is None or tgt is None:
                continue
            if src not in model.modules:
                continue
            if tgt.name not in src.dependencies:
                src.dependencies.append(tgt.name)
        return model

    def _parse_classes(self, mxcells: List[ET.Element]) -> 'DrawIOCleanEngineeringModel':
        model = DrawIOCleanEngineeringModel(name='', sequential_order=1)
        order = 1
        id_to_class: dict[str, OoadClass] = {}
        module = DrawIOModule(name='', sequential_order=1)
        for cell in mxcells:
            if cell.get('vertex') != '1':
                continue
            value = cell.get('value', '')
            name, props, ops = self._parse_class_html(value)
            if not name:
                continue
            oclass = DrawIOClass(name=name, sequential_order=order, properties=props, operations=ops)
            module.classes.append(oclass)
            id_to_class[cell.get('id', '')] = oclass
            order += 1
        if module.classes:
            model.modules.append(module)
        for cell in mxcells:
            if cell.get('edge') != '1':
                continue
            src_id = cell.get('source', '')
            tgt_id = cell.get('target', '')
            src_cls = id_to_class.get(src_id)
            if src_cls is None:
                continue
            tgt_cls = id_to_class.get(tgt_id)
            tgt_name = tgt_cls.name if tgt_cls else tgt_id
            kind = self._classify_edge(cell.get('style', ''))
            src_cls.relationships.append(Relationship(target=tgt_name, kind=kind))
        return model

    def _parse_classes_multipage(self, diagrams: List[ET.Element]) -> 'DrawIOCleanEngineeringModel':
        """One Draw.io page → one module; skip dashed «from:» import cards."""
        self._multi_model = DrawIOCleanEngineeringModel(name='', sequential_order=1)
        self._multi_order = 1
        self._seen_names = set()
        self._id_to_class = {}
        self._id_to_name = {}
        for diagram in diagrams:
            self._parse_multipage_diagram(diagram)
        return self._multi_model

    def _parse_multipage_diagram(self, diagram: ET.Element) -> None:
        page_name = diagram.get('name') or f'module-{self._multi_order}'
        module = DrawIOModule(name=page_name, sequential_order=self._multi_order)
        page_cells = list(diagram.iter('mxCell'))
        self._parse_multipage_vertices(page_cells, module)
        if module.classes:
            self._multi_model.modules.append(module)
            self._multi_order += 1
        self._parse_multipage_edges(page_cells)

    def _parse_multipage_vertices(self, page_cells, module) -> None:
        for cell in page_cells:
            if cell.get('vertex') != '1':
                continue
            style = cell.get('style', '')
            value = cell.get('value', '')
            name, props, ops = self._parse_class_html(value)
            if not name:
                continue
            cell_id = cell.get('id', '')
            self._id_to_name[cell_id] = name
            if 'dashed=1' in style:
                continue
            plain = self._plain_class_name(name)
            if plain in self._seen_names:
                continue
            self._seen_names.add(plain)
            oclass = DrawIOClass(name=name, sequential_order=len(module.classes) + 1, properties=props, operations=ops)
            module.classes.append(oclass)
            self._id_to_class[cell_id] = oclass

    def _parse_multipage_edges(self, page_cells) -> None:
        for cell in page_cells:
            if cell.get('edge') != '1':
                continue
            src_id = cell.get('source', '')
            tgt_id = cell.get('target', '')
            src_cls = self._id_to_class.get(src_id)
            if src_cls is None:
                continue
            tgt_cls = self._id_to_class.get(tgt_id)
            tgt_name = tgt_cls.name if tgt_cls is not None else self._id_to_name.get(tgt_id, tgt_id)
            kind = self._classify_edge(cell.get('style', ''))
            already = any((r.target == tgt_name and (r.kind or 'association') == kind for r in src_cls.relationships))
            if not already:
                src_cls.relationships.append(Relationship(target=tgt_name, kind=kind))

    def render(self, canonical: CleanEngineeringModel) -> str:
        if self._is_modules_view(canonical):
            return self._render_modules(canonical)
        return self._render_classes(canonical)

    def _render_modules(self, canonical: CleanEngineeringModel) -> str:
        prev_pos = self._read_positions(self.previous) if self.previous else {}
        mxfile = ET.Element('mxfile')
        mxfile.set('host', 'CleanEngineering.diagram.drawio')
        diagram = ET.SubElement(mxfile, 'diagram')
        diagram.set('name', 'Modules Context')
        diagram.set('id', 'modules-context')
        model_el = ET.SubElement(diagram, 'mxGraphModel')
        self._page_width = '1600'
        self._page_height = '1200'
        self._set_graph_attrs(model_el)
        root_el = ET.SubElement(model_el, 'root')
        cell0 = ET.SubElement(root_el, 'mxCell')
        cell0.set('id', '0')
        cell1 = ET.SubElement(root_el, 'mxCell')
        cell1.set('id', '1')
        cell1.set('parent', '0')
        system_name = canonical.name or 'System'
        forest = self._containment_forest(canonical.modules)
        layout = self._module_containment_layout(forest)
        max_x = max((b[0] + b[2] for b in layout.bounds.values()), default=MODULE_START_X)
        max_y = max((b[1] + b[3] for b in layout.bounds.values()), default=MODULE_START_Y)
        page_w = int(max(1600, max_x + 80))
        page_h = int(max(1200, max_y + 80))
        model_el.set('pageWidth', str(page_w))
        model_el.set('pageHeight', str(page_h))
        title = ET.SubElement(root_el, 'mxCell')
        title.set('id', 'title')
        title.set('value', f'{system_name} - Modules Context')
        title.set('style', MODULE_TITLE_STYLE)
        title.set('parent', '1')
        title.set('vertex', '1')
        title_geo = ET.SubElement(title, 'mxGeometry')
        title_geo.set('x', '40')
        title_geo.set('y', '20')
        title_geo.set('width', str(page_w - 80))
        title_geo.set('height', '32')
        title_geo.set('as', 'geometry')
        subtitle = ET.SubElement(root_el, 'mxCell')
        subtitle.set('id', 'subtitle')
        subtitle.set('value', 'Independent modules with one-way dependencies. Arrows point toward the depended-on module (build before). Path nesting = containment; shared base terms live on the parent.')
        subtitle.set('style', MODULE_SUBTITLE_STYLE)
        subtitle.set('parent', '1')
        subtitle.set('vertex', '1')
        sub_geo = ET.SubElement(subtitle, 'mxGeometry')
        sub_geo.set('x', '40')
        sub_geo.set('y', '55')
        sub_geo.set('width', str(page_w - 80))
        sub_geo.set('height', '20')
        sub_geo.set('as', 'geometry')
        name_to_id = dict(layout.name_to_id)
        for name in layout.render_order:
            module = forest.by_name[name]
            cell_id = name_to_id[name]
            parent_id = layout.parent_id.get(name, '1')
            x, y, w, h = layout.bounds[name]
            if cell_id in prev_pos and parent_id == '1':
                x, y = prev_pos[cell_id]
            style = MODULE_CHILD_STYLE if parent_id != '1' else MODULE_STYLE
            self._cell_id = cell_id
            self._cell_x = x
            self._cell_y = y
            self._cell_width = w
            self._cell_height = h
            self._cell_parent_id = parent_id
            self._cell_style = style
            self._create_module_cell(root_el, module)
        edge_counter = len(forest.by_name) + 20
        for module in canonical.modules:
            src_id = name_to_id.get(module.name)
            path_parent = self._path_parent(module.name)
            for dep in module.dependencies:
                if dep == path_parent:
                    continue
                tgt_id = name_to_id.get(dep)
                if not src_id or not tgt_id:
                    continue
                edge_counter += 1
                self._edge_src_id = src_id
                self._edge_tgt_id = tgt_id
                self._edge_id = f'dep-{edge_counter}'
                self._create_module_edge(root_el)
        ET.indent(ET.ElementTree(mxfile), space='  ')
        return ET.tostring(mxfile, encoding='unicode', xml_declaration=False)

    def _render_classes(self, canonical) -> str:
        name_to_id: dict[str, str] = {}
        id_to_oclass: Dict[str, OoadClass] = {}
        for oclass in canonical.classes:
            cell_id = self._slug(oclass.name)
            name_to_id[oclass.name] = cell_id
            plain = self._plain_class_name(oclass.name)
            if plain and plain != oclass.name:
                name_to_id.setdefault(plain, cell_id)
            id_to_oclass[cell_id] = oclass
        self._name_to_id = name_to_id
        self._id_to_oclass = id_to_oclass
        self._relationships = self._collect_relationships(canonical.classes, name_to_id)
        self._id_to_module = self._class_module_labels(canonical.modules)
        self._modules = canonical.modules
        named_modules = [m for m in canonical.modules if m.classes]
        if len(named_modules) < 2:
            return self._render_classes_single_page(canonical)
        return self._render_classes_multipage(named_modules)

    def _render_classes_multipage(self, named_modules) -> str:
        mxfile = ET.Element('mxfile')
        mxfile.set('host', 'CleanEngineering.diagram.drawio')
        for module in named_modules:
            self._render_one_module_page(mxfile, module)
        ET.indent(ET.ElementTree(mxfile), space='  ')
        return ET.tostring(mxfile, encoding='unicode', xml_declaration=False)

    def _render_one_module_page(self, mxfile, module) -> None:
        page_name = module.name.strip()
        root_el = self._add_diagram_page(mxfile, page_name)
        local_ids = [self._slug(c.name) for c in module.classes]
        local_set = set(local_ids)
        self._local_module_name = page_name
        import_ids = self._direct_import_ids(local_set)
        self._import_ids = import_ids
        self._local_id_list = local_ids
        self._local_ids = local_set
        placements = self._layout_page_with_imports(local_ids)
        self._placements = placements
        self._page_ids = local_set | set(import_ids)
        self._append_imported_class_cells(root_el)
        self._append_local_class_cells(root_el)
        self._render_edges_on_page(root_el)

    def _append_imported_class_cells(self, root_el) -> None:
        for iid in self._import_ids:
            self._from_module = self._id_to_module.get(iid, 'other')
            self._cell_id = iid
            x, y, _w, _h = self._placements[iid]
            self._cell_x = int(round(x))
            self._cell_y = int(round(y))
            self._create_imported_class_cell(root_el, self._id_to_oclass[iid])

    def _append_local_class_cells(self, root_el) -> None:
        for lid in self._local_id_list:
            self._cell_id = lid
            x, y, _w, _h = self._placements[lid]
            self._cell_x = int(round(x))
            self._cell_y = int(round(y))
            self._create_class_cell(root_el, self._id_to_oclass[lid])

    def _render_classes_single_page(self, canonical) -> str:
        mxfile = ET.Element('mxfile')
        mxfile.set('host', 'CleanEngineering.diagram.drawio')
        diagram = ET.SubElement(mxfile, 'diagram')
        diagram.set('name', 'CleanEngineering Model')
        diagram.set('id', 'CleanEngineering-model')
        model_el = ET.SubElement(diagram, 'mxGraphModel')
        self._page_width = '1654'
        self._page_height = '1169'
        self._set_graph_attrs(model_el)
        root_el = self._add_graph_root(model_el)
        self._place_and_draw_single_page(root_el, canonical)
        ET.indent(ET.ElementTree(mxfile), space='  ')
        return ET.tostring(mxfile, encoding='unicode', xml_declaration=False)

    def _add_graph_root(self, model_el) -> ET.Element:
        root_el = ET.SubElement(model_el, 'root')
        cell0 = ET.SubElement(root_el, 'mxCell')
        cell0.set('id', '0')
        cell1 = ET.SubElement(root_el, 'mxCell')
        cell1.set('id', '1')
        cell1.set('parent', '0')
        return root_el

    def _place_and_draw_single_page(self, root_el, canonical) -> None:
        previous = self.previous
        prev_pos = self._read_positions(previous) if previous else {}
        prev_edges = self._read_edges(previous) if self.keep_positioning and previous else {}
        self._previous_positions = prev_pos if previous else None
        if self.keep_positioning and previous:
            placements = self._layout_classes_keep_positioning(self._id_to_oclass)
        else:
            placements = self._layout_classes_clustered(self._id_to_oclass)
            placements = self._resolve_class_overlaps(placements)
        self._placements = placements
        self._local_id_list = [self._name_to_id[c.name] for c in canonical.classes]
        self._append_local_class_cells(root_el)
        kept_pairs = self._copy_kept_edges(root_el, prev_edges)
        page_rels = [(s, t, k) for s, t, k in self._relationships if (s, t) not in kept_pairs]
        self._relationships = page_rels
        self._page_ids = set(placements.keys())
        self._local_ids = None
        self._render_edges_on_page(root_el)

    def _copy_kept_edges(self, root_el, prev_edges) -> set:
        kept_pairs: set[Tuple[str, str]] = set()
        if not (self.keep_positioning and prev_edges):
            return kept_pairs
        for src_id, tgt_id, _kind in self._relationships:
            existing = prev_edges.get((src_id, tgt_id))
            if existing is None:
                continue
            self._append_copied_edge(root_el, existing)
            kept_pairs.add((src_id, tgt_id))
        return kept_pairs

    def sync(self, text: str, canonical: CleanEngineeringModel) -> UpdateReport:
        return canonical.translate_from(self.parse(text))

    def _is_modules_view(self, canonical: CleanEngineeringModel) -> bool:
        return is_modules_view(canonical)

    def _looks_like_modules_diagram(self, mxcells: List[ET.Element]) -> bool:
        module_cells, class_cells = self._count_diagram_cell_kinds(mxcells)
        if module_cells and (not class_cells):
            return True
        if module_cells > class_cells:
            return True
        return False

    def _count_diagram_cell_kinds(self, mxcells: List[ET.Element]) -> Tuple[int, int]:
        module_cells = 0
        class_cells = 0
        for cell in mxcells:
            kind = self._vertex_diagram_kind(cell)
            if kind == 'module':
                module_cells += 1
            elif kind == 'class':
                class_cells += 1
        return (module_cells, class_cells)

    def _vertex_diagram_kind(self, cell: ET.Element) -> Optional[str]:
        if cell.get('vertex') != '1':
            return None
        style = cell.get('style', '')
        value = cell.get('value', '')
        if 'text;' in style or style.startswith('text;'):
            return None
        if self._is_module_style(style):
            return 'module'
        name, props, ops = self._parse_class_html(value)
        if name and (props or ops or 'hr size=' in value.lower()):
            return 'class'
        if name and ('\u2022' in html.unescape(value) or '-' in html.unescape(value)):
            return 'module'
        return None

    def _slug(self, name: str) -> str:
        return re.sub('\\W+', '-', name).lower().strip('-')

    def _plain_class_name(self, name: str) -> str:
        return DiagramClass(name=name, sequential_order=1).display_name()

    def _extends_base_name(self, name: str) -> Optional[str]:
        return DiagramClass(name=name, sequential_order=1).extends_base_name()

    def _is_module_style(self, style: str) -> bool:
        return _MODULE_MARKER in style or _MODULE_CHILD_MARKER in style or 'fillColor=#1a3a6e' in style or ('fillColor=#dae8fc' in style)

    def _path_parent(self, name: str) -> Optional[str]:
        return path_parent(name)

    def _set_graph_attrs(self, el) -> None:
        page_width = self._page_width or '1654'
        page_height = self._page_height or '1169'
        for k, v in [('dx', '1200'), ('dy', '800'), ('grid', '1'), ('gridSize', '10'), ('guides', '1'), ('tooltips', '1'), ('connect', '1'), ('arrows', '1'), ('fold', '1'), ('page', '1'), ('pageScale', '1'), ('pageWidth', page_width), ('pageHeight', page_height), ('math', '0'), ('shadow', '0')]:
            el.set(k, v)

    def _containment_forest(self, modules: List[Module]) -> ContainmentForest:
        return ContainmentForest.build(modules, synthesize_parents=True)

    def _module_dep_depth(self, name: str) -> int:
        return self._forest.module_dep_depth(name)

    def _size_subtree(self, name: str, forest: ContainmentForest) -> Tuple[float, float]:
        """Return (width, height) for a module cell including nested children."""
        module = forest.by_name[name]
        kids = forest.children_of.get(name, [])
        header_h = float(self.load_module(module).header_height())
        if not kids:
            return (float(MODULE_CELL_WIDTH), max(float(MODULE_CELL_MIN_HEIGHT), header_h))
        child_sizes = [self._size_subtree(c, forest) for c in kids]
        cols = min(MODULE_CHILD_COLS, len(kids))
        rows = (len(kids) + cols - 1) // cols
        col_widths = [0.0] * cols
        row_heights = [0.0] * rows
        for i, (cw, ch) in enumerate(child_sizes):
            c, r = (i % cols, i // cols)
            col_widths[c] = max(col_widths[c], cw)
            row_heights[r] = max(row_heights[r], ch)
        grid_w = sum(col_widths) + MODULE_CHILD_GAP * (cols - 1)
        grid_h = sum(row_heights) + MODULE_CHILD_GAP * (rows - 1)
        width = max(float(MODULE_CELL_WIDTH), grid_w + 2 * MODULE_CHILD_PAD_X)
        height = header_h + grid_h + 2 * MODULE_CHILD_PAD_Y
        return (width, height)

    def _place_subtree(self, name: str) -> None:
        forest = self._forest
        layout = self._layout
        module = forest.by_name[name]
        w, h = self._size_subtree(name, forest)
        if self._cell_parent_id == '1':
            layout.bounds[name] = (self._abs_x, self._abs_y, w, h)
        synthetic = name in forest.synthetic
        cell_id = f'nest-{self._slug(name)}' if synthetic else self._slug(name) or name
        layout.name_to_id[name] = cell_id
        layout.parent_id[name] = self._cell_parent_id
        layout.render_order.append(name)
        if not forest.children_of.get(name, []):
            return
        self._place_subtree_children(name, cell_id)

    def _place_subtree_children(self, name: str, cell_id: str) -> None:
        forest = self._forest
        layout = self._layout
        module = forest.by_name[name]
        kids = forest.children_of.get(name, [])
        header_h = float(self.load_module(module).header_height())
        cols = min(MODULE_CHILD_COLS, len(kids))
        child_sizes = [self._size_subtree(c, forest) for c in kids]
        col_widths, row_heights = self._child_grid_extents(child_sizes, cols)
        abs_x, abs_y = (self._abs_x, self._abs_y)
        for i, child in enumerate(kids):
            c, r = (i % cols, i // cols)
            rel_x = MODULE_CHILD_PAD_X + sum(col_widths[:c]) + MODULE_CHILD_GAP * c
            rel_y = header_h + MODULE_CHILD_PAD_Y + sum(row_heights[:r]) + MODULE_CHILD_GAP * r
            cw, ch = child_sizes[i]
            layout.bounds[child] = (rel_x, rel_y, cw, ch)
            self._abs_x = abs_x + rel_x
            self._abs_y = abs_y + rel_y
            self._cell_parent_id = cell_id
            self._place_subtree(child)
        self._abs_x, self._abs_y = (abs_x, abs_y)

    def _child_grid_extents(self, child_sizes, cols) -> Tuple[List[float], List[float]]:
        rows = (len(child_sizes) + cols - 1) // cols
        col_widths = [0.0] * cols
        row_heights = [0.0] * rows
        for i, (cw, ch) in enumerate(child_sizes):
            c, r = (i % cols, i // cols)
            col_widths[c] = max(col_widths[c], cw)
            row_heights[r] = max(row_heights[r], ch)
        return (col_widths, row_heights)

    def _module_containment_layout(self, forest: ContainmentForest) -> _ContainmentLayout:
        """Layer roots by dependency depth; nest path children inside parents."""
        self._forest = forest
        layout = _ContainmentLayout()
        if not forest.roots:
            return layout
        self._layout = layout
        layers = self._roots_by_dep_depth()
        self._place_layered_roots(layers)
        return layout

    def _roots_by_dep_depth(self) -> Dict[int, List[str]]:
        forest = self._forest
        layers: Dict[int, List[str]] = {}
        for root in forest.roots:
            d = self._module_dep_depth(root)
            layers.setdefault(d, []).append(root)
        for d in layers:
            layers[d].sort(key=lambda n: (forest.by_name[n].sequential_order or 0, n))
        return layers

    def _place_layered_roots(self, layers: Dict[int, List[str]]) -> None:
        forest = self._forest
        layout = self._layout
        layer_widths = {d: max((self._size_subtree(n, forest)[0] for n in names)) for d, names in layers.items()}
        x_cursor = float(MODULE_START_X)
        for d in sorted(layers):
            y = float(MODULE_START_Y)
            for name in layers[d]:
                self._abs_x = x_cursor
                self._abs_y = y
                self._cell_parent_id = '1'
                self._place_subtree(name)
                _w, h = (layout.bounds[name][2], layout.bounds[name][3])
                y += h + MODULE_ROW_GAP
            x_cursor += layer_widths[d] + MODULE_COL_GAP

    def _read_positions(self, previous: str) -> Dict[str, Tuple[float, float]]:
        out: Dict[str, Tuple[float, float]] = {}
        try:
            root = ET.fromstring(previous)
        except ET.ParseError:
            return out
        for cell in root.iter('mxCell'):
            pos = self._vertex_cell_position(cell)
            if pos is None:
                continue
            cell_id, xy = pos
            out[cell_id] = xy
        return out

    def _vertex_cell_position(self, cell):
        if cell.get('vertex') != '1':
            return None
        cell_id = cell.get('id', '')
        geo = cell.find('mxGeometry')
        if geo is None or not cell_id:
            return None
        x = geo.get('x')
        y = geo.get('y')
        if x is None or y is None:
            return None
        try:
            return (cell_id, (float(x), float(y)))
        except ValueError:
            return None

    def _read_edges(self, previous: str) -> Dict[Tuple[str, str], ET.Element]:
        """Index existing DrawIO edges by (source, target) so they can be reused."""
        out: Dict[Tuple[str, str], ET.Element] = {}
        try:
            root = ET.fromstring(previous)
        except ET.ParseError:
            return out
        for cell in root.iter('mxCell'):
            if cell.get('edge') != '1':
                continue
            src = cell.get('source')
            tgt = cell.get('target')
            if src and tgt:
                out[src, tgt] = cell
        return out

    def _append_copied_edge(self, root_el: ET.Element, edge: ET.Element) -> None:
        root_el.append(copy.deepcopy(edge))

    def _place_new_classes_clear_of_existing(self, new_placements: Dict[str, Tuple[float, float, float, float]], existing_placements: Dict[str, Tuple[float, float, float, float]]) -> Dict[str, Tuple[float, float, float, float]]:
        """Shift newly laid-out classes so they do not overlap kept positions."""
        if not new_placements:
            return new_placements
        if not existing_placements:
            return new_placements
        max_right = max((x + w for x, _y, w, _h in existing_placements.values()))
        min_new_x = min((x for x, _y, _w, _h in new_placements.values()))
        shift_x = max_right + CLUSTER_GAP_X - min_new_x
        if shift_x < 0:
            shift_x = 0.0
        shifted = {cid: (x + shift_x, y, w, h) for cid, (x, y, w, h) in new_placements.items()}
        for cid in list(shifted):
            while any((self._rects_overlap(shifted[cid], geo) for geo in existing_placements.values())):
                x, y, w, h = shifted[cid]
                shifted[cid] = (x, y + OVERLAP_GAP, w, h)
        return shifted

    def _layout_classes_keep_positioning(self, id_to_oclass) -> Dict[str, Tuple[float, float, float, float]]:
        """Keep existing class positions; layout only classes that are new."""
        placements, new_ids = self._kept_and_new_class_ids(id_to_oclass)
        if not new_ids:
            return placements
        new_placements = self._layout_new_classes(id_to_oclass, new_ids)
        new_placements = self._place_new_classes_clear_of_existing(new_placements, placements)
        placements.update(new_placements)
        return placements

    def _kept_and_new_class_ids(self, id_to_oclass):
        previous_positions = self._previous_positions or {}
        placements: Dict[str, Tuple[float, float, float, float]] = {}
        new_ids: List[str] = []
        for cid, oclass in id_to_oclass.items():
            if cid in previous_positions:
                x, y = previous_positions[cid]
                placements[cid] = (x, y, float(CELL_WIDTH), float(self.load_class(oclass).height()))
            else:
                new_ids.append(cid)
        return (placements, new_ids)

    def _layout_new_classes(self, id_to_oclass, new_ids):
        saved_id_to_oclass = self._id_to_oclass
        saved_rels = self._relationships
        saved_prev = self._previous_positions
        self._id_to_oclass = {cid: id_to_oclass[cid] for cid in new_ids}
        self._relationships = [(src, tgt, kind) for src, tgt, kind in saved_rels if src in self._id_to_oclass and tgt in self._id_to_oclass]
        self._previous_positions = None
        new_placements = self._layout_classes_clustered(self._id_to_oclass)
        self._id_to_oclass = saved_id_to_oclass
        self._relationships = saved_rels
        self._previous_positions = saved_prev
        return new_placements

    def _create_module_cell(self, root_el, module) -> ET.Element:
        node = self.load_module(module)
        node.cell_id = self._cell_id
        node.parent_id = self._cell_parent_id
        node.nested = self._cell_style == MODULE_CHILD_STYLE
        width = self._cell_width if self._cell_width is not None else MODULE_CELL_WIDTH
        height = self._cell_height if self._cell_height is not None else node.height()
        node.geometry = Geometry(float(self._cell_x), float(self._cell_y), float(width), float(height))
        return Page('', root_el).place(node)

    def _create_module_edge(self, root_el) -> ET.Element:
        cell = ET.SubElement(root_el, 'mxCell')
        cell.set('id', self._edge_id)
        cell.set('value', '')
        cell.set('style', MODULE_DEP_EDGE_STYLE)
        cell.set('edge', '1')
        cell.set('source', self._edge_src_id)
        cell.set('target', self._edge_tgt_id)
        cell.set('parent', '1')
        geo = ET.SubElement(cell, 'mxGeometry')
        geo.set('relative', '1')
        geo.set('as', 'geometry')
        return cell

    def _create_class_cell(self, root_el, oclass) -> ET.Element:
        node = self.load_class(oclass)
        node.cell_id = self._cell_id
        node.geometry = Geometry(
            float(self._cell_x),
            float(self._cell_y),
            float(CELL_WIDTH),
            float(node.height()),
        )
        return Page('', root_el).place(node)

    def _module_tab_label(self, module_name: str) -> str:
        return module_tab_label(module_name)

    def _class_module_labels(self, modules: List[Module]) -> dict[str, str]:
        """Map class cell id → owning module short label for import stereotypes."""
        out: dict[str, str] = {}
        for module in modules:
            label = self._module_tab_label(module.name)
            for oclass in module.classes:
                out[self._slug(oclass.name)] = label
                plain = self._plain_class_name(oclass.name)
                if plain:
                    out.setdefault(self._slug(plain), label)
        return out

    def _collect_relationships(self, classes: List[OoadClass], name_to_id: dict[str, str]) -> List[Tuple[str, str, str]]:
        relationships = [(name_to_id[c.name], name_to_id[rel.target], rel.kind or 'association') for c in classes for rel in c.relationships if rel.target in name_to_id]
        for oclass in classes:
            base = self._extends_base_name(oclass.name)
            if base and base in name_to_id:
                pair = (name_to_id[oclass.name], name_to_id[base], 'inheritance')
                if pair not in relationships:
                    relationships.append(pair)
        return relationships

    def _direct_import_ids(self, local_ids) -> List[str]:
        """Foreign class ids with a direct link from this aggregate.

    Imports:
    - targets of edges that leave a local class (local → foreign)
    - foreign subtypes that inherit into a local base (foreign → local, inheritance)

    Inbound association sources stay on the other aggregate's tab.
    """
        self._import_local_ids = local_ids
        self._import_local_label = self._module_tab_label(self._local_module_name)
        imports: set[str] = set()
        for src, tgt, kind in self._relationships:
            self._edge_src = src
            self._edge_tgt = tgt
            self._edge_kind = kind
            if self._is_outbound_import():
                imports.add(tgt)
            elif self._is_inbound_inheritance_import():
                imports.add(src)
        return sorted(imports)

    def _is_outbound_import(self) -> bool:
        src, tgt = self._edge_src, self._edge_tgt
        local_ids = self._import_local_ids
        if src not in local_ids or tgt in local_ids:
            return False
        return self._id_to_module.get(tgt, '') != self._import_local_label

    def _is_inbound_inheritance_import(self) -> bool:
        src, tgt = self._edge_src, self._edge_tgt
        local_ids = self._import_local_ids
        if tgt not in local_ids or src in local_ids:
            return False
        if (self._edge_kind or 'association').lower() != 'inheritance':
            return False
        return self._id_to_module.get(src, '') != self._import_local_label

    def _create_imported_class_cell(self, root_el, oclass) -> ET.Element:
        node = self._imported_class(oclass, self._from_module)
        node.cell_id = self._cell_id
        node.geometry = Geometry(
            float(self._cell_x),
            float(self._cell_y),
            float(CELL_WIDTH),
            float(node.height()),
        )
        return Page('', root_el).place(node)

    def _layout_page_with_imports(self, local_ids) -> Dict[str, Tuple[float, float, float, float]]:
        """Pack locals tightly; inheritance imports above, others beside linkers."""
        local_set = set(local_ids)
        page_rels = [(s, t, k) for s, t, k in self._relationships if s in local_set and t in local_set]
        self._origin_x = float(START_X)
        self._origin_y = float(START_Y)
        self._pack_cols = 3
        saved_rels = self._relationships
        self._relationships = page_rels
        local_map, _width, _height = self._pack_cluster(local_ids)
        self._relationships = saved_rels
        self._placements = dict(local_map)
        if not self._import_ids:
            return self._resolve_class_overlaps(self._placements)
        self._place_page_imports()
        return self._resolve_class_overlaps(self._placements)

    def _linkers_for(self, imported_id: str) -> List[Tuple[str, str]]:
        out: List[Tuple[str, str]] = []
        for s, t, k in self._relationships:
            kind = (k or 'association').lower()
            if s == imported_id and t in self._placements:
                out.append((t, kind))
            elif t == imported_id and s in self._placements:
                out.append((s, kind))
        return out

    def _place_page_imports(self) -> None:
        parents, children, beside_ids = self._classify_import_bands()
        if parents:
            self._place_inheritance_parents(parents)
        self._place_inheritance_children(children)
        self._place_beside_imports(beside_ids)

    def _classify_import_bands(self) -> Tuple[List[str], List[str], List[str]]:
        inheritance_parents = []
        inheritance_children = []
        for iid in self._import_ids:
            links = self._linkers_for(iid)
            if any((k == 'inheritance' for _lid, k in links)):
                if any((s == iid and t in self._placements and ((k or '').lower() == 'inheritance') for s, t, k in self._relationships)):
                    inheritance_children.append(iid)
                else:
                    inheritance_parents.append(iid)
        beside_ids = [iid for iid in self._import_ids if iid not in inheritance_parents and iid not in inheritance_children]
        return (inheritance_parents, inheritance_children, beside_ids)

    def _place_inheritance_parents(self, inheritance_parents: List[str]) -> None:
        band_h = max((float(self._imported_class(self._id_to_oclass[i]).height()) for i in inheritance_parents)) + INNER_ROW_GAP * 2
        self._placements = {cid: (x, y + band_h, w, h) for cid, (x, y, w, h) in self._placements.items()}
        used: List[Tuple[float, float, float, float]] = []
        for iid in inheritance_parents:
            used.append(self._place_one_inheritance_parent(iid, used))

    def _place_one_inheritance_parent(self, iid: str, used: List) -> Tuple[float, float, float, float]:
        h = float(self._imported_class(self._id_to_oclass[iid]).height())
        links = self._linkers_for(iid)
        primary = min((lid for lid, _k in links), key=lambda lid: (self._placements[lid][1], self._placements[lid][0]))
        x = self._placements[primary][0]
        y = float(START_Y)
        candidate = (x, y, float(CELL_WIDTH), h)
        for _ in range(12):
            if all((not self._rects_overlap(candidate, geo) for geo in used)):
                break
            x += CELL_WIDTH + INNER_COL_GAP
            candidate = (x, y, float(CELL_WIDTH), h)
        self._placements[iid] = candidate
        return candidate

    def _place_inheritance_children(self, inheritance_children: List[str]) -> None:
        child_slots: dict[str, int] = {}
        for iid in inheritance_children:
            h = float(self._imported_class(self._id_to_oclass[iid]).height())
            links = self._linkers_for(iid)
            primary = min((lid for lid, _k in links), key=lambda lid: (self._placements[lid][1], self._placements[lid][0]))
            px, py, _pw, ph = self._placements[primary]
            slot = child_slots.get(primary, 0)
            child_slots[primary] = slot + 1
            x = px + slot * (CELL_WIDTH + INNER_COL_GAP)
            y = py + ph + INNER_ROW_GAP
            self._placements[iid] = (x, y, float(CELL_WIDTH), h)

    def _place_beside_imports(self, beside_ids: List[str]) -> None:
        from collections import defaultdict
        by_hub: dict[str, List[str]] = defaultdict(list)
        orphan_imports: List[str] = []
        for iid in beside_ids:
            links = self._linkers_for(iid)
            if not links:
                orphan_imports.append(iid)
                continue
            ys = sorted((self._placements[lid][1] for lid, _k in links))
            mid_y = ys[len(ys) // 2]
            primary = min((lid for lid, _k in links), key=lambda lid: (abs(self._placements[lid][1] - mid_y), self._placements[lid][0]))
            by_hub[primary].append(iid)
        self._fan_imports_by_hub(by_hub)
        for iid in orphan_imports:
            h = float(self._imported_class(self._id_to_oclass[iid]).height())
            self._placements[iid] = (float(START_X), float(START_Y), float(CELL_WIDTH), h)

    def _fan_imports_by_hub(self, by_hub) -> None:
        self._fan_cols = 2
        for hub, iids in by_hub.items():
            self._fan_hx, self._fan_hy, _hw, _hh = self._placements[hub]
            for idx, iid in enumerate(iids):
                self._fan_idx = idx
                self._place_fanned_import(iid)

    def _place_fanned_import(self, iid) -> None:
        h = float(self._imported_class(self._id_to_oclass[iid]).height())
        col = self._fan_idx % self._fan_cols
        row = self._fan_idx // self._fan_cols
        hx, hy = self._fan_hx, self._fan_hy
        x = hx + CELL_WIDTH + INNER_COL_GAP + col * (CELL_WIDTH + INNER_COL_GAP)
        y = hy + row * (h + INNER_ROW_GAP)
        candidate = (x, y, float(CELL_WIDTH), h)
        guard = 0
        while any((self._rects_overlap(candidate, geo) for oid, geo in self._placements.items() if oid != iid)) and guard < 20:
            guard += 1
            row += 1
            y = hy + row * (h + INNER_ROW_GAP)
            candidate = (x, y, float(CELL_WIDTH), h)
        self._placements[iid] = candidate

    def _add_diagram_page(self, mxfile: ET.Element, page_name: str) -> ET.Element:
        diagram = ET.SubElement(mxfile, 'diagram')
        diagram.set('name', page_name)
        diagram.set('id', f'page-{self._slug(page_name)}')
        model_el = ET.SubElement(diagram, 'mxGraphModel')
        self._page_width = '1654'
        self._page_height = '1169'
        self._set_graph_attrs(model_el)
        root_el = ET.SubElement(model_el, 'root')
        cell0 = ET.SubElement(root_el, 'mxCell')
        cell0.set('id', '0')
        cell1 = ET.SubElement(root_el, 'mxCell')
        cell1.set('id', '1')
        cell1.set('parent', '0')
        return root_el

    def _render_edges_on_page(self, root_el) -> None:
        """Wire edges present on this page.

    When *local_ids* is set (per-aggregate tabs), only draw:
    - edges that leave a local class (local → local/import)
    - inheritance into a local base (import → local, inheritance)

    Never import↔import, and never inbound association from an import.
    """
        edge_specs = self._page_edge_specs()
        self._assign_distinct_anchors(edge_specs)
        edge_specs.sort(key=self._edge_sort_key)
        self._draw_routed_edges(root_el, edge_specs)

    def _page_relationships(self) -> List[Tuple[str, str, str]]:
        page_ids = self._page_ids
        local_ids = self._local_ids
        return [(s, t, k) for s, t, k in self._relationships if s in page_ids and t in page_ids and (local_ids is None or s in local_ids or (t in local_ids and (k or '').lower() == 'inheritance'))]

    def _page_edge_specs(self) -> List[dict]:
        edge_specs: List[dict] = []
        for src_id, tgt_id, kind in self._page_relationships():
            exit_side, entry_side = self._preferred_sides(self._placements[src_id], self._placements[tgt_id])
            edge_specs.append({'src_id': src_id, 'tgt_id': tgt_id, 'kind': kind, 'exit_side': exit_side, 'entry_side': entry_side})
        return edge_specs

    def _edge_sort_key(self, spec: dict) -> Tuple[int, float, str]:
        s = self._placements[spec['src_id']]
        t = self._placements[spec['tgt_id']]
        dist = abs(s[0] + s[2] / 2 - (t[0] + t[2] / 2)) + abs(s[1] + s[3] / 2 - (t[1] + t[3] / 2))
        ownership = 0 if self._ownership_kinds(spec['kind']) else 1
        return (ownership, dist, spec['src_id'])

    def _draw_routed_edges(self, root_el, edge_specs) -> None:
        used_ids = {cell.get('id', '') for cell in root_el.iter('mxCell')}
        numeric_ids = [int(i) for i in used_ids if i.isdigit()]
        edge_counter = max(numeric_ids) if numeric_ids else len(self._page_ids) + 10
        self._routed_segments: List[List[Tuple[Tuple[float, float], Tuple[float, float]]]] = []
        for lane_idx, spec in enumerate(edge_specs):
            edge_counter += 1
            self._edge_spec = spec
            self._edge_counter = edge_counter
            self._lane_idx = lane_idx
            self._draw_one_routed_edge(root_el)

    def _draw_one_routed_edge(self, root_el) -> None:
        spec = self._edge_spec
        self._exit_x, self._exit_y = self._side_anchor(spec['exit_side'], spec['exit_frac'])
        self._entry_x, self._entry_y = self._side_anchor(spec['entry_side'], spec['entry_frac'])
        self._bind_route_from_spec()
        self._waypoints = self._route_waypoints(self._placements[spec['src_id']])
        self._route_trial_points = self._waypoints
        self._edge_src_id = spec['src_id']
        self._edge_tgt_id = spec['tgt_id']
        self._edge_kind = spec['kind']
        self._edge_id = str(self._edge_counter)
        self._create_edge(root_el)
        self._routed_segments.append(self._segments_from_route(self._placements[spec['src_id']]))

    def _bind_route_from_spec(self) -> None:
        spec = self._edge_spec
        self._route_tgt = self._placements[spec['tgt_id']]
        self._exit_side = spec['exit_side']
        self._entry_side = spec['entry_side']
        self._exit_frac = spec['exit_frac']
        self._entry_frac = spec['entry_frac']
        self._obstacles = [geo for cid, geo in self._placements.items() if cid not in (spec['src_id'], spec['tgt_id'])]
        self._route_lane = self._lane_idx * ROUTE_LANE_STEP
        self._avoid_segments = self._routed_segments
        self._all_placements = self._placements

    def _create_edge(self, root_el) -> ET.Element:
        style = self._edge_anchor_style()
        cell = ET.SubElement(root_el, 'mxCell')
        cell.set('id', self._edge_id)
        cell.set('value', '')
        cell.set('style', style)
        cell.set('edge', '1')
        cell.set('source', self._edge_src_id)
        cell.set('target', self._edge_tgt_id)
        cell.set('parent', '1')
        geo = ET.SubElement(cell, 'mxGeometry')
        geo.set('relative', '1')
        geo.set('as', 'geometry')
        self._append_edge_waypoints(geo)
        return cell

    def _edge_anchor_style(self) -> str:
        style = EDGE_STYLES.get(self._edge_kind, DEFAULT_EDGE_STYLE)
        parts = self._edge_anchor_parts()
        if parts:
            style = style.rstrip(';') + ';' + ';'.join(parts) + ';'
        return style

    def _edge_anchor_parts(self) -> List[str]:
        parts: List[str] = []
        if self._exit_x is not None:
            parts.append(f'exitX={self._exit_x}')
        if self._exit_y is not None:
            parts.append(f'exitY={self._exit_y}')
        if self._exit_x is not None or self._exit_y is not None:
            parts.extend(['exitDx=0', 'exitDy=0'])
        if self._entry_x is not None:
            parts.append(f'entryX={self._entry_x}')
        if self._entry_y is not None:
            parts.append(f'entryY={self._entry_y}')
        if self._entry_x is not None or self._entry_y is not None:
            parts.extend(['entryDx=0', 'entryDy=0'])
        return parts

    def _append_edge_waypoints(self, geo) -> None:
        if not self._waypoints:
            return
        arr = ET.SubElement(geo, 'Array')
        arr.set('as', 'points')
        for wx, wy in self._waypoints:
            pt = ET.SubElement(arr, 'mxPoint')
            pt.set('x', str(int(round(wx))))
            pt.set('y', str(int(round(wy))))

    def _rects_overlap(self, first, second) -> bool:
        ax, ay, aw, ah = first
        bx, by, bw, bh = second
        gap = OVERLAP_GAP
        return ax < bx + bw + gap and ax + aw + gap > bx and (ay < by + bh + gap) and (ay + ah + gap > by)

    def _resolve_class_overlaps(self, placements: Dict[str, Tuple[float, float, float, float]], prefer_move: Optional[set[str]]=None) -> Dict[str, Tuple[float, float, float, float]]:
        """Push overlapping class boxes apart — prefer sideways on the same row.

    *prefer_move* ids (e.g. imports) are shifted right instead of shoving local
    packs down into long vertical spines.
    """
        self._prefer_move = prefer_move or set()
        self._overlap_placements = placements
        ids = list(placements.keys())
        for _ in range(len(ids) * len(ids) + 1):
            if not self._nudge_one_overlap(ids):
                break
        return placements

    def _nudge_one_overlap(self, ids) -> bool:
        placements = self._overlap_placements
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                if self._rects_overlap(placements[a], placements[b]):
                    self._overlap_a = a
                    self._overlap_b = b
                    self._separate_overlap_pair()
                    return True
        return False

    def _separate_overlap_pair(self) -> None:
        placements = self._overlap_placements
        a, b = self._overlap_a, self._overlap_b
        ax, ay, aw, ah = placements[a]
        bx, by, bw, bh = placements[b]
        prefer_move = self._prefer_move
        if a in prefer_move and b not in prefer_move:
            placements[a] = (bx + bw + OVERLAP_GAP, ay, aw, ah)
            return
        if b in prefer_move and a not in prefer_move:
            placements[b] = (ax + aw + OVERLAP_GAP, by, bw, bh)
            return
        self._separate_same_or_stacked()

    def _separate_same_or_stacked(self) -> None:
        placements = self._overlap_placements
        a, b = self._overlap_a, self._overlap_b
        ax, ay, aw, ah = placements[a]
        bx, by, bw, bh = placements[b]
        same_row = abs(ay - by) <= max(ah, bh) * 0.6
        if same_row and ax <= bx:
            placements[b] = (ax + aw + OVERLAP_GAP, by, bw, bh)
            return
        if same_row:
            placements[a] = (bx + bw + OVERLAP_GAP, ay, aw, ah)
            return
        if ay <= by:
            placements[b] = (bx, ay + ah + OVERLAP_GAP, bw, bh)
            return
        placements[a] = (ax, by + bh + OVERLAP_GAP, aw, ah)

    def _preferred_sides(self, src: Tuple[float, float, float, float], tgt: Tuple[float, float, float, float]) -> Tuple[str, str]:
        sx, sy, sw, sh = src
        tx, ty, tw, th = tgt
        scx, scy = (sx + sw / 2.0, sy + sh / 2.0)
        tcx, tcy = (tx + tw / 2.0, ty + th / 2.0)
        dx, dy = (tcx - scx, tcy - scy)
        if abs(dy) >= max(abs(dx) * 0.6, (sh + th) * 0.25):
            if dy >= 0:
                return ('bottom', 'top')
            return ('top', 'bottom')
        if abs(dx) >= abs(dy):
            if dx >= 0:
                return ('right', 'left')
            return ('left', 'right')
        if dy >= 0:
            return ('bottom', 'top')
        return ('top', 'bottom')

    def _side_anchor(self, side: str, frac: float) -> Tuple[float, float]:
        if side == 'top':
            return (frac, 0.0)
        if side == 'bottom':
            return (frac, 1.0)
        if side == 'left':
            return (0.0, frac)
        return (1.0, frac)

    def _distribute_fracs(self, count: int) -> List[float]:
        if count <= 1:
            return [0.5]
        return [round(0.15 + 0.7 * i / (count - 1), 3) for i in range(count)]

    def _assign_distinct_anchors(self, edge_specs: List[dict]) -> None:
        from collections import defaultdict
        exit_groups: dict[Tuple[str, str], List[int]] = defaultdict(list)
        entry_groups: dict[Tuple[str, str], List[int]] = defaultdict(list)
        for idx, spec in enumerate(edge_specs):
            exit_groups[spec['src_id'], spec['exit_side']].append(idx)
            entry_groups[spec['tgt_id'], spec['entry_side']].append(idx)
        for idxs in exit_groups.values():
            for frac, idx in zip(self._distribute_fracs(len(idxs)), idxs):
                edge_specs[idx]['exit_frac'] = frac
        for idxs in entry_groups.values():
            for frac, idx in zip(self._distribute_fracs(len(idxs)), idxs):
                edge_specs[idx]['entry_frac'] = frac

    def _point_on_side(self, geo, side) -> Tuple[float, float]:
        frac = self._anchor_frac
        x, y, w, h = geo
        if side == 'top':
            return (x + w * frac, y)
        if side == 'bottom':
            return (x + w * frac, y + h)
        if side == 'left':
            return (x, y + h * frac)
        return (x + w, y + h * frac)

    def _outward_point(self, geo, side) -> Tuple[float, float]:
        ax, ay = self._point_on_side(geo, side)
        clearance = self._clearance
        if side == 'top':
            return (ax, ay - clearance)
        if side == 'bottom':
            return (ax, ay + clearance)
        if side == 'left':
            return (ax - clearance, ay)
        return (ax + clearance, ay)

    def _polyline_hits_obstacle(self, points) -> bool:
        margin = self._hit_margin
        for i in range(len(points) - 1):
            start_x, start_y = points[i]
            end_x, end_y = points[i + 1]
            for left, top, width, height in self._obstacles:
                if self._line_intersects_rect(
                    (start_x, start_y, end_x, end_y),
                    (left, top, width, height, margin),
                ):
                    return True
        return False

    def _line_intersects_rect(self, segment, rect) -> bool:
        start_x, start_y, end_x, end_y = segment
        left, top, width, height, margin = rect
        left -= margin
        top -= margin
        width += 2 * margin
        height += 2 * margin
        corners = [
            (left, top),
            (left + width, top),
            (left + width, top + height),
            (left, top + height),
        ]
        sides = [
            (corners[0], corners[1]),
            (corners[1], corners[2]),
            (corners[2], corners[3]),
            (corners[3], corners[0]),
        ]
        for first, second in sides:
            if self._segments_cross_2d(
                (start_x, start_y, end_x, end_y),
                (first[0], first[1], second[0], second[1]),
            ):
                return True
        if left <= start_x <= left + width and top <= start_y <= top + height:
            return True
        return False

    def _ccw_2d(self, first, second) -> bool:
        ax, ay = first
        bx, by = second
        cx, cy = self._ccw_third
        return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)

    def _segments_cross_2d(self, first, second) -> bool:
        ax, ay, bx, by = first
        cx, cy, dx, dy = second
        self._ccw_third = (dx, dy)
        first_turn = self._ccw_2d((ax, ay), (cx, cy)) != self._ccw_2d((bx, by), (cx, cy))
        self._ccw_third = (cx, cy)
        second_turn = self._ccw_2d((ax, ay), (bx, by))
        self._ccw_third = (dx, dy)
        return first_turn and second_turn != self._ccw_2d((ax, ay), (bx, by))

    def _dedupe_points(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        out: List[Tuple[float, float]] = []
        for pt in points:
            if not out or abs(out[-1][0] - pt[0]) > 0.5 or abs(out[-1][1] - pt[1]) > 0.5:
                out.append(pt)
        return out

    def _column_gutters(self, placements: Dict[str, Tuple[float, float, float, float]]) -> List[float]:
        """Vertical channel x positions: page margins + midpoints between class columns."""
        if not placements:
            return [START_X - ROUTE_CLEARANCE]
        xs = sorted({int(round(geo[0])) for geo in placements.values()})
        gutters = [float(xs[0] - ROUTE_CLEARANCE)]
        for i, x in enumerate(xs):
            gutters.append(float(x + CELL_WIDTH + COL_GAP / 2.0))
        gutters.append(float(xs[-1] + CELL_WIDTH + ROUTE_CLEARANCE))
        out: List[float] = []
        for g in sorted(gutters):
            if not out or abs(out[-1] - g) > 1:
                out.append(g)
        return out

    def _row_highways(self, placements: Dict[str, Tuple[float, float, float, float]]) -> List[float]:
        """Horizontal channel y positions through gaps between stacked class rows."""
        if not placements:
            return [START_Y - ROUTE_CLEARANCE]
        bands = sorted({(int(round(geo[1])), int(round(geo[1] + geo[3]))) for geo in placements.values()})
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

    def _nearest(self, values: List[float], target: float) -> float:
        return min(values, key=lambda v: abs(v - target))

    def _ownership_kinds(self, kind: str) -> bool:
        return (kind or '').lower() in {'composition', 'aggregation'}

    def _infer_clusters(self, ids) -> List[List[str]]:
        """Group classes by module/BC when available; else by composition aggregates.

    Nested owners (a composed class that itself composes others) become their
    own cluster so related lines stay local and foreign lines stay in the gaps.
    """
        named = self._clusters_from_named_modules(ids)
        if named is not None:
            return named
        return self._clusters_from_ownership(ids)

    def _clusters_from_named_modules(self, ids) -> Optional[List[List[str]]]:
        id_set = set(ids)
        named_modules = [m for m in self._modules or [] if m.name and m.name.strip() and m.classes]
        if len(named_modules) < 2:
            return None
        clusters: List[List[str]] = []
        seen: set[str] = set()
        for module in named_modules:
            members = [self._slug(c.name) for c in module.classes if self._slug(c.name) in id_set]
            members = [m for m in members if m not in seen]
            if members:
                clusters.append(members)
                seen.update(members)
        leftovers = sorted((cid for cid in ids if cid not in seen))
        if leftovers:
            clusters.append(leftovers)
        return clusters

    def _ownership_parent_maps(self):
        from collections import defaultdict
        children: Dict[str, List[str]] = defaultdict(list)
        parents: Dict[str, str] = {}
        for src, tgt, kind in self._relationships:
            if src == tgt or not self._ownership_kinds(kind):
                continue
            children[src].append(tgt)
            parents.setdefault(tgt, src)
        return (children, parents)

    def _clusters_from_ownership(self, ids) -> List[List[str]]:
        children, parents = self._ownership_parent_maps()
        self._cluster_ids = ids
        self._cluster_children = children
        self._cluster_parents = parents
        self._cluster_assigned: set[str] = set()
        self._member_clusters: List[List[str]] = []
        self._collect_nested_root_clusters()
        self._collect_top_root_clusters()
        leftovers = sorted((cid for cid in ids if cid not in self._cluster_assigned))
        self._attach_associated_orphans(leftovers)
        return self._member_clusters

    def _collect_nested_root_clusters(self) -> None:
        ids = self._cluster_ids
        children = self._cluster_children
        parents = self._cluster_parents
        nested_roots = sorted((cid for cid in ids if children.get(cid) and cid in parents))
        for root in nested_roots:
            if root in self._cluster_assigned:
                continue
            self._member_clusters.append(self._nested_root_members(root))

    def _nested_root_members(self, root) -> List[str]:
        children = self._cluster_children
        parents = self._cluster_parents
        assigned = self._cluster_assigned
        members = [root]
        assigned.add(root)
        for child in sorted(children.get(root, ())):
            if child in assigned:
                continue
            if children.get(child) and child in parents and (child != root):
                continue
            members.append(child)
            assigned.add(child)
        return members

    def _collect_top_root_clusters(self) -> None:
        ids = self._cluster_ids
        children = self._cluster_children
        parents = self._cluster_parents
        nested_roots = set((cid for cid in ids if children.get(cid) and cid in parents))
        self._nested_cluster_roots = nested_roots
        top_roots = sorted((cid for cid in ids if children.get(cid) and cid not in parents))
        for root in top_roots:
            if root in self._cluster_assigned:
                continue
            self._member_clusters.append(self._top_root_members(root))

    def _top_root_members(self, root) -> List[str]:
        children = self._cluster_children
        nested_roots = self._nested_cluster_roots
        assigned = self._cluster_assigned
        members = [root]
        assigned.add(root)
        for child in sorted(children.get(root, ())):
            if child in assigned or child in nested_roots:
                continue
            members.append(child)
            assigned.add(child)
        return members

    def _attach_associated_orphans(self, leftovers) -> None:
        clusters = self._member_clusters
        self._cluster_of_tmp = {cid: index for index, members in enumerate(clusters) for cid in members}
        still_orphan: List[str] = []
        for cid in leftovers:
            if self._attach_orphan_if_unique(cid):
                continue
            still_orphan.append(cid)
        for cid in still_orphan:
            clusters.append([cid])

    def _attach_orphan_if_unique(self, cid) -> bool:
        clusters = self._member_clusters
        cluster_of_tmp = self._cluster_of_tmp
        assigned = self._cluster_assigned
        assoc_targets = [tgt for src, tgt, kind in self._relationships if src == cid and (not self._ownership_kinds(kind)) and (tgt in cluster_of_tmp)]
        assoc_targets += [src for src, tgt, kind in self._relationships if tgt == cid and (not self._ownership_kinds(kind)) and (src in cluster_of_tmp)]
        target_clusters = {cluster_of_tmp[t] for t in assoc_targets}
        if len(target_clusters) != 1:
            return False
        clusters[next(iter(target_clusters))].append(cid)
        assigned.add(cid)
        return True

    def _pack_cluster(self, members) -> Tuple[Dict[str, Tuple[float, float, float, float]], float, float]:
        id_to_oclass = self._id_to_oclass
        origin_x = self._origin_x
        origin_y = self._origin_y
        relationships = self._relationships
        cols = self._pack_cols
        if cols is None:
            cols = INNER_COLS
        if not members:
            return ({}, 0.0, 0.0)
        member_set = set(members)
        col_count = max(1, cols)
        from collections import defaultdict
        composition: Dict[str, List[str]] = defaultdict(list)
        aggregation: Dict[str, List[str]] = defaultdict(list)
        for src, tgt, kind in relationships:
            if src not in member_set or tgt not in member_set or src == tgt:
                continue
            k = (kind or '').lower()
            if k == 'composition':
                composition[src].append(tgt)
            elif k == 'aggregation' and 'repository' not in src:
                aggregation[src].append(tgt)
        owned = {c for kids in composition.values() for c in kids}
        owned |= {c for kids in aggregation.values() for c in kids}

        def _is_repo(cid: str) -> bool:
            return 'repository' in cid
        roots = [m for m in members if m not in owned and (composition.get(m) or aggregation.get(m))]
        if not roots:
            roots = [m for m in members if m not in owned and (not _is_repo(m))] or list(members)

        def _root_score(cid: str) -> Tuple[int, int, str]:
            return (-(len(composition.get(cid, ())) + len(aggregation.get(cid, ()))), 0 if 'aggregate' in cid or 'entity' in cid else 1, cid)
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
                h = float(self.load_class(id_to_oclass[cid]).height())
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
            oh = float(self.load_class(id_to_oclass[owner]).height())
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
                repo_x = origin_x + CELL_WIDTH + INNER_COL_GAP
                bottom = y + oh
                for src, tgt, kind in relationships:
                    if tgt != owner or src in placed or src not in member_set:
                        continue
                    if (kind or '').lower() != 'aggregation' or 'repository' not in src:
                        continue
                    rh = float(self.load_class(id_to_oclass[src]).height())
                    placements[src] = (repo_x, y, float(CELL_WIDTH), rh)
                    placed.add(src)
                    max_x = max(max_x, repo_x + CELL_WIDTH)
                    bottom = max(bottom, y + rh)
                    repo_x += CELL_WIDTH + INNER_COL_GAP
                return bottom
            repo_x = origin_x + CELL_WIDTH + INNER_COL_GAP
            bottom = y + oh
            for src, tgt, kind in relationships:
                if tgt != owner or src in placed or src not in member_set:
                    continue
                if (kind or '').lower() != 'aggregation' or 'repository' not in src:
                    continue
                rh = float(self.load_class(id_to_oclass[src]).height())
                placements[src] = (repo_x, y, float(CELL_WIDTH), rh)
                placed.add(src)
                max_x = max(max_x, repo_x + CELL_WIDTH)
                bottom = max(bottom, y + rh)
                repo_x += CELL_WIDTH + INNER_COL_GAP
            nested = [k for k in uniq_kids if composition.get(k) or aggregation.get(k)]
            leaves = [k for k in uniq_kids if k not in nested]
            side_kids = list(leaves)
            deep_nested = list(nested)
            if nested and (not leaves):
                side_kids = [nested[0]]
                deep_nested = nested[1:]
            if side_kids:
                x = repo_x
                row_y = y
                row_h = oh
                col = int(round((x - origin_x) / (CELL_WIDTH + INNER_COL_GAP)))
                leaf_cols = min(2, col_count)
                for kid in side_kids:
                    if kid in placed:
                        continue
                    if kid in nested:
                        nest_bottom = _place_owner_tree_at(kid, (x, row_y))
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
                    kh = float(self.load_class(id_to_oclass[kid]).height())
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

        def _place_owner_tree_at(owner, origin) -> float:
            x, y = origin
            'Place an owner tree rooted at (x, y); returns bottom y.'
            nonlocal max_x
            if owner in placed:
                return y
            oh = float(self.load_class(id_to_oclass[owner]).height())
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
                kh = float(self.load_class(id_to_oclass[kid]).height())
                placements[kid] = (cx, y, float(CELL_WIDTH), kh)
                placed.add(kid)
                max_x = max(max_x, cx + CELL_WIDTH)
                bottom = max(bottom, y + kh)
                cx += CELL_WIDTH + INNER_COL_GAP
            ny = bottom + INNER_ROW_GAP
            for nest in nested:
                ny = _place_owner_tree_at(nest, (x, ny)) + INNER_ROW_GAP
            return max(bottom, ny - INNER_ROW_GAP)
        for root in roots:
            if root in placed:
                continue
            cursor_y = _place_owner_tree(root, cursor_y) + INNER_ROW_GAP
        for src, tgt, kind in relationships:
            if (kind or '').lower() != 'aggregation':
                continue
            if 'repository' not in src:
                continue
            if src not in member_set or src in placed or tgt not in placements:
                continue
            tx, ty, _tw, _th = placements[tgt]
            rh = float(self.load_class(id_to_oclass[src]).height())
            rx = tx + CELL_WIDTH + INNER_COL_GAP
            candidate = (rx, ty, float(CELL_WIDTH), rh)
            guard = 0
            while any((self._rects_overlap(candidate, geo) for oid, geo in placements.items())) and guard < 8:
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
                    if self._ownership_kinds(kind) and 'repository' not in src:
                        continue
                    if src == cid and tgt in placed or (tgt == cid and src in placed):
                        links += 1
                if links > best_score:
                    best_score = links
                    best_i = i
            batch = [leftovers.pop(best_i)]
            for cid in list(leftovers):
                if len(batch) >= col_count:
                    break
                linked = any((src == cid and tgt in placed or (tgt == cid and src in placed) or (src == cid and tgt in batch) or (tgt == cid and src in batch) for src, tgt, kind in relationships if not self._ownership_kinds(kind) or 'repository' in src))
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
        return (placements, width, height)

    def _layout_classes_clustered(self, id_to_oclass) -> Dict[str, Tuple[float, float, float, float]]:
        """Place same-module / same-aggregate classes in tight islands.

    Distinct modules (or composition aggregates when modules are flat) sit
    farther apart so intra-context edges stay short and inter-context edges
    run in the gaps instead of tangling through unrelated boxes.
    """
        self._id_to_oclass = id_to_oclass
        reused = self._reuse_previous_if_clear()
        if reused is not None:
            return reused
        ids = list(id_to_oclass.keys())
        clusters = self._infer_clusters(ids)
        named_module_count = sum((1 for m in self._modules or [] if m.name and m.name.strip() and m.classes))
        if named_module_count >= 2:
            return self._layout_module_driven_clusters(clusters)
        return self._layout_ownership_clusters(clusters)

    def _reuse_previous_if_clear(self):
        previous_positions = self._previous_positions
        if not previous_positions:
            return None
        trial: Dict[str, Tuple[float, float, float, float]] = {}
        for cid in self._id_to_oclass:
            if cid not in previous_positions:
                return None
            x, y = previous_positions[cid]
            h = float(self.load_class(self._id_to_oclass[cid]).height())
            trial[cid] = (x, y, float(CELL_WIDTH), h)
        if self._trial_has_overlap(trial):
            return None
        return trial

    def _trial_has_overlap(self, trial) -> bool:
        cid_list = list(trial.keys())
        for i, a in enumerate(cid_list):
            for b in cid_list[i + 1:]:
                if self._rects_overlap(trial[a], trial[b]):
                    return True
        return False

    def _layout_module_driven_clusters(self, clusters) -> Dict[str, Tuple[float, float, float, float]]:
        placements: Dict[str, Tuple[float, float, float, float]] = {}
        cursor_y = float(START_Y)
        self._pack_cols = INNER_COLS
        for members in clusters:
            self._origin_x = float(START_X)
            self._origin_y = cursor_y
            local, _width, height = self._pack_cluster(members)
            placements.update(local)
            cursor_y += height + CLUSTER_GAP_Y
        return placements

    def _layout_ownership_clusters(self, clusters) -> Dict[str, Tuple[float, float, float, float]]:
        child_clusters, parent_of_cluster = self._ownership_cluster_tree(clusters)
        roots = [i for i in range(len(clusters)) if i not in parent_of_cluster]
        roots.sort(key=lambda i: (-len(clusters[i]), i))
        parent_roots = [i for i in roots if child_clusters[i] or len(clusters[i]) > 1]
        leaf_orphans = [i for i in roots if i not in parent_roots]
        self._placements = {}
        self._cluster_members = clusters
        self._parent_roots = parent_roots
        self._child_clusters_by_root = child_clusters
        self._cursor_y = float(START_Y)
        cursor_y = self._place_parent_root_clusters()
        self._place_leaf_orphan_clusters(leaf_orphans, cursor_y)
        return self._placements

    def _ownership_cluster_tree(self, clusters):
        cluster_of = {cid: index for index, members in enumerate(clusters) for cid in members}
        child_clusters: Dict[int, List[int]] = {i: [] for i in range(len(clusters))}
        parent_of_cluster: Dict[int, int] = {}
        for src, tgt, kind in self._relationships:
            if not self._ownership_kinds(kind):
                continue
            if src not in cluster_of or tgt not in cluster_of:
                continue
            ps, pt = (cluster_of[src], cluster_of[tgt])
            if ps == pt:
                continue
            if pt not in child_clusters[ps]:
                child_clusters[ps].append(pt)
            parent_of_cluster.setdefault(pt, ps)
        return (child_clusters, parent_of_cluster)

    def _place_cluster_at(self, index) -> Tuple[float, float]:
        self._pack_cols = INNER_COLS
        local, width, height = self._pack_cluster(self._cluster_members[index])
        self._placements.update(local)
        return (width, height)

    def _place_parent_root_clusters(self) -> float:
        clusters = self._cluster_members
        cursor_y = self._cursor_y
        for root_i in self._parent_roots:
            children = sorted(self._child_clusters_by_root[root_i])
            child_packs = self._measure_child_cluster_packs(children)
            approx_children_width = sum((cw for _i, cw, _ch in child_packs))
            if children:
                approx_children_width += CLUSTER_GAP_X * (len(children) - 1)
            root_w_est = min(INNER_COLS, len(clusters[root_i])) * CELL_WIDTH
            band_width = max(root_w_est, approx_children_width)
            self._origin_x = float(START_X + max(0.0, (band_width - root_w_est) / 2.0))
            self._origin_y = cursor_y
            _root_w, root_h = self._place_cluster_at(root_i)
            cursor_y = self._place_child_cluster_row(child_packs, cursor_y, root_h, band_width, approx_children_width)
        return cursor_y

    def _measure_child_cluster_packs(self, children):
        child_packs = []
        saved_x, saved_y = (self._origin_x, self._origin_y)
        for child_i in children:
            self._origin_x = 0.0
            self._origin_y = 0.0
            self._pack_cols = INNER_COLS
            _local, cw, ch = self._pack_cluster(self._cluster_members[child_i])
            child_packs.append((child_i, cw, ch))
        self._origin_x, self._origin_y = (saved_x, saved_y)
        return child_packs

    def _place_child_cluster_row(self, child_packs, cursor_y, root_h, band_width, approx_children_width) -> float:
        child_y = cursor_y + root_h + CLUSTER_GAP_Y
        child_x = float(START_X + max(0.0, (band_width - approx_children_width) / 2.0))
        child_row_h = 0.0
        for child_i, cw, _ch in child_packs:
            self._origin_x = child_x
            self._origin_y = child_y
            _cw, ch2 = self._place_cluster_at(child_i)
            child_x += cw + CLUSTER_GAP_X
            child_row_h = max(child_row_h, ch2)
        return child_y + child_row_h + CLUSTER_GAP_Y

    def _place_leaf_orphan_clusters(self, leaf_orphans, cursor_y) -> None:
        if not leaf_orphans:
            return
        orphan_x = float(START_X)
        orphan_y = cursor_y + CLUSTER_GAP_Y * 0.5
        row_h = 0.0
        for orphan_i in leaf_orphans:
            self._origin_x = orphan_x
            self._origin_y = orphan_y
            ow, oh = self._place_cluster_at(orphan_i)
            orphan_x += ow + CLUSTER_GAP_X
            row_h = max(row_h, oh)
            if orphan_x > START_X + 3 * (CELL_WIDTH + CLUSTER_GAP_X):
                orphan_x = float(START_X)
                orphan_y += row_h + CLUSTER_GAP_Y
                row_h = 0.0

    def _segments_from_route(self, src) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        self._anchor_frac = self._exit_frac
        p1 = self._point_on_side(src, self._exit_side)
        self._anchor_frac = self._entry_frac
        p2 = self._point_on_side(self._route_tgt, self._entry_side)
        points = self._dedupe_points([p1, *self._route_trial_points, p2])
        return [(points[i], points[i + 1]) for i in range(len(points) - 1)]

    def _segment_pair_conflicts(self, segs_a: List[Tuple[Tuple[float, float], Tuple[float, float]]], segs_b: List[Tuple[Tuple[float, float], Tuple[float, float]]]) -> bool:
        self._proximity = 10
        self._endpoint_tol = 2.0
        for sa in segs_a:
            for sb in segs_b:
                if self._edge_segments_overlap(sa, sb):
                    return True
                crossed, _pt = self._orthogonal_segments_cross(sa, sb)
                if crossed:
                    return True
        return False

    def _segments_overlap_1d(self, first, second) -> bool:
        a_start, a_end = first
        b_start, b_end = second
        threshold = 8
        lo_a, hi_a = min(a_start, a_end), max(a_start, a_end)
        lo_b, hi_b = min(b_start, b_end), max(b_start, b_end)
        return min(hi_a, hi_b) - max(lo_a, lo_b) > threshold

    def _edge_segments_overlap(self, seg_a, seg_b) -> bool:
        (ax1, ay1), (ax2, ay2) = seg_a
        (bx1, by1), (bx2, by2) = seg_b
        proximity = self._proximity
        a_horiz = abs(ay2 - ay1) < 2
        a_vert = abs(ax2 - ax1) < 2
        b_horiz = abs(by2 - by1) < 2
        b_vert = abs(bx2 - bx1) < 2
        if a_horiz and b_horiz and abs(ay1 - by1) < proximity:
            if self._segments_overlap_1d((ax1, ax2), (bx1, bx2)):
                return True
        if a_vert and b_vert and abs(ax1 - bx1) < proximity:
            if self._segments_overlap_1d((ay1, ay2), (by1, by2)):
                return True
        return False

    def _orthogonal_segments_cross(self, seg_a, seg_b) -> Tuple[bool, Optional[Tuple[float, float]]]:
        (ax1, ay1), (ax2, ay2) = seg_a
        (bx1, by1), (bx2, by2) = seg_b
        endpoint_tol = self._endpoint_tol
        a_horiz = abs(ay2 - ay1) < 2
        a_vert = abs(ax2 - ax1) < 2
        b_horiz = abs(by2 - by1) < 2
        b_vert = abs(bx2 - bx1) < 2
        if a_horiz and b_vert:
            y = (ay1 + ay2) / 2
            x = (bx1 + bx2) / 2
            a_lo_x, a_hi_x = sorted((ax1, ax2))
            b_lo_y, b_hi_y = sorted((by1, by2))
            if a_lo_x + endpoint_tol < x < a_hi_x - endpoint_tol and b_lo_y + endpoint_tol < y < b_hi_y - endpoint_tol:
                return (True, (x, y))
        if a_vert and b_horiz:
            x = (ax1 + ax2) / 2
            y = (by1 + by2) / 2
            a_lo_y, a_hi_y = sorted((ay1, ay2))
            b_lo_x, b_hi_x = sorted((bx1, bx2))
            if a_lo_y + endpoint_tol < y < a_hi_y - endpoint_tol and b_lo_x + endpoint_tol < x < b_hi_x - endpoint_tol:
                return (True, (x, y))
        return (False, None)

    def _capped_outward_point(self, geo, side) -> Tuple[float, float]:
        """Outward point that stays inside the nearest open highway band."""
        ax, ay = self._point_on_side(geo, side)
        x, y, w, h = geo
        clearance = self._clearance
        highways = self._highways
        if side == 'bottom':
            band = min((hy for hy in highways if hy >= y + h), default=y + h + clearance)
            return (ax, min(ay + clearance, band))
        if side == 'top':
            band = max((hy for hy in highways if hy <= y), default=y - clearance)
            return (ax, max(ay - clearance, band))
        if side == 'left':
            return (ax - clearance, ay)
        return (ax + clearance, ay)

    def _route_waypoints(self, src) -> List[Tuple[float, float]]:
        """Orthogonal channel router: prefer no/few waypoints; highway only if needed."""
        self._route_src = src
        self._bind_route_geometry()
        simple = self._try_simple_routes()
        if simple is not None:
            return simple
        return self._route_channel_search()

    def _bind_route_geometry(self) -> None:
        src = self._route_src
        tgt = self._route_tgt
        self._avoid_segments = self._avoid_segments or []
        placements = self._all_placements or {str(i): geo for i, geo in enumerate([src, tgt, *self._obstacles])}
        self._all_placements = placements
        self._route_gutters = self._column_gutters(placements)
        self._route_lane_i = int(round(self._route_lane / ROUTE_LANE_STEP)) if ROUTE_LANE_STEP else 0
        self._clearance = max(12.0, min(ROUTE_CLEARANCE, ROW_GAP * 0.35))
        self._highways = self._row_highways(placements)
        self._anchor_frac = self._exit_frac
        self._route_leave = self._capped_outward_point(src, self._exit_side)
        self._anchor_frac = self._entry_frac
        self._route_approach = self._capped_outward_point(tgt, self._entry_side)
        self._route_lane_sep = 12.0
        self._anchor_frac = self._exit_frac
        self._route_exit_pt = self._point_on_side(src, self._exit_side)
        self._anchor_frac = self._entry_frac
        self._route_entry_pt = self._point_on_side(tgt, self._entry_side)

    def _route_is_clear(self, pts) -> bool:
        self._hit_margin = 3.0
        if self._polyline_hits_obstacle(pts):
            return False
        self._route_trial_points = pts
        segs = self._segments_from_route(self._route_src)
        points = [segs[0][0], *[p for seg in segs for p in seg[1:]]]
        if self._polyline_hits_obstacle(points):
            return False
        if self._route_check_edges and any((self._segment_pair_conflicts(segs, prior) for prior in self._avoid_segments)):
            return False
        return True

    def _try_simple_routes(self):
        self._route_check_edges = True
        found = self._simple_route_variants()
        if found is not None:
            return found
        src, tgt = (self._route_src, self._route_tgt)
        scx, scy = (src[0] + src[2] / 2.0, src[1] + src[3] / 2.0)
        tcx, tcy = (tgt[0] + tgt[2] / 2.0, tgt[1] + tgt[3] / 2.0)
        if abs(scx - tcx) + abs(scy - tcy) >= 420:
            return None
        self._route_check_edges = False
        return self._simple_route_variants()

    def _simple_route_variants(self):
        if self._route_is_clear([]):
            return []
        leave, approach = (self._route_leave, self._route_approach)
        exit_pt = self._route_exit_pt
        if {self._exit_side, self._entry_side} <= {'top', 'bottom'}:
            mid = [(exit_pt[0], (leave[1] + approach[1]) / 2.0)]
            if self._route_is_clear(mid):
                return mid
        if {self._exit_side, self._entry_side} <= {'left', 'right'}:
            mid = [((leave[0] + approach[0]) / 2.0, exit_pt[1])]
            if self._route_is_clear(mid):
                return mid
        elbow = [leave, approach]
        if self._route_is_clear(elbow):
            return elbow
        return None

    def _occupied_horiz_ys(self) -> List[float]:
        ys: List[float] = []
        for segs in self._avoid_segments:
            for a, b in segs:
                if abs(a[1] - b[1]) < 2.0 and abs(a[0] - b[0]) > 12.0:
                    ys.append((a[1] + b[1]) / 2.0)
        return ys

    def _sorted_free_ys(self, cands: List[float]) -> List[float]:
        occupied = self._occupied_horiz_ys()
        lane_sep = self._route_lane_sep
        uniq: List[float] = []
        for y in cands:
            if all((abs(y - e) >= 1.0 for e in uniq)):
                uniq.append(y)

        def _score(y: float) -> Tuple[float, float]:
            if not occupied:
                return (0.0, abs(y - cands[0]))
            dist = min((abs(y - o) for o in occupied))
            penalty = 0.0 if dist >= lane_sep else lane_sep - dist
            return (penalty, -dist)
        return sorted(uniq, key=_score)

    def _fan_y(self, base) -> List[float]:
        outward = self._fan_outward
        count = self._fan_count
        lane_i = self._route_lane_i
        lane_sep = self._route_lane_sep
        order = [lane_i] + [i for i in range(count) if i != lane_i]
        vals: List[float] = []
        for step in order:
            y = base + outward * float(step) * lane_sep
            if outward > 0 and y < base - 0.5:
                continue
            if outward < 0 and y > base + 0.5:
                continue
            if all((abs(y - e) >= lane_sep - 0.5 for e in vals)):
                vals.append(y)
        return vals or [base]

    def _route_channels(self, extra: float=0.0) -> List[float]:
        src, tgt = (self._route_src, self._route_tgt)
        gutters = self._route_gutters
        lane_i = self._route_lane_i
        xs = [gx + (lane_i - 2) * 8 for gx in gutters]
        near_left = src[0] - 16.0 - extra
        near_right = src[0] + src[2] + 16.0 + extra
        far_left = [gutters[0] - 40 - lane_i * 10 - extra, gutters[0] - 80 - lane_i * 14 - extra, gutters[0] - 140 - lane_i * 18 - extra]
        far_right = [gutters[-1] + 40 + lane_i * 10 + extra, gutters[-1] + 80 + lane_i * 14 + extra, gutters[-1] + 140 + lane_i * 18 + extra]
        return self._channel_order(extra, xs, near_left, near_right, far_left, far_right)

    def _channel_order(self, extra, xs, near_left, near_right, far_left, far_right):
        src, tgt = (self._route_src, self._route_tgt)
        span_top = min(src[1], tgt[1])
        span_bot = max(src[1] + src[3], tgt[1] + tgt[3])
        intervening = [geo for geo in self._all_placements.values() if geo != src and geo != tgt and (geo[1] < span_bot) and (geo[1] + geo[3] > span_top)]
        if intervening:
            band_lo = min((g[0] for g in intervening)) - 20.0 - extra
            band_hi = max((g[0] + g[2] for g in intervening)) + 20.0 + extra
            if self._route_exit_pt[0] >= src[0] + src[2] * 0.5:
                outside = [band_hi, band_hi + 40.0, band_lo, band_lo - 40.0]
            else:
                outside = [band_lo, band_lo - 40.0, band_hi, band_hi + 40.0]
            return outside + far_right + far_left + [near_right, near_left] + xs
        if self._route_entry_pt[0] >= self._route_exit_pt[0]:
            return far_right + [near_right] + xs + [near_left] + far_left
        return far_left + [near_left] + xs + [near_right] + far_right

    def _route_candidates(self, extra: float=0.0):
        if self._exit_side in ('left', 'right') or self._entry_side in ('left', 'right'):
            return self._side_route_candidates(extra)
        return self._vertical_route_candidates(extra)

    def _side_route_candidates(self, extra: float):
        leave, approach = (self._route_leave, self._route_approach)
        channels = self._route_channels(extra)
        self._fan_outward = 1.0
        self._fan_count = 6
        y_vals = self._sorted_free_ys(self._fan_y(leave[1]) + [leave[1] - (i + 1) * self._route_lane_sep for i in range(5)])
        paths: List[List[Tuple[float, float]]] = []
        for y in y_vals[:8]:
            for cx in channels[:8]:
                paths.append([leave, (leave[0], y), (cx, y), (approach[0], y), approach])
                paths.append([leave, (cx, leave[1]), (cx, y), (approach[0], y), approach])
        paths.append([leave, (approach[0], leave[1]), approach])
        paths.append([leave, approach])
        return paths

    def _vertical_route_candidates(self, extra: float):
        channels = self._route_channels(extra)
        exit_pt, entry_pt = (self._route_exit_pt, self._route_entry_pt)
        out_exit = 1.0 if self._exit_side == 'bottom' else -1.0
        out_entry = -1.0 if self._entry_side == 'top' else 1.0
        stub_y = exit_pt[1] + out_exit * 10.0
        src_ys, tgt_ys = self._vertical_route_ys(stub_y, out_exit, out_entry)
        return self._vertical_route_paths(channels, stub_y, src_ys, tgt_ys)

    def _vertical_route_ys(self, stub_y, out_exit, out_entry):
        exit_pt, entry_pt = (self._route_exit_pt, self._route_entry_pt)
        self._fan_outward = out_exit
        self._fan_count = 6
        src_ys = self._sorted_free_ys(self._fan_y(stub_y))
        self._fan_outward = out_entry
        tgt_ys = self._sorted_free_ys(self._fan_y(entry_pt[1] + out_entry * 10.0))
        tgt_ys = [y for y in tgt_ys if (self._entry_side != 'top' or y <= entry_pt[1]) and (self._entry_side != 'bottom' or y >= entry_pt[1])] or [entry_pt[1] + out_entry * 10.0]
        if self._exit_side == 'bottom' and self._entry_side == 'top':
            src_ys, tgt_ys = self._clip_gap_ys(src_ys, tgt_ys)
        src_ys = [y for y in src_ys if (self._exit_side != 'bottom' or y >= exit_pt[1]) and (self._exit_side != 'top' or y <= exit_pt[1])] or [stub_y]
        return (src_ys, tgt_ys)

    def _clip_gap_ys(self, src_ys, tgt_ys):
        gap_lo = self._route_exit_pt[1] + 10.0
        gap_hi = self._route_entry_pt[1] - 10.0
        in_gap = [y for y in tgt_ys if gap_lo - 0.5 <= y <= gap_hi + 0.5]
        if in_gap:
            tgt_ys = in_gap
        src_in_gap = [y for y in src_ys if gap_lo - 0.5 <= y <= gap_hi + 0.5]
        if src_in_gap:
            src_ys = src_in_gap
        return (src_ys, tgt_ys)

    def _vertical_route_paths(self, channels, stub_y, src_ys, tgt_ys):
        exit_pt, entry_pt = (self._route_exit_pt, self._route_entry_pt)
        channel_paths: List[List[Tuple[float, float]]] = []
        gap_paths: List[List[Tuple[float, float]]] = []
        for tgt_hw in tgt_ys:
            for cx in channels[:8]:
                channel_paths.append([(exit_pt[0], stub_y), (cx, stub_y), (cx, tgt_hw), (entry_pt[0], tgt_hw)])
            for src_hw in src_ys[:4]:
                for cx in channels[:6]:
                    channel_paths.append([(exit_pt[0], src_hw), (cx, src_hw), (cx, tgt_hw), (entry_pt[0], tgt_hw)])
        for src_hw in src_ys[:6]:
            gap_paths.append([(exit_pt[0], src_hw), (entry_pt[0], src_hw)])
            for tgt_hw in tgt_ys[:4]:
                if abs(tgt_hw - src_hw) >= self._route_lane_sep * 0.5:
                    gap_paths.append([(exit_pt[0], src_hw), (entry_pt[0], src_hw), (entry_pt[0], tgt_hw)])
        if self._avoid_segments:
            return channel_paths + gap_paths
        return gap_paths + channel_paths

    def _search_route(self, extra: float):
        for path in self._route_candidates(extra):
            pts = self._dedupe_points(path)
            if pts and self._route_is_clear(pts):
                return pts
        return None

    def _route_channel_search(self):
        self._route_check_edges = True
        found = self._search_route(0.0)
        if found is not None:
            return found
        if not self._avoid_segments:
            self._route_check_edges = False
            found = self._search_route(0.0)
            if found is not None:
                return found
        else:
            for extra in (40.0, 100.0, 180.0, 280.0):
                found = self._search_route(extra)
                if found is not None:
                    return found
        best = self._best_conflict_route()
        if best is not None:
            return best
        return self._fallback_channel_path()

    def _best_conflict_route(self):
        best = None
        best_conflicts = 10 ** 9
        self._route_check_edges = False
        for path in self._route_candidates(280.0):
            pts = self._dedupe_points(path)
            if not pts or not self._route_is_clear(pts):
                continue
            self._route_trial_points = pts
            segs = self._segments_from_route(self._route_src)
            conflicts = sum((1 for prior in self._avoid_segments if self._segment_pair_conflicts(segs, prior)))
            if conflicts < best_conflicts:
                best = pts
                best_conflicts = conflicts
                if conflicts == 0:
                    return pts
        return best

    def _fallback_channel_path(self):
        exit_pt, entry_pt = (self._route_exit_pt, self._route_entry_pt)
        out_exit = 1.0 if self._exit_side == 'bottom' else -1.0
        out_entry = -1.0 if self._entry_side == 'top' else 1.0
        ox = self._route_channels(280.0)[0]
        return self._dedupe_points([(exit_pt[0], exit_pt[1] + out_exit * 10.0), (ox, exit_pt[1] + out_exit * 10.0), (ox, entry_pt[1] + out_entry * 10.0), (entry_pt[0], entry_pt[1] + out_entry * 10.0)])

    def _parse_class_html(self, value: str) -> Tuple[Optional[str], List[Property], List[Operation]]:
        text = html.unescape(value)
        if ('\u2022' in text or '-' in text) and 'hr size="1"' not in text.lower() and ('<hr size=' not in text.lower()):
            if re.search('<i[^>]*>', text, re.IGNORECASE):
                return (None, [], [])
        m = re.search('<b[^>]*>([^<]+)</b>', text)
        name = m.group(1).strip() if m else None
        if not name:
            return (None, [], [])
        sections = re.split('<hr\\s+size="1"\\s*/?>', text, flags=re.IGNORECASE)
        props: List[Property] = []
        ops: List[Operation] = []

        def _items(sec: str) -> List[str]:
            return [line.strip() for line in re.findall('[+\\-]\\s*([^<]+)', sec) if line.strip()]
        if len(sections) >= 3:
            for raw in _items(sections[1]):
                if ':' in raw:
                    n, t = raw.split(':', 1)
                    props.append(Property(name=n.strip(), type_hint=t.strip()))
                else:
                    props.append(Property(name=raw))
            for raw in _items(sections[2]):
                m2 = re.match('(_?\\w+)\\(([^)]*)\\)(?::\\s*(.+))?', raw)
                if m2:
                    params = [p.strip() for p in m2.group(2).split(',') if p.strip()]
                    ops.append(Operation(name=m2.group(1), parameters=params, return_type=(m2.group(3) or '').strip()))
        return (name, props, ops)

    def _classify_edge(self, style: str) -> str:
        if 'endFill=0' in style and 'endArrow=block' in style:
            return 'inheritance'
        if 'startFill=1' in style and 'diamondThin' in style:
            return 'composition'
        if 'startFill=0' in style and 'diamondThin' in style:
            return 'aggregation'
        return 'association'

class _ContainmentLayout:

    def __init__(self) -> None:
        self.bounds: Dict[str, Tuple[float, float, float, float]] = {}
        self.parent_id: Dict[str, str] = {}
        self.name_to_id: Dict[str, str] = {}
        self.render_order: List[str] = []
