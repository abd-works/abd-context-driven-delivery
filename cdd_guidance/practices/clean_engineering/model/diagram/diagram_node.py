"""Placed-node contract: geometry, height, keep-or-place, ordering. Channel-agnostic."""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
)
from practices.clean_engineering.model.diagram.geometry import (
    CELL_MIN_HEIGHT,
    CELL_WIDTH,
    LINE_HEIGHT,
    MODULE_CELL_MIN_HEIGHT,
    MODULE_CELL_WIDTH,
    MODULE_HEADER_HEIGHT,
    MODULE_LINE_HEIGHT,
    MODULE_MAX_SEAM_BULLETS,
    MODULE_PURPOSE_MAX_CHARS,
    SECTION_PAD,
    Geometry,
)


class DiagramNode(ABC):
    """One placed cell. HTML vs Mermaid is the channel; the box is shared."""

    def __init__(self) -> None:
        self.geometry = Geometry(0, 0, CELL_WIDTH, CELL_MIN_HEIGHT)
        self.cell_id = ''
        self.parent_id = '1'
        self._previous_boxes: Dict[str, Tuple[float, float, float, float]] = {}

    @abstractmethod
    def height(self) -> int:
        ...

    def keep_or_place(self, default: Geometry) -> Geometry:
        saved = self._previous_boxes.get(self.cell_id)
        if saved is None:
            return default
        return Geometry(saved[0], saved[1], saved[2], saved[3])

    def overlaps(self, other: "DiagramNode") -> bool:
        return self.geometry.overlaps(other.geometry)

    def draw(self, page) -> object:
        self.geometry = self.keep_or_place(self.geometry)
        return page.place(self)


class DiagramClass(OoadClass, DiagramNode):
    """OoadClass on a page: name, members, height. Channel fills the label."""

    def __init__(self, name: str = '', sequential_order: int = 1, **kwargs) -> None:
        OoadClass.__init__(self, name, sequential_order, **kwargs)
        DiagramNode.__init__(self)
        self.geometry = Geometry(0, 0, CELL_WIDTH, float(self.height()))

    def height(self) -> int:
        n_content = len(self.properties) + len(self.operations)
        return max(CELL_MIN_HEIGHT, 30 + n_content * LINE_HEIGHT + 2 * SECTION_PAD)

    def display_name(self) -> str:
        n = re.sub('\\*+', '', self.name)
        n = re.sub('<<[^>]+>>', '', n)
        n = re.sub('\\s+extends\\s+.+$', '', n, flags=re.IGNORECASE)
        return n.strip()

    def tactical_stereotypes(self) -> list[str]:
        n = re.sub('\\*+', '', self.name)
        return [s.strip() for s in re.findall('<<[^>]+>>', n)]

    def place_below(self, base: "DiagramClass") -> None:
        siblings = [
            node for node in getattr(base, "_row", []) if isinstance(node, DiagramClass)
        ]
        if self not in siblings:
            siblings.append(self)
        base._row = siblings
        gap = 28.0
        self.geometry = Geometry(
            base.geometry.x + (len(siblings) - 1) * (CELL_WIDTH + gap),
            base.geometry.y + base.geometry.height + gap,
            float(CELL_WIDTH),
            float(self.height()),
        )

    def extends_base_name(self) -> Optional[str]:
        n = re.sub('\\*+', '', self.name)
        n = re.sub('<<[^>]+>>', '', n)
        m = re.search('\\bextends\\s+([A-Z]\\w*)', n, flags=re.IGNORECASE)
        return m.group(1) if m else None


class ImportedClass(DiagramClass):
    """Compact card for a class owned by another aggregate."""

    def __init__(
        self,
        name: str = '',
        sequential_order: int = 1,
        from_module: str = '',
        **kwargs,
    ) -> None:
        super().__init__(name, sequential_order, **kwargs)
        self.from_module = from_module

    def clone(self):
        cloned = super().clone()
        cloned.from_module = self.from_module
        return cloned

    def height(self) -> int:
        n = min(4, len(self.properties)) + 2
        return max(CELL_MIN_HEIGHT - 10, 30 + n * LINE_HEIGHT + 2 * SECTION_PAD)

    def key_properties(self):
        return self.properties[:4]

    def place_above(self) -> None:
        self.geometry = Geometry(self.geometry.x, 40.0, self.geometry.width, float(self.height()))

    def place_beside(self, local: DiagramClass) -> None:
        self.geometry = Geometry(
            local.geometry.x + local.geometry.width + 48.0,
            local.geometry.y,
            self.geometry.width or float(CELL_WIDTH),
            float(self.height()),
        )


class DiagramModule(Module, DiagramNode):
    """Module on a page: purpose, seam, nesting, height. Channel fills the label."""

    def __init__(self, name: str = '', sequential_order: int = 1, **kwargs) -> None:
        Module.__init__(self, name, sequential_order, **kwargs)
        DiagramNode.__init__(self)
        self.children: List['DiagramModule'] = []
        self.nested = False
        self.geometry = Geometry(0, 0, MODULE_CELL_WIDTH, float(self.height()))

    def load_class(self, source: OoadClass) -> DiagramClass:
        loaded = DiagramClass(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        return loaded

    def height(self) -> int:
        return self.header_height()

    def header_height(self) -> int:
        terms = self.public_terms()
        if not terms:
            return MODULE_HEADER_HEIGHT + MODULE_LINE_HEIGHT
        n = min(MODULE_MAX_SEAM_BULLETS, len(terms))
        if len(terms) > MODULE_MAX_SEAM_BULLETS:
            n += 1
        return max(MODULE_CELL_MIN_HEIGHT, MODULE_HEADER_HEIGHT + n * MODULE_LINE_HEIGHT + 24)

    def external_deps(self) -> List[str]:
        parent = path_parent(self.name)
        return [d for d in self.dependencies if d != parent]

    def purpose_line(self) -> str:
        purpose = self.description.strip() or '{one-line purpose}'
        purpose_line = purpose.splitlines()[0].strip()
        if len(purpose_line) > MODULE_PURPOSE_MAX_CHARS:
            purpose_line = purpose_line[:MODULE_PURPOSE_MAX_CHARS - 1].rstrip() + '...'
        return purpose_line

    def size(self) -> Geometry:
        kids = [child for child in self.modules if isinstance(child, DiagramNode)]
        if not kids:
            return Geometry(self.geometry.x, self.geometry.y, float(MODULE_CELL_WIDTH), float(self.height()))
        widths = [child.size().width for child in kids]
        heights = [child.size().height for child in kids]
        cols = min(2, len(kids))
        rows = (len(kids) + cols - 1) // cols
        col_widths = [0.0] * cols
        row_heights = [0.0] * rows
        for index, child in enumerate(kids):
            column, row = index % cols, index // cols
            col_widths[column] = max(col_widths[column], widths[index])
            row_heights[row] = max(row_heights[row], heights[index])
        gap = 12.0
        grid_w = sum(col_widths) + gap * (cols - 1)
        grid_h = sum(row_heights) + gap * (rows - 1)
        width = max(float(MODULE_CELL_WIDTH), grid_w + 32)
        height = float(self.header_height()) + grid_h + 24
        return Geometry(self.geometry.x, self.geometry.y, width, height)

    def place_children(self) -> None:
        kids = [child for child in self.modules if isinstance(child, DiagramModule)]
        if not kids:
            self.geometry = self.size()
            return
        cols = min(2, len(kids))
        sizes = [child.size() for child in kids]
        col_widths = [0.0] * cols
        rows = (len(kids) + cols - 1) // cols
        row_heights = [0.0] * rows
        for index, box in enumerate(sizes):
            column, row = index % cols, index // cols
            col_widths[column] = max(col_widths[column], box.width)
            row_heights[row] = max(row_heights[row], box.height)
        gap = 12.0
        pad_x = 16.0
        pad_y = 12.0
        for index, child in enumerate(kids):
            column, row = index % cols, index // cols
            child.geometry = Geometry(
                pad_x + sum(col_widths[:column]) + gap * column,
                float(self.header_height()) + pad_y + sum(row_heights[:row]) + gap * row,
                sizes[index].width,
                sizes[index].height,
            )
            child.place_children()
        self.geometry = self.size()

    def shown_seam_terms(self) -> List[str]:
        terms = self.public_terms()
        shown = terms[:MODULE_MAX_SEAM_BULLETS]
        if len(terms) > MODULE_MAX_SEAM_BULLETS:
            return shown + ['...']
        return shown


def path_parent(name: str) -> Optional[str]:
    if '/' not in name:
        return None
    return name.rsplit('/', 1)[0]


def module_tab_label(module_name: str) -> str:
    name = module_name.strip()
    for sep in (' — ', ' – ', ' - ', '—', '–'):
        if sep in name:
            return name.split(sep, 1)[0].strip()
    return name


def is_modules_view(canonical: CleanEngineeringModel) -> bool:
    if not canonical.modules:
        return False
    for oclass in canonical.classes:
        if oclass.properties or oclass.operations:
            return False
        if any(r.kind for r in oclass.relationships):
            return False
    if any(m.dependencies or m.seam_terms for m in canonical.modules):
        return True
    if not canonical.classes:
        return True
    return all(
        (not c.properties and not c.operations and not c.relationships)
        for c in canonical.classes
    )


class ContainmentForest:
    """Path nesting and dependency depth for module ordering. Shared by both channels."""

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
        self._depth_cache: Dict[str, int] = {}
        self._visiting: set = set()

    @classmethod
    def build(cls, modules: List[Module], synthesize_parents: bool = False) -> 'ContainmentForest':
        by_name: Dict[str, Module] = {m.name: m for m in modules}
        synthetic: set = set()
        if synthesize_parents:
            synthetic = cls._synthesize_parents(by_name)
        children_of: Dict[str, List[str]] = {n: [] for n in by_name}
        roots: List[str] = []
        for name in by_name:
            parent = path_parent(name)
            if parent and parent in by_name:
                children_of[parent].append(name)
            else:
                roots.append(name)
        for parent in children_of:
            children_of[parent].sort(key=lambda n: (by_name[n].sequential_order or 0, n))
        roots.sort(key=lambda n: (by_name[n].sequential_order or 0, n))
        return cls(by_name, children_of, roots, synthetic)

    @classmethod
    def _synthesize_parents(cls, by_name: Dict[str, Module]) -> set:
        synthetic: set = set()
        needed: List[str] = []
        for name in list(by_name):
            p = path_parent(name)
            while p:
                if p not in by_name:
                    needed.append(p)
                p = path_parent(p)
        for prefix in sorted(set(needed), key=lambda s: s.count('/')):
            by_name[prefix] = Module(
                name=prefix, sequential_order=0, description='nested modules', seam_terms=[]
            )
            synthetic.add(prefix)
        return synthetic

    def module_dep_depth(self, name: str) -> int:
        if name in self._depth_cache:
            return self._depth_cache[name]
        if name in self._visiting:
            self._depth_cache[name] = 0
            return 0
        self._visiting.add(name)
        root_deps = [self._root_of(dep) for dep in self._dep_names_for(name)]
        depths = [self.module_dep_depth(dep) for dep in root_deps if dep and dep != name]
        self._visiting.discard(name)
        d = 0 if not depths else 1 + max(depths)
        self._depth_cache[name] = d
        return d

    def _dep_names_for(self, name: str) -> List[str]:
        module = self.by_name[name]
        node = DiagramModule(
            name=module.name,
            sequential_order=module.sequential_order,
            dependencies=list(module.dependencies),
        )
        dep_names = list(node.external_deps())
        if name in self.synthetic or (
            self.children_of.get(name)
            and not module.public_terms()
            and not module.dependencies
        ):
            for child in self.children_of.get(name, []):
                nested = self.by_name[child]
                dep_names.extend(
                    DiagramModule(
                        name=nested.name,
                        sequential_order=nested.sequential_order,
                        dependencies=list(nested.dependencies),
                    ).external_deps()
                )
        return dep_names

    def _root_of(self, dep: str) -> Optional[str]:
        if dep not in self.by_name:
            return None
        cur = dep
        while True:
            parent = path_parent(cur)
            if not parent or parent not in self.by_name:
                break
            cur = parent
        if cur in self.roots:
            return cur
        return None


class DiagramCleanEngineeringModel(CleanEngineeringModel):
    """Shared diagram channel. Draw.io and Miro extend this model."""

    module_type = DiagramModule

    def place_modules(self) -> None:
        forest = ContainmentForest.build(self.modules, synthesize_parents=True)
        x = 40.0
        depths = sorted({forest.module_dep_depth(name) for name in forest.roots})
        for depth in depths:
            y = 100.0
            column_width = 0.0
            for name in forest.roots:
                if forest.module_dep_depth(name) != depth:
                    continue
                module = forest.by_name[name]
                if not isinstance(module, DiagramModule):
                    continue
                module.place_children()
                box = module.size()
                module.geometry = Geometry(x, y, box.width, box.height)
                y += box.height + 32.0
                column_width = max(column_width, box.width)
            x += column_width + 48.0

    def place_classes(self) -> None:
        for module in self.modules:
            if isinstance(module, DiagramModule):
                self._place_module_classes(module)

    def _place_module_classes(self, module: DiagramModule) -> None:
        by_name = {
            oclass.display_name(): oclass
            for oclass in module.classes
            if isinstance(oclass, DiagramClass)
        }
        cursor_x = module.geometry.x
        cursor_y = module.geometry.y + module.geometry.height + 48.0
        for oclass in module.classes:
            if not isinstance(oclass, DiagramClass):
                continue
            base_name = oclass.extends_base_name()
            base = by_name.get(base_name) if base_name else None
            if isinstance(base, DiagramClass):
                oclass.place_below(base)
                continue
            if isinstance(oclass, ImportedClass):
                oclass.place_above()
                continue
            oclass.geometry = Geometry(cursor_x, cursor_y, float(CELL_WIDTH), float(oclass.height()))
            cursor_x += CELL_WIDTH + 28.0
