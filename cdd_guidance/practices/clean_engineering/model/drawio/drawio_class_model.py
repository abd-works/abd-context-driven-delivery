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

One render or parse is one call; the state it needs while it works lives on a writer or reader made for that call,
never on the channel, so two renders through one channel cannot see each other's ids or positions.
"""
from __future__ import annotations

import copy
import html
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass, UnreadableSource
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import marks_in
from cdd_guidance.practices.clean_engineering.model.diagram.class_layout import ArrowRouter, CardSpacing, DiagramArrow
from cdd_guidance.practices.clean_engineering.model.diagram.class_view import (
    ClassView,
    ClassViewPage,
    cell_slug as _cell_slug,
    plain_class_name as _plain_class_name,
)
from cdd_guidance.practices.clean_engineering.model.diagram.diagram_node import DiagramCleanEngineeringModel, ModulesView
from cdd_guidance.practices.clean_engineering.model.diagram.geometry import Geometry
from cdd_guidance.practices.clean_engineering.model.diagram.module_layout import MODULE_START_X, MODULE_START_Y, ModuleLayout
from cdd_guidance.practices.clean_engineering.model.drawio.page.drawio_page import DrawioPage, class_name_in, style_value
from cdd_guidance.practices.clean_engineering.model.drawio.diagram_node import (
    DrawIOClass,
    DrawIOModule,
    DrawIOImportedClass,
)
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property

_EDGE_BASE_STYLE = 'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;fontSize=10;labelBackgroundColor=#ffffff;'
EDGE_STYLES = {'inheritance': f'{_EDGE_BASE_STYLE}endArrow=block;endSize=16;endFill=0;', 'composition': f'{_EDGE_BASE_STYLE}startArrow=diamondThin;startFill=1;startSize=14;endArrow=open;endSize=12;', 'aggregation': f'{_EDGE_BASE_STYLE}startArrow=diamondThin;startFill=0;startSize=14;endArrow=open;endSize=12;', 'association': f'{_EDGE_BASE_STYLE}endArrow=open;endSize=12;', 'dependency': f'{_EDGE_BASE_STYLE}dashed=1;endArrow=open;endSize=12;'}
DEFAULT_EDGE_STYLE = EDGE_STYLES['association']
PAGE_EDGE_ALLOWANCE = 200
MODULES_PAGE_MARGIN = 80
"""The room a modules view leaves right of and below its last module; its title is inset half of it on each side."""
DEPENDENCY_ID_OFFSET = 20
"""Dependency arrows are numbered past the module cells, so an arrow's id never repeats a cell's."""
CLASS_PAGE_WIDTH = 1654
CLASS_PAGE_HEIGHT = 1169
MODULES_PAGE_WIDTH = 1600
MODULES_PAGE_HEIGHT = 1200
MODULE_DEP_EDGE_STYLE = 'edgeStyle=orthogonalEdgeStyle;rounded=1;endArrow=classic;html=1;strokeWidth=2;fontSize=10;'
MODULE_TITLE_STYLE = 'text;html=1;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;'
MODULE_SUBTITLE_STYLE = 'text;html=1;align=center;verticalAlign=middle;fontSize=11;fontStyle=2;'
_MODULE_MARKER = 'fillColor=#1a3a6e'
_MODULE_CHILD_MARKER = 'fillColor=#dae8fc'
# The interaction a dependency names, written on its arrow as `«runs»` on `Repo ---<<runs>>--> Git`.
_DEPENDENCY_LABEL = re.compile('«([^»]+)»')



class DrawIOCleanEngineeringModel(DiagramCleanEngineeringModel):
    module_type = DrawIOModule

    module_cell_types: Tuple[type, ...] = (DrawIOModule,)
    """The cell types a modules view reads its cells back as, each picked by the kind its cell's style names; a model
    that draws modules of its own kinds names their cell types first."""

    def __init__(self, name: str='', sequential_order: int=1) -> None:
        super().__init__(name, sequential_order)
        # The diagram as it is now; with keep_positioning, cards and arrows already on it stay where they are.
        self.previous = None
        self.keep_positioning = False
        # With keep_positioning, also close up the empty space between the kept cards, keeping their arrangement.
        self.close_gaps = False

    def save(self) -> str:
        return self.render(self)

    def imported_class(self, source: OoadClass, from_module: str = '') -> DrawIOImportedClass:
        loaded = DrawIOImportedClass(
            name=source.name,
            sequential_order=source.sequential_order,
            from_module=from_module,
        )
        loaded.translate_from(source)
        return loaded

    def parse(self, text: str) -> 'DrawIOCleanEngineeringModel':
        """Read a modules-view or class-view diagram into this model's own modules, and return it."""
        root_el = self._diagram_xml(text)
        self.modules = []
        document = DrawioPage(None, '', root_el)
        if self._looks_like_modules_diagram(document.cells):
            self._read_modules(document)
        else:
            self._read_classes(root_el, document)
        return self

    def _diagram_xml(self, text: str) -> ET.Element:
        try:
            return ET.fromstring(text)
        except ET.ParseError as error:
            raise UnreadableSource(f'draw.io diagram is not valid XML: {error}') from error

    def _read_classes(self, root_el: ET.Element, document: DrawioPage) -> None:
        """A diagram of several pages holds one module per page; a single page names each card's module in its style."""
        if len(root_el.findall('diagram')) > 1:
            _ClassDiagramReader(self).read_pages(DrawioPage.pages_in(root_el))
        else:
            _ClassDiagramReader(self).read_single_page(document)

    def render(self, canonical: CleanEngineeringModel) -> str:
        """Become the canonical model once, as Draw.io modules and classes, then write this model's own diagram."""
        if canonical is not self:
            self.translate_from(canonical)
        if self.is_modules_view:
            return _ModulesDiagramWriter(self).write()
        return _ClassDiagramWriter(self).write()

    def kept_previous(self) -> Optional[str]:
        """The previous diagram when this render keeps its positions, else None."""
        return self.previous if self.keep_positioning else None

    def _read_modules(self, document: DrawioPage) -> None:
        id_to_module: dict[str, Module] = {}
        for cell in document.vertices:
            style = cell.get('style', '')
            if 'text;' in style:
                self._read_title(cell)
                continue
            module = self._module_in(cell, len(id_to_module) + 1) if self._is_module_style(style) else None
            if module is None:
                continue
            cell_id = cell.get('id', '')
            id_to_module[cell_id] = module
            if not cell_id.startswith('nest-'):
                self.modules.append(module)
        self._add_module_dependencies(document, id_to_module)

    def _read_title(self, cell: ET.Element) -> None:
        """The system's name, from the `{name} - Modules Context` title a modules view writes."""
        if cell.get('id') != 'title':
            return
        named = re.match(r'^(.+?)\s*[-\-]\s*Modules?', html.unescape(cell.get('value', '')))
        if named:
            self.name = named.group(1).strip()

    def _module_in(self, cell: ET.Element, sequential_order: int) -> Optional[Module]:
        """The module a cell shows, read as the first of this model's cell types that draws the cell's kind."""
        read = (kind.from_cell(cell, sequential_order) for kind in self.module_cell_types)
        return next((module for module in read if module is not None), None)

    def _looks_like_modules_diagram(self, mxcells: List[ET.Element]) -> bool:
        kinds = [self._vertex_diagram_kind(cell) for cell in mxcells]
        module_cells, class_cells = kinds.count('module'), kinds.count('class')
        return bool(module_cells) and (not class_cells or module_cells > class_cells)

    def _vertex_diagram_kind(self, cell: ET.Element) -> Optional[str]:
        if cell.get('vertex') != '1':
            return None
        style = cell.get('style', '')
        value = cell.get('value', '')
        if 'text;' in style:
            return None
        if self._is_module_style(style):
            return 'module'
        name, _stereotypes, props, ops = _class_card_members(value)
        if name and (props or ops or 'hr size=' in value.lower()):
            return 'class'
        if name and ('\u2022' in html.unescape(value) or '-' in html.unescape(value)):
            return 'module'
        return None

    def _is_module_style(self, style: str) -> bool:
        return _MODULE_MARKER in style or _MODULE_CHILD_MARKER in style

    def _add_module_dependencies(self, document: DrawioPage, id_to_module: dict[str, Module]) -> None:
        """A child cell depends on the top-level cell it sits in; then each edge source depends on its target, keeping
        the words written on the edge."""
        nested = [
            (id_to_module.get(cell.get('id', '')), id_to_module.get(cell.get('parent', '')))
            for cell in document.vertices
        ]
        drawn = [
            (id_to_module.get(cell.get('source', '')), id_to_module.get(cell.get('target', '')), html.unescape(cell.get('value', '') or ''))
            for cell in document.edges
        ]
        nested = [(child, parent, '') for child, parent in nested if parent is None or parent in self.modules]
        for dependent, depended_on, label in nested + drawn:
            if dependent is None or depended_on is None or dependent not in self.modules:
                continue
            if depended_on.name not in dependent.dependencies:
                dependent.dependencies.append(depended_on.name)
            if label:
                dependent.dependency_labels[depended_on.name] = label





class _ClassDiagramReader:
    """Reads class cards and the arrows between them back into a model. One reader serves one parse."""

    def __init__(self, model: DrawIOCleanEngineeringModel) -> None:
        self.model = model
        self._classes_by_cell: dict[str, OoadClass] = {}
        self._names_by_cell: dict[str, str] = {}
        self._seen_names: set[str] = set()

    def read_single_page(self, page: DrawioPage) -> None:
        """One page: each card names its module in its style."""
        modules: Dict[str, DrawIOModule] = {}
        for cell, oclass in self._class_cards(page):
            self._names_by_cell[cell.get('id', '')] = oclass.name
            if 'dashed=1' in cell.get('style', ''):
                continue
            module_name = style_value(cell.get('style', ''), 'module')
            module = modules.setdefault(module_name, DrawIOModule(name=module_name, sequential_order=len(modules) + 1))
            oclass.sequential_order = len(self._classes_by_cell) + 1
            module.classes.append(oclass)
            self._classes_by_cell[cell.get('id', '')] = oclass
        self.model.modules.extend(modules.values())
        self._read_arrows(page)

    def read_pages(self, pages: List[DrawioPage]) -> None:
        """One Draw.io page → one module; skip dashed «from:» import cards."""
        for page in pages:
            module = DrawIOModule(name=page.name or f'module-{len(self.model.modules) + 1}', sequential_order=len(self.model.modules) + 1)
            self._read_page_cards(page, module)
            if module.classes:
                self.model.modules.append(module)
            self._read_arrows(page)

    def _read_page_cards(self, page: DrawioPage, module: DrawIOModule) -> None:
        for cell, oclass in self._class_cards(page):
            self._names_by_cell[cell.get('id', '')] = oclass.name
            if 'dashed=1' in cell.get('style', '') or oclass.name in self._seen_names:
                continue
            self._seen_names.add(oclass.name)
            oclass.sequential_order = len(module.classes) + 1
            module.classes.append(oclass)
            self._classes_by_cell[cell.get('id', '')] = oclass

    def _class_cards(self, page: DrawioPage) -> List[Tuple[ET.Element, DrawIOClass]]:
        """Each class card on the page, with the class it shows; the caller numbers the classes it keeps."""
        cards = []
        for cell in page.vertices:
            name, stereotypes, props, ops = _class_card_members(cell.get('value', ''))
            if not name:
                continue
            oclass = DrawIOClass(name=_plain_class_name(name), sequential_order=1)
            oclass.properties = props
            oclass.operations = ops
            oclass.stereotypes = stereotypes + [item for item in marks_in(name) if item not in stereotypes]
            cards.append((cell, oclass))
        return cards

    def _read_arrows(self, page: DrawioPage) -> None:
        """Each arrow marks the property it stands for with its kind; the properties then derive their relationships."""
        for cell in page.edges:
            source = self._classes_by_cell.get(cell.get('source', ''))
            if source is None:
                continue
            target_id = cell.get('target', '')
            target = self._classes_by_cell.get(target_id)
            target_name = target.name if target is not None else self._names_by_cell.get(target_id, target_id)
            kind = page.kind_of(cell)
            if kind == 'inheritance' and target_name not in source.bases:
                source.bases.append(target_name)
            for label in _DEPENDENCY_LABEL.findall(html.unescape(cell.get('value', '') or '')):
                source.arrows.depend_on(target_name, label.strip())
            source.take_arrow(target_name, kind)
        for oclass in self._classes_by_cell.values():
            for prop in oclass.properties:
                prop.arrow.derive()


class _ModulesDiagramWriter(ModulesView):
    """Writes one modules-view diagram: top-level modules layered by dependency depth, path children nested inside."""

    def __init__(self, channel: DrawIOCleanEngineeringModel) -> None:
        super().__init__(channel)
        self._bounds: Dict[str, Geometry] = {}
        self._parent_ids: Dict[str, str] = {}
        self._cell_ids: Dict[str, str] = {
            name: f'nest-{_cell_slug(name)}' if name in self._forest.synthetic else _cell_slug(name) or name
            for name in self._forest.by_name
        }

    def write(self) -> str:
        previous = DrawioPage.whole(self._channel.previous) if self._channel.previous else None
        previous_positions = previous.positions() if previous is not None else {}
        self._lay_out()
        mxfile = ET.Element('mxfile')
        mxfile.set('host', 'CleanEngineering.diagram.drawio')
        diagram = ET.SubElement(mxfile, 'diagram')
        diagram.set('name', 'Modules Context')
        diagram.set('id', 'modules-context')
        model_el = ET.SubElement(diagram, 'mxGraphModel')
        page_width = int(max(MODULES_PAGE_WIDTH, max((b[0] + b[2] for b in self._bounds.values()), default=MODULE_START_X) + MODULES_PAGE_MARGIN))
        page_height = int(max(MODULES_PAGE_HEIGHT, max((b[1] + b[3] for b in self._bounds.values()), default=MODULE_START_Y) + MODULES_PAGE_MARGIN))
        _set_graph_attrs(model_el, page_width, page_height)
        root_el = _add_graph_root(model_el)
        self._write_titles(root_el, page_width)
        for name in self._forest.in_model_order(self._forest.roots):
            self._write_module(root_el, name, previous_positions)
        self._write_dependencies(root_el)
        ET.indent(ET.ElementTree(mxfile), space='  ')
        return ET.tostring(mxfile, encoding='unicode', xml_declaration=False)

    def _write_titles(self, root_el: ET.Element, page_width: int) -> None:
        subtitle = (
            'Independent modules with one-way dependencies. Arrows point toward the depended-on module (build before). '
            'Path nesting = containment; shared base terms live on the parent.'
        )
        for cell_id, value, style, y, height in (
            ('title', self._channel.modules_title, MODULE_TITLE_STYLE, '20', '32'),
            ('subtitle', subtitle, MODULE_SUBTITLE_STYLE, '55', '20'),
        ):
            cell = ET.SubElement(root_el, 'mxCell', attrib={'id': cell_id, 'value': value, 'style': style, 'parent': '1', 'vertex': '1'})
            ET.SubElement(cell, 'mxGeometry', attrib={
                'x': str(MODULES_PAGE_MARGIN // 2), 'y': y, 'width': str(page_width - MODULES_PAGE_MARGIN),
                'height': height, 'as': 'geometry',
            })

    def _write_module(self, root_el: ET.Element, name: str, previous_positions: Dict[str, Tuple[float, float]]) -> None:
        cell_id = self._cell_ids[name]
        parent_id = self._parent_ids.get(name, '1')
        x, y, width, height = self._bounds[name]
        if cell_id in previous_positions and parent_id == '1':
            x, y = previous_positions[cell_id]
        node = self._cells[name]
        node.cell_id = cell_id
        node.parent_id = parent_id
        node.nested = parent_id != '1'
        node.geometry = Geometry(float(x), float(y), float(width), float(height))
        node.append_to(root_el)

    def _write_dependencies(self, root_el: ET.Element) -> None:
        edge_number = len(self._forest.by_name) + DEPENDENCY_ID_OFFSET
        for module in self._channel.modules:
            source_id = self._cell_ids.get(module.name)
            for dependency in module.dependencies:
                target_id = self._cell_ids.get(dependency)
                if dependency == module.path_parent or not source_id or not target_id:
                    continue
                edge_number += 1
                cell = ET.SubElement(root_el, 'mxCell', attrib={
                    'id': f'dep-{edge_number}', 'value': self._cells[module.name].dependency_labels.get(dependency, ''),
                    'style': MODULE_DEP_EDGE_STYLE, 'edge': '1',
                    'source': source_id, 'target': target_id, 'parent': '1',
                })
                ET.SubElement(cell, 'mxGeometry', attrib={'relative': '1', 'as': 'geometry'})

    def _lay_out(self) -> None:
        """The shared modules layout: roots in columns by dependency depth, path children nested inside their parents."""
        layout = ModuleLayout(self._forest, self._cells).lay_out()
        self._bounds = layout.bounds
        self._parent_ids = {
            name: self._cell_ids[parent] if parent is not None else '1' for name, parent in layout.parent_of.items()
        }


class _ClassDiagramWriter(ClassView):
    """Writes one class-view diagram as Draw.io pages."""

    def write(self) -> str:
        mxfile = ET.Element('mxfile')
        mxfile.set('host', 'CleanEngineering.diagram.drawio')
        if self.on_one_page:
            self._write_single_page(mxfile)
        else:
            for module in self.named_modules:
                self._write_module_page(mxfile, module)
        ET.indent(ET.ElementTree(mxfile), space='  ')
        return ET.tostring(mxfile, encoding='unicode', xml_declaration=False)

    def _write_single_page(self, mxfile: ET.Element) -> None:
        graph = self._add_diagram_page(mxfile, 'CleanEngineering Model', 'CleanEngineering-model')
        page = _ClassDiagramPage(self)
        previous = self.channel.kept_previous()
        drawn = DrawioPage.whole(previous) if previous else None
        positions = drawn.positions() if drawn is not None else {}
        previous_edges = drawn.edges_by_ends() if drawn is not None else {}
        page.write(graph, positions, previous_edges)

    def _write_module_page(self, mxfile: ET.Element, module: Module) -> None:
        page_name = module.name.strip()
        graph = self._add_diagram_page(mxfile, page_name, f'page-{_cell_slug(page_name)}')
        drawn = self.previous_pages.get(page_name)
        positions = drawn.positions() if drawn is not None else {}
        previous_edges = drawn.edges_by_ends() if drawn is not None else {}
        _ClassDiagramPage(self, module).write(graph, positions, previous_edges)

    def _previous_pages(self) -> Dict[str, DrawioPage]:
        """The pages of the diagram this render replaces, by name; none when it keeps no positions or the previous
        text is not a draw.io file."""
        previous = self.channel.kept_previous()
        if not previous:
            return {}
        try:
            return {page.name: page for page in DrawioPage.pages_in(ET.fromstring(previous))}
        except ET.ParseError:
            return {}

    def _add_diagram_page(self, mxfile: ET.Element, page_name: str, page_id: str) -> ET.Element:
        """A new diagram page; returns its mxGraphModel."""
        diagram = ET.SubElement(mxfile, 'diagram')
        diagram.set('name', page_name)
        diagram.set('id', page_id)
        graph = ET.SubElement(diagram, 'mxGraphModel')
        _set_graph_attrs(graph, CLASS_PAGE_WIDTH, CLASS_PAGE_HEIGHT)
        return graph


class _ClassDiagramPage(ClassViewPage):
    """One Draw.io page of a class diagram."""

    def write(self, graph: ET.Element, positions: Dict[str, Tuple[float, float]], previous_edges: Dict[Tuple[str, str], ET.Element]) -> None:
        """Place the cards, keeping any a person already placed (closing up the space between them when the render asks
        to), then draw arrows, keeping the routes already drawn."""
        root_el = _add_graph_root(graph)
        cards, arrows = self.laid_out(positions)
        if self._writer.channel.kept_previous() and self._writer.channel.close_gaps and CardSpacing(list(cards.values()), arrows).close_gaps():
            # A card moved, so an arrow kept from the last drawing no longer meets it: every arrow is drawn again.
            previous_edges = {}
        for card in cards.values():
            card.append_to(root_el)
        kept_pairs = self._copy_kept_edges(root_el, previous_edges)
        new_arrows = [arrow for arrow in arrows if (arrow.source, arrow.target) not in kept_pairs]
        kept_paths = [self._edge_waypoints(previous_edges[pair]) for pair in kept_pairs]
        self._append_edges(root_el, cards, ArrowRouter(list(cards.values()), new_arrows, kept_paths=kept_paths).route())
        graph.set('pageWidth', str(int(max((card.geometry.x + card.geometry.width for card in cards.values()), default=0) + PAGE_EDGE_ALLOWANCE)))
        graph.set('pageHeight', str(int(max((card.geometry.y + card.geometry.height for card in cards.values()), default=0) + PAGE_EDGE_ALLOWANCE)))

    def _copy_kept_edges(self, root_el: ET.Element, previous_edges: Dict[Tuple[str, str], ET.Element]) -> set:
        kept_pairs: set[Tuple[str, str]] = set()
        for source, target, _kind in self._writer.relationships:
            existing = previous_edges.get((source, target))
            if existing is None:
                continue
            root_el.append(copy.deepcopy(existing))
            kept_pairs.add((source, target))
        return kept_pairs

    def _edge_waypoints(self, edge: ET.Element) -> List[Tuple[int, int]]:
        return [(int(float(point.get('x', 0))), int(float(point.get('y', 0)))) for point in edge.iter('mxPoint')]

    def _append_edges(self, root_el: ET.Element, cards: Dict[str, DrawIOClass], routed: List[DiagramArrow]) -> None:
        """Each routed arrow as an edge cell, numbered after the highest numeric id already on the page."""
        used_ids = [int(cell.get('id')) for cell in root_el.iter('mxCell') if (cell.get('id') or '').isdigit()]
        first_id = max(used_ids, default=len(cards) + 10) + 1
        for offset, arrow in enumerate(routed):
            root_el.append(self._edge_cell(arrow, cards, str(first_id + offset)))

    def _edge_cell(self, arrow: DiagramArrow, cards: Dict[str, DrawIOClass], edge_id: str) -> ET.Element:
        style = EDGE_STYLES.get(arrow.kind, DEFAULT_EDGE_STYLE)
        if arrow.straight:
            style = style.replace('edgeStyle=orthogonalEdgeStyle;', 'edgeStyle=none;')
        cell = ET.Element('mxCell', attrib={
            'id': edge_id, 'value': arrow.label, 'style': self._anchored_style(style, arrow, cards), 'edge': '1',
            'source': arrow.source, 'target': arrow.target, 'parent': '1',
        })
        geo = ET.SubElement(cell, 'mxGeometry', attrib={'relative': '1', 'as': 'geometry'})
        if arrow.corners:
            points = ET.SubElement(geo, 'Array', attrib={'as': 'points'})
            for x, y in arrow.corners:
                ET.SubElement(points, 'mxPoint', attrib={'x': str(x), 'y': str(y)})
        return cell

    def _anchored_style(self, base_style: str, arrow: DiagramArrow, cards: Dict[str, DrawIOClass]) -> str:
        """The arrow's style plus its exit and entry points, as fractions of each card, so Draw.io keeps both ends put."""
        exit_x, exit_y, entry_x, entry_y = arrow.anchors_on(cards[arrow.source].geometry, cards[arrow.target].geometry)
        return (
            f'{base_style}exitX={exit_x};exitY={exit_y};exitDx=0;exitDy=0;exitPerimeter=0;'
            f'entryX={entry_x};entryY={entry_y};entryDx=0;entryDy=0;entryPerimeter=0;'
        )


def _set_graph_attrs(graph: ET.Element, page_width: int, page_height: int) -> None:
    for k, v in [('dx', '1200'), ('dy', '800'), ('grid', '1'), ('gridSize', '10'), ('guides', '1'), ('tooltips', '1'), ('connect', '1'), ('arrows', '1'), ('fold', '1'), ('page', '1'), ('pageScale', '1'), ('pageWidth', str(page_width)), ('pageHeight', str(page_height)), ('math', '0'), ('shadow', '0')]:
        graph.set(k, v)


def _add_graph_root(graph: ET.Element) -> ET.Element:
    root_el = ET.SubElement(graph, 'root')
    ET.SubElement(root_el, 'mxCell', attrib={'id': '0'})
    ET.SubElement(root_el, 'mxCell', attrib={'id': '1', 'parent': '0'})
    return root_el


def _class_card_members(card_html: str) -> Tuple[Optional[str], List[str], List[Property], List[Operation]]:
    """The class name, stereotypes, properties, and operations a UML class card shows; no name for a cell that is not
    a class card."""
    text = html.unescape(card_html)
    if ('\u2022' in text or '-' in text) and 'hr size="1"' not in text.lower() and ('<hr size=' not in text.lower()):
        if re.search('<i[^>]*>', text, re.IGNORECASE):
            return (None, [], [], [])
    name = class_name_in(card_html)
    if not name:
        return (None, [], [], [])
    sections = re.split('<hr\\s+size="1"\\s*/?>', text, flags=re.IGNORECASE)
    stereotypes = marks_in(sections[0])
    if len(sections) < 3:
        return (name, stereotypes, [], [])
    props = [Property.from_signature(line) or Property(name=line.strip()) for line in _card_lines(sections[1])]
    ops = [operation for operation in (Operation.from_signature(line) for line in _card_lines(sections[2])) if operation is not None]
    return (name, stereotypes, props, ops)


def _card_lines(section: str) -> List[str]:
    # UML lines start after a tag. Stop at the next break, so Collection<Customer> stays intact.
    return [
        line.strip()
        for line in re.findall(r'(?:^|>|<br\s*/?>)\s*[+\-]\s*(.+?)(?=<br\s*/?>|</)', section, flags=re.IGNORECASE)
        if line.strip()
    ]
