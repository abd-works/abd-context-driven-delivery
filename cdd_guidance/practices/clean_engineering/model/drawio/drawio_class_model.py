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

from harness.annotations.name import Name

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass, UnreadableSource
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import marks_in, without_marks
from cdd_guidance.practices.clean_engineering.model.field_types import RELATIONSHIP_STRENGTH
from cdd_guidance.practices.clean_engineering.model.diagram.class_layout import (
    GROUP_FILL_COLORS,
    SMALLEST_PORT_SPACING,
    ArrowRouter,
    CardPlacement,
    DiagramArrow,
)
from cdd_guidance.practices.clean_engineering.model.diagram.diagram_node import (
    ContainmentForest,
    DiagramCleanEngineeringModel,
    module_tab_label,
)
from cdd_guidance.practices.clean_engineering.model.diagram.geometry import Geometry, MODULE_CELL_MIN_HEIGHT, MODULE_CELL_WIDTH
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
CLASSES_ON_ONE_PAGE = 40
PAGE_EDGE_ALLOWANCE = 200
CLASS_PAGE_WIDTH = 1654
CLASS_PAGE_HEIGHT = 1169
MODULES_PAGE_WIDTH = 1600
MODULES_PAGE_HEIGHT = 1200
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
# The interaction a dependency names, written on its arrow as `«runs»` on `Repo ---<<runs>>--> Git`.
_DEPENDENCY_LABEL = re.compile('«([^»]+)»')

Relationships = List[Tuple[str, str, str]]


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

    def save(self) -> str:
        return self.render(self)

    def load_module_cell(self, source: Module) -> DrawIOModule:
        """A Draw.io cell for a container module the containment forest made, filled from it."""
        loaded = self.load_module(source)
        loaded.translate_from(source)
        return loaded

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
        try:
            root_el = ET.fromstring(text)
        except ET.ParseError as error:
            raise UnreadableSource(f'draw.io diagram is not valid XML: {error}') from error
        self.modules = []
        document = DrawioPage(None, '', root_el)
        if _looks_like_modules_diagram(document.cells):
            self._read_modules(document)
            return self
        if len(root_el.findall('diagram')) > 1:
            _ClassDiagramReader(self).read_pages(DrawioPage.pages_in(root_el))
        else:
            _ClassDiagramReader(self).read_single_page(document)
        return self

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
        order = 1
        id_to_module: dict[str, Module] = {}
        for cell in document.vertices:
            style = cell.get('style', '')
            if 'text;' in style or style.startswith('text;'):
                if cell.get('id') == 'title':
                    title = html.unescape(cell.get('value', ''))
                    m = re.match(r'^(.+?)\s*[-\-]\s*Modules?', title)
                    if m:
                        self.name = m.group(1).strip()
                continue
            if not _is_module_style(style):
                continue
            cell_type = next((kind for kind in self.module_cell_types if kind.draws(style)), DrawIOModule)
            module = cell_type.from_cell(cell.get('value', ''), order)
            if module is None:
                continue
            cell_id = cell.get('id', '')
            id_to_module[cell_id] = module
            if not cell_id.startswith('nest-'):
                self.modules.append(module)
            order += 1
        self._add_module_dependencies(document, id_to_module)

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
            oclass = DrawIOClass(name=_plain_class_name(name), sequential_order=1, properties=props, operations=ops)
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
                source.depend_on(target_name, label.strip())
            source.take_arrow(target_name, kind)
        for oclass in self._classes_by_cell.values():
            for prop in oclass.properties:
                prop.derive_relationship()


class _ModulesDiagramWriter:
    """Writes one modules-view diagram: top-level modules layered by dependency depth, path children nested inside."""

    def __init__(self, channel: DrawIOCleanEngineeringModel) -> None:
        self._channel = channel
        self._forest = ContainmentForest.build(list(channel.modules), synthesize_parents=True)
        # The cell each module is drawn as: the channel's own module, or a Draw.io copy of a container the forest made.
        self._cells: Dict[str, DrawIOModule] = {
            name: module if isinstance(module, DrawIOModule) else channel.load_module_cell(module)
            for name, module in self._forest.by_name.items()
        }
        self._bounds: Dict[str, Geometry] = {}
        self._parent_ids: Dict[str, str] = {}
        self._cell_ids: Dict[str, str] = {}

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
        page_width = int(max(MODULES_PAGE_WIDTH, max((b[0] + b[2] for b in self._bounds.values()), default=MODULE_START_X) + 80))
        page_height = int(max(MODULES_PAGE_HEIGHT, max((b[1] + b[3] for b in self._bounds.values()), default=MODULE_START_Y) + 80))
        _set_graph_attrs(model_el, page_width, page_height)
        root_el = _add_graph_root(model_el)
        self._write_titles(root_el, page_width)
        for name in self._in_model_order(self._forest.roots):
            self._write_module(root_el, name, previous_positions)
        self._write_dependencies(root_el)
        ET.indent(ET.ElementTree(mxfile), space='  ')
        return ET.tostring(mxfile, encoding='unicode', xml_declaration=False)

    def _write_titles(self, root_el: ET.Element, page_width: int) -> None:
        system_name = self._channel.name or 'System'
        subtitle = (
            'Independent modules with one-way dependencies. Arrows point toward the depended-on module (build before). '
            'Path nesting = containment; shared base terms live on the parent.'
        )
        for cell_id, value, style, y, height in (
            ('title', f'{system_name} - Modules Context', MODULE_TITLE_STYLE, '20', '32'),
            ('subtitle', subtitle, MODULE_SUBTITLE_STYLE, '55', '20'),
        ):
            cell = ET.SubElement(root_el, 'mxCell', attrib={'id': cell_id, 'value': value, 'style': style, 'parent': '1', 'vertex': '1'})
            ET.SubElement(cell, 'mxGeometry', attrib={'x': '40', 'y': y, 'width': str(page_width - 80), 'height': height, 'as': 'geometry'})

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

    def _in_model_order(self, names: List[str]) -> List[str]:
        """The modules named and everything nested in them, each parent before its children, in the model's order, so
        parse reads the modules back in the order the model lists them."""
        ordered: List[str] = []
        for name in names:
            ordered.append(name)
            ordered.extend(self._in_model_order(self._forest.children_of.get(name, [])))
        return ordered

    def _write_dependencies(self, root_el: ET.Element) -> None:
        edge_number = len(self._forest.by_name) + 20
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
        """Layer roots by dependency depth, left to right; nest path children inside their parents."""
        layers: Dict[int, List[str]] = {}
        for root in self._forest.roots:
            layers.setdefault(self._forest.module_dep_depth(root), []).append(root)
        x_cursor = float(MODULE_START_X)
        for depth in sorted(layers):
            names = sorted(layers[depth], key=lambda n: (self._forest.by_name[n].sequential_order or 0, n))
            y = float(MODULE_START_Y)
            for name in names:
                self._place(name, (x_cursor, y), '1')
                y += self._bounds[name][3] + MODULE_ROW_GAP
            x_cursor += max(self._size(name)[0] for name in names) + MODULE_COL_GAP

    def _place(self, name: str, position: Tuple[float, float], parent_id: str) -> None:
        if parent_id == '1':
            self._bounds[name] = Geometry(position[0], position[1], *self._size(name))
        cell_id = f'nest-{_cell_slug(name)}' if name in self._forest.synthetic else _cell_slug(name) or name
        self._cell_ids[name] = cell_id
        self._parent_ids[name] = parent_id
        children = self._forest.children_of.get(name, [])
        if not children:
            return
        header_height = float(self._cells[name].header_height())
        sizes = [self._size(child) for child in children]
        columns = min(MODULE_CHILD_COLS, len(children))
        widths, heights = _grid_extents(sizes, columns)
        for index, child in enumerate(children):
            column, line = index % columns, index // columns
            relative_x = MODULE_CHILD_PAD_X + sum(widths[:column]) + MODULE_CHILD_GAP * column
            relative_y = header_height + MODULE_CHILD_PAD_Y + sum(heights[:line]) + MODULE_CHILD_GAP * line
            self._bounds[child] = Geometry(relative_x, relative_y, *sizes[index])
            self._place(child, (position[0] + relative_x, position[1] + relative_y), cell_id)

    def _size(self, name: str) -> Tuple[float, float]:
        """Width and height of a module cell, grown to hold its nested children."""
        header_height = float(self._cells[name].header_height())
        children = self._forest.children_of.get(name, [])
        if not children:
            return (float(MODULE_CELL_WIDTH), max(float(MODULE_CELL_MIN_HEIGHT), header_height))
        columns = min(MODULE_CHILD_COLS, len(children))
        widths, heights = _grid_extents([self._size(child) for child in children], columns)
        grid_width = sum(widths) + MODULE_CHILD_GAP * (columns - 1)
        grid_height = sum(heights) + MODULE_CHILD_GAP * (len(heights) - 1)
        return (max(float(MODULE_CELL_WIDTH), grid_width + 2 * MODULE_CHILD_PAD_X), header_height + grid_height + 2 * MODULE_CHILD_PAD_Y)


def _grid_extents(sizes: List[Tuple[float, float]], columns: int) -> Tuple[List[float], List[float]]:
    """The widest card in each column and the tallest in each line of a grid filled left to right."""
    widths = [0.0] * columns
    heights = [0.0] * ((len(sizes) + columns - 1) // columns)
    for index, (width, height) in enumerate(sizes):
        widths[index % columns] = max(widths[index % columns], width)
        heights[index // columns] = max(heights[index // columns], height)
    return (widths, heights)


class _ClassDiagramWriter:
    """Writes one class-view diagram: a single page, or one page per module when the model is large.

    Holds what every page needs: a cell id per class, the relationships between those ids, and each class's module."""

    def __init__(self, channel: DrawIOCleanEngineeringModel) -> None:
        self.channel = channel
        self.cell_ids: dict[int, str] = {}
        self.classes_by_cell: dict[str, OoadClass] = {}
        self.module_of: dict[int, Module] = {}
        self.classes = [oclass for module in channel.modules for oclass in module.classes]
        self._cell_ids_by_name: dict[str, list[str]] = {}
        self._assign_cell_ids()
        self.arrow_labels: Dict[Tuple[str, str], str] = {}
        # The interactions each pair's dependencies name, in model order: `stops`, `reads sections with`.
        self.dependency_labels: Dict[Tuple[str, str], List[str]] = {}
        self.relationships = self._collect_relationships()
        self.module_labels = {
            self.cell_ids[id(oclass)]: module_tab_label(module.name) for module in channel.modules for oclass in module.classes
        }
        self.named_modules = [module for module in channel.modules if module.classes]
        self.module_fills = self._module_fill_colors()

    def write(self) -> str:
        mxfile = ET.Element('mxfile')
        mxfile.set('host', 'CleanEngineering.diagram.drawio')
        if len(self.named_modules) < 2 or len(self.classes) <= CLASSES_ON_ONE_PAGE:
            self._write_single_page(mxfile)
        else:
            for module in self.named_modules:
                self._write_module_page(mxfile, module)
        ET.indent(ET.ElementTree(mxfile), space='  ')
        return ET.tostring(mxfile, encoding='unicode', xml_declaration=False)

    def resolve_target(self, source: OoadClass, target_name: str) -> Optional[str]:
        """The cell id of the class target_name names, preferring one in source's own module."""
        module = self.module_of.get(id(source))
        if module is not None:
            for oclass in module.classes:
                if oclass.name == target_name or _plain_class_name(oclass.name) == target_name:
                    return self.cell_ids[id(oclass)]
        ids = self._cell_ids_by_name.get(target_name) or []
        return ids[0] if ids else None

    def _assign_cell_ids(self) -> None:
        """One cell id per class. The same name in two modules is two boxes."""
        for module in self.channel.modules:
            for oclass in module.classes:
                cell_id = f"{_cell_slug(module.name)}--{_cell_slug(oclass.name)}"
                if cell_id in self.classes_by_cell:
                    cell_id = f"{cell_id}-{oclass.sequential_order}"
                self.cell_ids[id(oclass)] = cell_id
                self.classes_by_cell[cell_id] = oclass
                self.module_of[id(oclass)] = module
                self._cell_ids_by_name.setdefault(oclass.name, []).append(cell_id)
                plain = _plain_class_name(oclass.name)
                if plain and plain != oclass.name:
                    self._cell_ids_by_name.setdefault(plain, []).append(cell_id)

    def _module_fill_colors(self) -> Dict[str, str]:
        """One colour per module, so a reader sees where a class lives. One module needs no colour."""
        if len(self.named_modules) < 2:
            return {}
        return {
            module_tab_label(module.name): GROUP_FILL_COLORS[index % len(GROUP_FILL_COLORS)]
            for index, module in enumerate(self.named_modules)
        }

    def _collect_relationships(self) -> Relationships:
        relationships: Relationships = []
        for oclass in self.classes:
            source = self.cell_ids.get(id(oclass))
            if not source:
                continue
            for prop in oclass.properties:
                self._collect_property_relationship(source, oclass, prop, relationships)
            for dependency in oclass.dependencies:
                self._collect_dependency(source, oclass, dependency, relationships)
            for base in self._base_names(oclass):
                target = self.resolve_target(oclass, base)
                if target and (source, target, 'inheritance') not in relationships:
                    relationships.append((source, target, 'inheritance'))
        return relationships

    def _collect_property_relationship(self, source: str, oclass: OoadClass, prop: Property, relationships: Relationships) -> None:
        relationship = getattr(prop, 'relationship', None)
        target = self.resolve_target(oclass, relationship.target) if relationship is not None else None
        if not target:
            return
        relationships.append((source, target, relationship.kind or 'association'))
        named = self.arrow_labels.get((source, target))
        self.arrow_labels[(source, target)] = f'{named}, {prop.name}' if named else prop.name

    def _collect_dependency(self, source: str, oclass: OoadClass, dependency, relationships: Relationships) -> None:
        target = self.resolve_target(oclass, dependency.target)
        if not target or target == source:
            return
        if (source, target, 'dependency') not in relationships:
            relationships.append((source, target, 'dependency'))
        labels = self.dependency_labels.setdefault((source, target), [])
        if dependency.label and dependency.label not in labels:
            labels.append(dependency.label)

    def arrow_label(self, pair: Tuple[str, str]) -> str:
        """The arrow's words: the properties it stands for, then each interaction its dependencies name, as `«runs»`."""
        named = [self.arrow_labels.get(pair, '')] + [f'«{label}»' for label in self.dependency_labels.get(pair, [])]
        return ' '.join(part for part in named if part)

    def _base_names(self, oclass: OoadClass) -> List[str]:
        return list(oclass.bases)

    def _write_single_page(self, mxfile: ET.Element) -> None:
        graph = _add_diagram_page(mxfile, 'CleanEngineering Model', 'CleanEngineering-model')
        page = _ClassDiagramPage(self, set(self.classes_by_cell), None, [])
        previous = self.channel.kept_previous()
        drawn = DrawioPage.whole(previous) if previous else None
        positions = drawn.positions() if drawn is not None else {}
        previous_edges = drawn.edges_by_ends() if drawn is not None else {}
        page.write(graph, positions, previous_edges)

    def _write_module_page(self, mxfile: ET.Element, module: Module) -> None:
        page_name = module.name.strip()
        graph = _add_diagram_page(mxfile, page_name, f'page-{_cell_slug(page_name)}')
        local_ids = {self.cell_ids[id(oclass)] for oclass in module.classes}
        import_ids = self._direct_import_ids(local_ids, module_tab_label(page_name))
        _ClassDiagramPage(self, local_ids | set(import_ids), local_ids, import_ids).write(graph, {}, {})

    def _direct_import_ids(self, local_ids: set[str], local_label: str) -> List[str]:
        """Foreign class ids with a direct link from this module's page.

        Imports are the targets of edges that leave a local class, and foreign subtypes that inherit into a local base.
        Inbound association sources stay on the other module's page."""
        imports: set[str] = set()
        for source, target, kind in self.relationships:
            if source in local_ids and target not in local_ids and self.module_labels.get(target, '') != local_label:
                imports.add(target)
            elif self._is_inbound_inheritance(source, target, kind, local_ids) and self.module_labels.get(source, '') != local_label:
                imports.add(source)
        return sorted(imports)

    def _is_inbound_inheritance(self, source: str, target: str, kind: str, local_ids: set[str]) -> bool:
        return target in local_ids and source not in local_ids and (kind or 'association').lower() == 'inheritance'


class _ClassDiagramPage:
    """One page of a class diagram: which classes it shows, which of them it owns, and which it imports."""

    def __init__(self, writer: _ClassDiagramWriter, page_ids: set[str], local_ids: Optional[set[str]], import_ids: List[str]) -> None:
        self._writer = writer
        self._page_ids = page_ids
        # None on a single page, where every class is local.
        self._local_ids = local_ids
        self._import_ids = import_ids

    def write(self, graph: ET.Element, positions: Dict[str, Tuple[float, float]], previous_edges: Dict[Tuple[str, str], ET.Element]) -> None:
        """Place the cards, keeping any a person already placed, then draw arrows, keeping the routes already drawn."""
        root_el = _add_graph_root(graph)
        arrows = self._arrows()
        cards = self._cards(arrows)
        self._place_cards_keeping(cards, arrows, positions)
        for card in cards.values():
            card.append_to(root_el)
        kept_pairs = self._copy_kept_edges(root_el, previous_edges)
        new_arrows = [arrow for arrow in arrows if (arrow.source, arrow.target) not in kept_pairs]
        kept_paths = [_edge_waypoints(previous_edges[pair]) for pair in kept_pairs]
        self._draw_arrows(root_el, cards, new_arrows, kept_paths)
        graph.set('pageWidth', str(int(max((card.geometry.x + card.geometry.width for card in cards.values()), default=0) + PAGE_EDGE_ALLOWANCE)))
        graph.set('pageHeight', str(int(max((card.geometry.y + card.geometry.height for card in cards.values()), default=0) + PAGE_EDGE_ALLOWANCE)))

    def _relationships(self) -> Relationships:
        local_ids = self._local_ids
        return [
            (source, target, kind) for source, target, kind in self._writer.relationships
            if source in self._page_ids and target in self._page_ids
            and (local_ids is None or source in local_ids or (target in local_ids and (kind or '').lower() == 'inheritance'))
        ]

    def _arrows(self) -> List[DiagramArrow]:
        """One arrow per pair of classes on this page, keeping the strongest kind and naming every property it stands for."""
        arrows: Dict[Tuple[str, str], DiagramArrow] = {}
        for source, target, kind in self._relationships():
            if source == target:
                continue
            label = self._writer.arrow_label((source, target))
            arrow = arrows.setdefault((source, target), DiagramArrow(source, target, kind, label))
            if RELATIONSHIP_STRENGTH[kind] > RELATIONSHIP_STRENGTH[arrow.kind]:
                arrow.kind = kind
        drawn = {
            pair: arrow for pair, arrow in arrows.items()
            if not self._repeats_inherited_arrow(arrow, arrows) and not _is_weaker_than_opposite(pair, arrows)
        }
        return list(drawn.values()) + self._arrows_for_unlinked_classes(drawn)

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
        oclass = self._writer.classes_by_cell[cell_id]
        name = _plain_class_name(oclass.name)
        for operation in oclass.operations:
            for callee in operation.callees:
                target = self._writer.resolve_target(oclass, callee.split('.', 1)[0].strip())
                if target in self._page_ids and target != cell_id:
                    return DiagramArrow(cell_id, target, 'dependency', operation.name)
        for other_id in sorted(self._page_ids - {cell_id}):
            for operation in self._writer.classes_by_cell[other_id].operations:
                signature = operation.return_type + ' '.join(parameter.save() for parameter in operation.parameters)
                if re.search(rf'\b{re.escape(name)}\b', signature):
                    return DiagramArrow(other_id, cell_id, 'dependency', operation.name)
        return None

    def _repeats_inherited_arrow(self, arrow: DiagramArrow, arrows: Dict[Tuple[str, str], DiagramArrow]) -> bool:
        """A subclass restating its base's field says nothing a reader cannot already see on the base. A dependency is
        what the subclass itself does, so it stays."""
        if arrow.kind == 'dependency':
            return False
        return any(
            source == arrow.source and kind == 'inheritance' and (target, arrow.target) in arrows
            for source, target, kind in self._writer.relationships
        )

    def _cards(self, arrows: List[DiagramArrow]) -> Dict[str, DrawIOClass]:
        """One card per class on the page, in the model's order so the diagram reads back in that order, wide enough
        to give every arrow on it its own port."""
        cards: Dict[str, DrawIOClass] = {}
        for cell_id in (cell_id for cell_id in self._writer.classes_by_cell if cell_id in self._page_ids):
            node = self._card_node(cell_id)
            arrow_count = sum(1 for arrow in arrows if cell_id in (arrow.source, arrow.target))
            width = max(node.width(), SMALLEST_PORT_SPACING * (arrow_count + 1))
            node.cell_id = cell_id
            node.group = self._writer.module_labels.get(cell_id, '')
            node.geometry = Geometry(0, 0, width, node.height())
            cards[cell_id] = node
        return cards

    def _card_node(self, cell_id: str) -> DrawIOClass:
        writer = self._writer
        oclass = writer.classes_by_cell[cell_id]
        if cell_id in self._import_ids:
            return writer.channel.imported_class(oclass, writer.module_labels.get(cell_id, 'other'))
        node = oclass
        node.fill_color = writer.module_fills.get(writer.module_labels.get(cell_id, ''), '')
        node.owning_module = writer.module_of[id(oclass)].name.strip() if id(oclass) in writer.module_of else ''
        return node

    def _place_cards_keeping(self, cards: Dict[str, DrawIOClass], arrows: List[DiagramArrow], positions: Dict[str, Tuple[float, float]]) -> None:
        """Cards already on the page stay where a person left them. Only new ones are laid out, below the rest."""
        new_cards = [card for cell_id, card in cards.items() if cell_id not in positions]
        new_ids = {card.cell_id for card in new_cards}
        inner = [arrow for arrow in arrows if arrow.source in new_ids and arrow.target in new_ids]
        CardPlacement(new_cards, inner).place()
        for cell_id, (x, y) in positions.items():
            if cell_id in cards:
                cards[cell_id].geometry = cards[cell_id].geometry.moved_to(x, y)
        kept = [card for card in cards.values() if card.cell_id not in new_ids]
        if not kept:
            return
        bottom = max(card.geometry.y + card.geometry.height for card in kept)
        for card in new_cards:
            card.geometry = card.geometry.shifted(0, bottom)

    def _copy_kept_edges(self, root_el: ET.Element, previous_edges: Dict[Tuple[str, str], ET.Element]) -> set:
        kept_pairs: set[Tuple[str, str]] = set()
        for source, target, _kind in self._writer.relationships:
            existing = previous_edges.get((source, target))
            if existing is None:
                continue
            root_el.append(copy.deepcopy(existing))
            kept_pairs.add((source, target))
        return kept_pairs

    def _draw_arrows(self, root_el: ET.Element, cards: Dict[str, DrawIOClass], arrows: List[DiagramArrow], kept_paths: List[List[Tuple[int, int]]]) -> None:
        routed = ArrowRouter(list(cards.values()), arrows, kept_paths=kept_paths).route()
        used_ids = [int(cell.get('id')) for cell in root_el.iter('mxCell') if (cell.get('id') or '').isdigit()]
        first_id = max(used_ids, default=len(cards) + 10) + 1
        for offset, arrow in enumerate(routed):
            _append_edge(root_el, arrow, cards, str(first_id + offset))


def _is_weaker_than_opposite(pair: Tuple[str, str], arrows: Dict[Tuple[str, str], DiagramArrow]) -> bool:
    """A field drawn both ways keeps the stronger end. A dependency says what one class does to the other, so it stays."""
    if arrows[pair].kind == 'dependency':
        return False
    opposite = arrows.get((pair[1], pair[0]))
    return opposite is not None and RELATIONSHIP_STRENGTH[opposite.kind] > RELATIONSHIP_STRENGTH[arrows[pair].kind]


def _append_edge(root_el: ET.Element, arrow: DiagramArrow, cards: Dict[str, DrawIOClass], edge_id: str) -> ET.Element:
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


def arrow_style(base_style: str, arrow: DiagramArrow, cards: Dict[str, DrawIOClass]) -> str:
    """The arrow's style plus its exit and entry points, as fractions of each card, so Draw.io keeps both ends put."""
    source, target = cards[arrow.source].geometry, cards[arrow.target].geometry
    exit_x = round((arrow.exit_point[0] - source.x) / source.width, 4)
    exit_y = round((arrow.exit_point[1] - source.y) / source.height, 4)
    entry_x = round((arrow.entry_point[0] - target.x) / target.width, 4)
    entry_y = round((arrow.entry_point[1] - target.y) / target.height, 4)
    return (
        f'{base_style}exitX={exit_x};exitY={exit_y};exitDx=0;exitDy=0;exitPerimeter=0;'
        f'entryX={entry_x};entryY={entry_y};entryDx=0;entryDy=0;entryPerimeter=0;'
    )


def _add_diagram_page(mxfile: ET.Element, page_name: str, page_id: str) -> ET.Element:
    """A new diagram page; returns its mxGraphModel."""
    diagram = ET.SubElement(mxfile, 'diagram')
    diagram.set('name', page_name)
    diagram.set('id', page_id)
    graph = ET.SubElement(diagram, 'mxGraphModel')
    _set_graph_attrs(graph, CLASS_PAGE_WIDTH, CLASS_PAGE_HEIGHT)
    return graph


def _set_graph_attrs(graph: ET.Element, page_width: int, page_height: int) -> None:
    for k, v in [('dx', '1200'), ('dy', '800'), ('grid', '1'), ('gridSize', '10'), ('guides', '1'), ('tooltips', '1'), ('connect', '1'), ('arrows', '1'), ('fold', '1'), ('page', '1'), ('pageScale', '1'), ('pageWidth', str(page_width)), ('pageHeight', str(page_height)), ('math', '0'), ('shadow', '0')]:
        graph.set(k, v)


def _add_graph_root(graph: ET.Element) -> ET.Element:
    root_el = ET.SubElement(graph, 'root')
    ET.SubElement(root_el, 'mxCell', attrib={'id': '0'})
    ET.SubElement(root_el, 'mxCell', attrib={'id': '1', 'parent': '0'})
    return root_el


def _looks_like_modules_diagram(mxcells: List[ET.Element]) -> bool:
    kinds = [_vertex_diagram_kind(cell) for cell in mxcells]
    module_cells, class_cells = kinds.count('module'), kinds.count('class')
    return bool(module_cells) and (not class_cells or module_cells > class_cells)


def _vertex_diagram_kind(cell: ET.Element) -> Optional[str]:
    if cell.get('vertex') != '1':
        return None
    style = cell.get('style', '')
    value = cell.get('value', '')
    if 'text;' in style or style.startswith('text;'):
        return None
    if _is_module_style(style):
        return 'module'
    name, _stereotypes, props, ops = _class_card_members(value)
    if name and (props or ops or 'hr size=' in value.lower()):
        return 'class'
    if name and ('\u2022' in html.unescape(value) or '-' in html.unescape(value)):
        return 'module'
    return None


def _plain_class_name(name: str) -> str:
    """A card's name without bold marks or `<<Mark>>`s, as diagrams drawn by hand sometimes write it."""
    return without_marks(name.replace('*', ''))


def _is_module_style(style: str) -> bool:
    return _MODULE_MARKER in style or _MODULE_CHILD_MARKER in style


def _edge_waypoints(edge: ET.Element) -> List[Tuple[int, int]]:
    return [(int(float(point.get('x', 0))), int(float(point.get('y', 0)))) for point in edge.iter('mxPoint')]


def _class_card_members(value: str) -> Tuple[Optional[str], List[str], List[Property], List[Operation]]:
    """The class name, stereotypes, properties, and operations a UML class card shows; no name for a cell that is not
    a class card."""
    text = html.unescape(value)
    if ('\u2022' in text or '-' in text) and 'hr size="1"' not in text.lower() and ('<hr size=' not in text.lower()):
        if re.search('<i[^>]*>', text, re.IGNORECASE):
            return (None, [], [], [])
    name = class_name_in(value)
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


def _cell_slug(name: str) -> str:
    """A name as a cell id spells it: `cart-repository` for `Cart repository`, as Name spells every title."""
    return Name(name).title_slug
