"""Placed-node contract: geometry, height, keep-or-place, ordering. Channel-agnostic."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    path_parent,
)
from cdd_guidance.practices.clean_engineering.model.diagram.geometry import (
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
    """One placed cell. HTML vs Mermaid is the channel; the box is shared.

    Card placement and arrow routing read and set `geometry`; `group` keeps cards of one module together."""

    def __init__(self, width: float = CELL_WIDTH) -> None:
        # The box starts as wide as its kind of card and as tall as what it holds; placement moves it.
        self.geometry = Geometry(0, 0, width, float(self.height()))
        self.cell_id = ''
        self.parent_id = '1'
        self.group = ''

    @abstractmethod
    def height(self) -> int:
        ...


class DiagramClass(OoadClass, DiagramNode):
    """OoadClass on a page: name, members, height. Channel fills the label."""

    def __init__(self, name: str = '', sequential_order: int = 1, **kwargs) -> None:
        OoadClass.__init__(self, name, sequential_order, **kwargs)
        DiagramNode.__init__(self)

    def height(self) -> int:
        n_content = len(self.properties) + len(self.operations)
        return max(CELL_MIN_HEIGHT, 30 + n_content * LINE_HEIGHT + 2 * SECTION_PAD)


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


class DiagramModule(Module, DiagramNode):
    """Module on a page: purpose, seam, nesting, height. Channel fills the label."""

    # How many seam terms the card lists before it ends the list with `...`.
    seam_bullets = MODULE_MAX_SEAM_BULLETS

    def __init__(self, name: str = '', sequential_order: int = 1, **kwargs) -> None:
        Module.__init__(self, name, sequential_order, **kwargs)
        self.nested = False
        DiagramNode.__init__(self, MODULE_CELL_WIDTH)

    def height(self) -> int:
        return self.header_height()

    def header_height(self) -> int:
        terms = self.public_terms()
        if not terms:
            return MODULE_HEADER_HEIGHT + MODULE_LINE_HEIGHT
        n = min(self.seam_bullets, len(terms))
        if len(terms) > self.seam_bullets:
            n += 1
        return max(MODULE_CELL_MIN_HEIGHT, MODULE_HEADER_HEIGHT + n * MODULE_LINE_HEIGHT + 24)

    def purpose_line(self) -> str:
        purpose = self.description.strip() or '{one-line purpose}'
        purpose_line = purpose.splitlines()[0].strip()
        if len(purpose_line) > MODULE_PURPOSE_MAX_CHARS:
            purpose_line = purpose_line[:MODULE_PURPOSE_MAX_CHARS - 1].rstrip() + '...'
        return purpose_line

    def shown_seam_terms(self) -> List[str]:
        terms = self.public_terms()
        shown = terms[:self.seam_bullets]
        if len(terms) > self.seam_bullets:
            return shown + ['...']
        return shown


def module_tab_label(module_name: str) -> str:
    name = module_name.strip()
    for sep in (' — ', ' – ', ' - ', '—', '–'):
        if sep in name:
            return name.split(sep, 1)[0].strip()
    return name


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
        dep_names = list(module.external_deps())
        if name in self.synthetic or (
            self.children_of.get(name)
            and not module.public_terms()
            and not module.dependencies
        ):
            for child in self.children_of.get(name, []):
                dep_names.extend(self.by_name[child].external_deps())
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
    """Shared diagram channel. Draw.io extends this model."""
