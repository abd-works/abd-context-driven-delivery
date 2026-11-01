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
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple
_repo = Path(__file__).resolve().parents[5]
if str(_repo) not in sys.path:
    sys.path.insert(0, str(_repo))
from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass, Operation, Property, Relationship
from cdd_guidance.practices.clean_engineering.model.diagram.diagram_node import (
    ContainmentForest,
    DiagramClass,
    DiagramCleanEngineeringModel,
    is_modules_view,
    module_tab_label,
    path_parent,
)
from cdd_guidance.practices.clean_engineering.model.diagram.class_layout import (
    GROUP_FILL_COLORS,
    SMALLEST_PORT_SPACING,
    ArrowRouter,
    CardPlacement,
    DiagramArrow,
    DiagramCard,
)
from cdd_guidance.practices.clean_engineering.model.diagram.geometry import CELL_WIDTH, Geometry, MODULE_CELL_MIN_HEIGHT, MODULE_CELL_WIDTH
from cdd_guidance.practices.clean_engineering.model.drawio.diagram_node import (
    DrawIOClass,
    DrawIOModule,
    ImportedClass,
    MODULE_CHILD_STYLE,
    MODULE_STYLE,
    Page,
)
from cdd_guidance.practices.clean_engineering.model.update_report import UpdateReport
_EDGE_BASE_STYLE = 'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;fontSize=10;labelBackgroundColor=#ffffff;'
EDGE_STYLES = {'inheritance': f'{_EDGE_BASE_STYLE}endArrow=block;endSize=16;endFill=0;', 'composition': f'{_EDGE_BASE_STYLE}startArrow=diamondThin;startFill=1;startSize=14;endArrow=open;endSize=12;', 'aggregation': f'{_EDGE_BASE_STYLE}startArrow=diamondThin;startFill=0;startSize=14;endArrow=open;endSize=12;', 'association': f'{_EDGE_BASE_STYLE}endArrow=open;endSize=12;', 'dependency': f'{_EDGE_BASE_STYLE}dashed=1;endArrow=open;endSize=12;'}
DEFAULT_EDGE_STYLE = EDGE_STYLES['association']
CLASSES_ON_ONE_PAGE = 40
PAGE_EDGE_ALLOWANCE = 200
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

class DrawIOCleanEngineeringModel(DiagramCleanEngineeringModel):

    def __init__(self, name: str='', sequential_order: int=1) -> None:
        super().__init__(name, sequential_order)
        self.previous = None
        self.keep_positioning = False
        self._page_width = '1654'
        self._page_height = '1169'
        self._id_to_oclass: Dict[str, OoadClass] = {}
        self._relationships: List[Tuple[str, str, str]] = []
        self._modules: List[Module] = []
        self._import_ids: List[str] = []
        self._page_ids: set = set()
        self._local_ids = None
        self._id_to_module: dict[str, str] = {}
        self._local_module_name = ''
        self._cell_id = ''
        self._cell_x = 0.0
        self._cell_y = 0.0
        self._cell_width = None
        self._cell_height = None
        self._cell_parent_id = '1'
        self._cell_style = ''
        self._edge_src_id = ''
        self._edge_tgt_id = ''
        self._edge_kind = ''
        self._edge_id = ''
        self._forest: Optional[ContainmentForest] = None
        self._layout: Optional[_ContainmentLayout] = None
        self._abs_x = 0.0
        self._abs_y = 0.0
        self._name_to_id: dict[str, str] = {}

    def load_module(self, source: Module) -> DrawIOModule:
        loaded = DrawIOModule(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        loaded.classes = list(source.classes)
        return loaded

    def load(self, text: str) -> "DrawIOCleanEngineeringModel":
        return self.parse(text)

    def save(self, canonical: CleanEngineeringModel | None = None) -> str:
        return self.render(canonical if canonical is not None else self)

    def clone(self) -> str:
        return super().clone().save()

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
        id_to_name: dict[str, str] = {}
        modules: Dict[str, DrawIOModule] = {}
        for cell in mxcells:
            if cell.get('vertex') != '1':
                continue
            value = cell.get('value', '')
            name, props, ops = self._parse_class_html(value)
            if not name:
                continue
            cell_id = cell.get('id', '')
            id_to_name[cell_id] = self._plain_class_name(name) or name
            if 'dashed=1' in cell.get('style', ''):
                continue
            oclass = DrawIOClass(name=name, sequential_order=order, properties=props, operations=ops)
            module_name = self._style_module(cell.get('style', ''))
            module = modules.setdefault(module_name, DrawIOModule(name=module_name, sequential_order=len(modules) + 1))
            module.classes.append(oclass)
            id_to_class[cell_id] = oclass
            order += 1
        model.modules.extend(modules.values())
        for cell in mxcells:
            if cell.get('edge') != '1':
                continue
            src_id = cell.get('source', '')
            tgt_id = cell.get('target', '')
            src_cls = id_to_class.get(src_id)
            if src_cls is None:
                continue
            tgt_cls = id_to_class.get(tgt_id)
            tgt_name = tgt_cls.name if tgt_cls else id_to_name.get(tgt_id, tgt_id)
            kind = self._classify_edge(cell.get('style', ''))
            self._bind_edge_to_property(src_cls, tgt_name, kind)
        for oclass in id_to_class.values():
            self._bind_class_properties(oclass)
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

    def _style_module(self, style: str) -> str:
        found = re.search(r'(?:^|;)module=([^;]*)', style)
        return found.group(1) if found else ''

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
            self._bind_edge_to_property(src_cls, tgt_name, kind)
        for oclass in self._id_to_class.values():
            self._bind_class_properties(oclass)

    def _bind_class_properties(self, oclass: OoadClass) -> None:
        from cdd_guidance.practices.clean_engineering.model.property import bind_property_relationship

        for prop in oclass.properties:
            bind_property_relationship(prop)

    def _bind_edge_to_property(self, oclass: OoadClass, target: str, kind: str) -> None:
        """The arrow is the property whose type names the target. Kind lives on that property."""
        if (kind or "").lower() == "inheritance":
            return
        rank = {"composition": 3, "aggregation": 2, "association": 1}
        for prop in oclass.properties:
            names = re.findall(r"\b([A-Z][A-Za-z0-9]*)\b", prop.type_hint or "")
            if target not in names:
                continue
            current = (getattr(prop, "stereotype", "") or "").lower()
            if rank.get((kind or "").lower(), 0) >= rank.get(current, 0):
                prop.stereotype = (kind or "association").lower()
            from cdd_guidance.practices.clean_engineering.model.property import bind_property_relationship

            bind_property_relationship(prop)

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
        self._bind_class_ids(canonical)
        self._relationships = self._collect_relationships(canonical.classes)
        self._id_to_module = self._class_module_labels(canonical.modules)
        self._modules = canonical.modules
        named_modules = [m for m in canonical.modules if m.classes]
        self._module_fills = self._module_fill_colors(named_modules)
        if len(named_modules) < 2 or len(canonical.classes) <= CLASSES_ON_ONE_PAGE:
            return self._render_classes_single_page(canonical)
        return self._render_classes_multipage(named_modules)

    def _module_fill_colors(self, named_modules) -> Dict[str, str]:
        """One colour per module, so a reader sees where a class lives. One module needs no colour."""
        if len(named_modules) < 2:
            return {}
        return {
            self._module_tab_label(module.name): GROUP_FILL_COLORS[index % len(GROUP_FILL_COLORS)]
            for index, module in enumerate(named_modules)
        }

    def _bind_class_ids(self, canonical) -> None:
        """One cell id per class. The same name in two modules is two boxes."""
        object_id: dict[int, str] = {}
        ids_by_name: dict[str, list[str]] = {}
        id_to_oclass: dict[str, OoadClass] = {}
        module_of: dict[int, Module] = {}
        for module in canonical.modules:
            for oclass in module.classes:
                cell_id = f"{self._slug(module.name)}--{self._slug(oclass.name)}"
                if cell_id in id_to_oclass:
                    cell_id = f"{cell_id}-{oclass.sequential_order}"
                object_id[id(oclass)] = cell_id
                id_to_oclass[cell_id] = oclass
                module_of[id(oclass)] = module
                ids_by_name.setdefault(oclass.name, []).append(cell_id)
                plain = self._plain_class_name(oclass.name)
                if plain and plain != oclass.name:
                    ids_by_name.setdefault(plain, []).append(cell_id)
        self._object_id = object_id
        self._ids_by_name = ids_by_name
        self._id_to_oclass = id_to_oclass
        self._module_of = module_of
        self._name_to_id = {name: ids[0] for name, ids in ids_by_name.items()}

    def _resolve_target(self, source: OoadClass, target_name: str) -> Optional[str]:
        module = self._module_of.get(id(source))
        if module is not None:
            for oclass in module.classes:
                if oclass.name == target_name or self._plain_class_name(oclass.name) == target_name:
                    return self._object_id[id(oclass)]
        ids = self._ids_by_name.get(target_name) or []
        return ids[0] if ids else None

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
        local_ids = [self._object_id[id(c)] for c in module.classes]
        local_set = set(local_ids)
        self._local_module_name = page_name
        import_ids = self._direct_import_ids(local_set)
        self._import_ids = import_ids
        self._local_id_list = local_ids
        self._local_ids = local_set
        self._page_ids = local_set | set(import_ids)
        arrows = self._page_arrows()
        cards = self._page_cards(arrows)
        CardPlacement(list(cards.values()), arrows).place()
        self._draw_cards(root_el, cards)
        self._draw_arrows(root_el, cards, arrows)
        self._fit_page_to_cards(root_el, cards)

    def _page_arrows(self) -> List[DiagramArrow]:
        """One arrow per pair of classes on this page, keeping the strongest kind and naming every property it stands for."""
        rank = {'inheritance': 4, 'composition': 3, 'aggregation': 2, 'association': 1, 'relative': 1}
        arrows: Dict[Tuple[str, str], DiagramArrow] = {}
        for source, target, kind in self._page_relationships():
            if source == target:
                continue
            label = self._arrow_labels.get((source, target), '')
            arrow = arrows.setdefault((source, target), DiagramArrow(source, target, kind, label))
            if rank[kind] > rank[arrow.kind]:
                arrow.kind = kind
        drawn = {
            pair: arrow for pair, arrow in arrows.items()
            if not self._repeats_inherited_arrow(arrow, arrows) and not self._is_weaker_than_opposite(pair, arrows, rank)
        }
        return list(drawn.values()) + self._arrows_for_unlinked_classes(drawn)

    def _is_weaker_than_opposite(self, pair, arrows: Dict[Tuple[str, str], DiagramArrow], rank: Dict[str, int]) -> bool:
        opposite = arrows.get((pair[1], pair[0]))
        return opposite is not None and rank[opposite.kind] > rank[arrows[pair].kind]

    def _arrows_for_unlinked_classes(self, arrows: Dict[Tuple[str, str], DiagramArrow]) -> List[DiagramArrow]:
        """A class no field reaches still belongs to the model, so its first use in an operation draws it in, dashed."""
        linked = {cell_id for pair in arrows for cell_id in pair}
        found = []
        for cell_id in sorted(self._page_ids - linked):
            arrow = self._operation_arrow(cell_id)
            if arrow is not None:
                found.append(arrow)
        return found

    def _operation_arrow(self, cell_id: str) -> Optional[DiagramArrow]:
        oclass = self._id_to_oclass[cell_id]
        name = self._plain_class_name(oclass.name)
        for operation in oclass.operations:
            for callee in operation.callees:
                target = self._resolve_target(oclass, callee.split('.', 1)[0].strip())
                if target in self._page_ids and target != cell_id:
                    return DiagramArrow(cell_id, target, 'dependency', operation.name)
        for other_id in sorted(self._page_ids - {cell_id}):
            for operation in self._id_to_oclass[other_id].operations:
                signature = operation.return_type + ' '.join(parameter.save() for parameter in operation.parameters)
                if re.search(rf'\b{re.escape(name)}\b', signature):
                    return DiagramArrow(other_id, cell_id, 'dependency', operation.name)
        return None

    def _repeats_inherited_arrow(self, arrow: DiagramArrow, arrows: Dict[Tuple[str, str], DiagramArrow]) -> bool:
        """A subclass restating its base's field says nothing a reader cannot already see on the base."""
        return any(
            source == arrow.source and kind == 'inheritance' and (target, arrow.target) in arrows
            for source, target, kind in self._relationships
        )

    def _page_cards(self, arrows: List[DiagramArrow]) -> Dict[str, DiagramCard]:
        cards: Dict[str, DiagramCard] = {}
        for cell_id in self._page_ids:
            node = self._card_node(cell_id)
            arrow_count = sum(1 for arrow in arrows if cell_id in (arrow.source, arrow.target))
            width = max(node.width(), SMALLEST_PORT_SPACING * (arrow_count + 1))
            cards[cell_id] = DiagramCard(cell_id, width, node.height(), self._id_to_module.get(cell_id, ''))
        return dict(sorted(cards.items()))

    def _card_node(self, cell_id: str) -> DrawIOClass:
        oclass = self._id_to_oclass[cell_id]
        if cell_id in self._import_ids:
            return self._imported_class(oclass, self._id_to_module.get(cell_id, 'other'))
        node = self.load_class(oclass)
        module_label = self._id_to_module.get(cell_id, '')
        node.fill_color = self._module_fills.get(module_label, '')
        node.owning_module = self._module_of[id(oclass)].name.strip() if id(oclass) in self._module_of else ''
        return node

    def _draw_cards(self, root_el, cards: Dict[str, DiagramCard]) -> None:
        for card in cards.values():
            node = self._card_node(card.cell_id)
            node.cell_id = card.cell_id
            node.geometry = card.geometry
            Page('', root_el).place(node)

    def _draw_arrows(self, root_el, cards: Dict[str, DiagramCard], arrows: List[DiagramArrow], kept_paths=()) -> None:
        routed = ArrowRouter(list(cards.values()), arrows, kept_paths=kept_paths).route()
        used_ids = [int(cell.get('id')) for cell in root_el.iter('mxCell') if (cell.get('id') or '').isdigit()]
        first_id = max(used_ids, default=len(cards) + 10) + 1
        for offset, arrow in enumerate(routed):
            self._create_edge(root_el, arrow, cards, str(first_id + offset))

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
        self._graph_of = lambda _root: model_el
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
        previous = self.previous if self.keep_positioning else None
        prev_edges = self._read_edges(previous) if previous else {}
        self._import_ids = []
        self._local_ids = None
        self._page_ids = set(self._id_to_oclass)
        arrows = self._page_arrows()
        cards = self._page_cards(arrows)
        self._place_cards_keeping(cards, arrows, self._read_positions(previous) if previous else {})
        self._draw_cards(root_el, cards)
        kept_pairs = self._copy_kept_edges(root_el, prev_edges)
        new_arrows = [arrow for arrow in arrows if (arrow.source, arrow.target) not in kept_pairs]
        kept_paths = [self._edge_waypoints(prev_edges[pair]) for pair in kept_pairs]
        self._draw_arrows(root_el, cards, new_arrows, kept_paths)
        self._fit_page_to_cards(root_el, cards)

    def _place_cards_keeping(self, cards, arrows, positions) -> None:
        """Cards already on the page stay where a person left them. Only new ones are laid out, below the rest."""
        new_cards = [card for cell_id, card in cards.items() if cell_id not in positions]
        new_ids = {card.cell_id for card in new_cards}
        inner = [arrow for arrow in arrows if arrow.source in new_ids and arrow.target in new_ids]
        CardPlacement(new_cards, inner).place()
        for cell_id, (x, y) in positions.items():
            if cell_id in cards:
                cards[cell_id].x, cards[cell_id].y = x, y
        kept = [card for card in cards.values() if card.cell_id not in new_ids]
        if kept:
            bottom = max(card.y + card.height for card in kept)
            for card in new_cards:
                card.y += bottom

    def _edge_waypoints(self, edge: ET.Element) -> List[Tuple[int, int]]:
        return [(int(float(point.get('x', 0))), int(float(point.get('y', 0)))) for point in edge.iter('mxPoint')]

    def _fit_page_to_cards(self, root_el, cards: Dict[str, DiagramCard]) -> None:
        graph = self._graph_of(root_el)
        graph.set('pageWidth', str(int(max(card.x + card.width for card in cards.values()) + PAGE_EDGE_ALLOWANCE)))
        graph.set('pageHeight', str(int(max(card.y + card.height for card in cards.values()) + PAGE_EDGE_ALLOWANCE)))

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

    def _module_tab_label(self, module_name: str) -> str:
        return module_tab_label(module_name)

    def _class_module_labels(self, modules: List[Module]) -> dict[str, str]:
        """Map class cell id → owning module short label for import stereotypes."""
        out: dict[str, str] = {}
        for module in modules:
            label = self._module_tab_label(module.name)
            for oclass in module.classes:
                out[self._object_id[id(oclass)]] = label
        return out

    def _collect_relationships(self, classes: List[OoadClass]) -> List[Tuple[str, str, str]]:
        relationships = []
        self._arrow_labels: Dict[Tuple[str, str], str] = {}
        for oclass in classes:
            src = self._object_id.get(id(oclass))
            if not src:
                continue
            for prop in oclass.properties:
                self._collect_property_relationship(src, oclass, prop, relationships)
            for base in self._base_names(oclass):
                tgt = self._resolve_target(oclass, base)
                if tgt and (src, tgt, 'inheritance') not in relationships:
                    relationships.append((src, tgt, 'inheritance'))
        return relationships

    def _collect_property_relationship(self, src, oclass, prop, relationships) -> None:
        rel = getattr(prop, 'relationship', None)
        tgt = self._resolve_target(oclass, rel.target) if rel is not None else None
        if not tgt:
            return
        relationships.append((src, tgt, rel.kind or 'association'))
        named = self._arrow_labels.get((src, tgt))
        self._arrow_labels[(src, tgt)] = f'{named}, {prop.name}' if named else prop.name

    def _base_names(self, oclass: OoadClass) -> List[str]:
        named = self._extends_base_name(oclass.name)
        return [named] if named else list(oclass.bases)

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

    def _add_diagram_page(self, mxfile: ET.Element, page_name: str) -> ET.Element:
        diagram = ET.SubElement(mxfile, 'diagram')
        diagram.set('name', page_name)
        diagram.set('id', f'page-{self._slug(page_name)}')
        model_el = ET.SubElement(diagram, 'mxGraphModel')
        self._page_width = '1654'
        self._page_height = '1169'
        self._set_graph_attrs(model_el)
        self._graph_of = lambda _root: model_el
        root_el = ET.SubElement(model_el, 'root')
        cell0 = ET.SubElement(root_el, 'mxCell')
        cell0.set('id', '0')
        cell1 = ET.SubElement(root_el, 'mxCell')
        cell1.set('id', '1')
        cell1.set('parent', '0')
        return root_el

    def _page_relationships(self) -> List[Tuple[str, str, str]]:
        page_ids = self._page_ids
        local_ids = self._local_ids
        return [(s, t, k) for s, t, k in self._relationships if s in page_ids and t in page_ids and (local_ids is None or s in local_ids or (t in local_ids and (k or '').lower() == 'inheritance'))]

    def _create_edge(self, root_el, arrow: DiagramArrow, cards: Dict[str, DiagramCard], edge_id: str) -> ET.Element:
        cell = ET.SubElement(root_el, 'mxCell')
        cell.set('id', edge_id)
        cell.set('value', arrow.label)
        cell.set('style', arrow_style(EDGE_STYLES.get(arrow.kind, DEFAULT_EDGE_STYLE), arrow, cards))
        cell.set('edge', '1')
        cell.set('source', arrow.source)
        cell.set('target', arrow.target)
        cell.set('parent', '1')
        geo = ET.SubElement(cell, 'mxGeometry')
        geo.set('relative', '1')
        geo.set('as', 'geometry')
        if arrow.corners:
            points = ET.SubElement(geo, 'Array')
            points.set('as', 'points')
            for x, y in arrow.corners:
                ET.SubElement(points, 'mxPoint', attrib={'x': str(x), 'y': str(y)})
        return cell

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
            # UML rows start after a tag. Stop at the next break, so Collection<Customer> stays intact.
            return [
                line.strip()
                for line in re.findall(
                    r'(?:^|>|<br\s*/?>)\s*[+\-]\s*(.+?)(?=<br\s*/?>|</)',
                    sec,
                    flags=re.IGNORECASE,
                )
                if line.strip()
            ]
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

def arrow_style(base_style: str, arrow: DiagramArrow, cards: Dict[str, DiagramCard]) -> str:
    """The arrow's style plus its exit and entry points, as fractions of each card, so Draw.io keeps both ends put."""
    source, target = cards[arrow.source], cards[arrow.target]
    exit_x = round((arrow.exit_point[0] - source.x) / source.width, 4)
    exit_y = round((arrow.exit_point[1] - source.y) / source.height, 4)
    entry_x = round((arrow.entry_point[0] - target.x) / target.width, 4)
    entry_y = round((arrow.entry_point[1] - target.y) / target.height, 4)
    return (
        f'{base_style}exitX={exit_x};exitY={exit_y};exitDx=0;exitDy=0;exitPerimeter=0;'
        f'entryX={entry_x};entryY={entry_y};entryDx=0;entryDy=0;entryPerimeter=0;'
    )


class _ContainmentLayout:

    def __init__(self) -> None:
        self.bounds: Dict[str, Tuple[float, float, float, float]] = {}
        self.parent_id: Dict[str, str] = {}
        self.name_to_id: Dict[str, str] = {}
        self.render_order: List[str] = []
