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

    def height(self) -> int:
        n = min(4, len(self.properties)) + 2
        return max(CELL_MIN_HEIGHT - 10, 30 + n * LINE_HEIGHT + 2 * SECTION_PAD)

    def key_properties(self):
        return self.properties[:4]


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
