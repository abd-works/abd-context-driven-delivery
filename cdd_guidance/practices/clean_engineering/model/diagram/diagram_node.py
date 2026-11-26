"""Placed-node contract: geometry, height, keep-or-place, ordering. Channel-agnostic."""
from __future__ import annotations

from abc import ABC, abstractmethod
import re
from typing import Dict, List, Optional

from harness.graph.graph import Graph

from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    path_parent,
)
from cdd_guidance.practices.clean_engineering.model.type_refs import pascal_type_names
from cdd_guidance.practices.clean_engineering.model.diagram.class_links import ClassModelLinks, ClassPlace
from harness.whiteboard import Box
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
)

# The class name band at the top of a card, above its members.
CLASS_TITLE_HEIGHT = 30
# An imported class shows only its first few properties, under its name and the module it comes from.
IMPORTED_KEY_PROPERTIES = 4
IMPORTED_HEADER_LINES = 2
IMPORTED_HEIGHT_TRIM = 10
# Space below a module's seam list, so the last term does not touch the card's edge.
MODULE_FOOTER_PAD = 24


class DiagramNode(ABC):
    """One placed cell. HTML vs Mermaid is the channel; the box is shared.

    Card placement and arrow routing read and set `geometry`; `group` keeps cards of one module together."""

    def __init__(self, width: float = CELL_WIDTH) -> None:
        # The box starts as wide as its kind of card and as tall as what it holds; placement moves it.
        self.geometry = Box(0, 0, width, float(self.height()))
        self.cell_id = ''
        self.parent_id = '1'
        self.group = ''

    @abstractmethod
    def height(self) -> int:
        ...


# The interactions an arrow's label names after the properties it stands for, as `lines «prices»`.
_INTERACTION_WORDS = re.compile('«[^»]*»')


class DiagramClass(OoadClass, DiagramNode):
    """OoadClass on a page: name, members, height. Channel fills the label."""

    drawn_from: Optional[ClassPlace] = None
    """Where the class is described, which its card links to: its heading in the model document beside the diagram, or
    the code it was read from; none when the diagram is drawn in no folder, or the class has neither."""

    def __init__(self, name: str = '', sequential_order: int = 1, intent: str = '') -> None:
        OoadClass.__init__(self, name, sequential_order, intent)
        DiagramNode.__init__(self)
        # The properties whose written relationship no arrow on the drawing shows, because the class their type names
        # has no card: the card writes the relationship on their line, so reading the drawing brings it back.
        self.marked_on_card: set[str] = set()

    def width(self) -> int:
        """The width of the card before the arrows it carries widen it; a format whose words need more sets its own."""
        return CELL_WIDTH

    def height(self) -> int:
        member_count = len(self.properties) + len(self.operations)
        folded = sum(CLASS_TITLE_HEIGHT + (len(item.properties) + len(item.operations)) * LINE_HEIGHT + 2 * SECTION_PAD for item in self.folded)
        return max(CELL_MIN_HEIGHT, CLASS_TITLE_HEIGHT + member_count * LINE_HEIGHT + 2 * SECTION_PAD + folded)

    def property_lines(self) -> List[str]:
        """Each property as its card writes it, with the relationship written on it when no arrow can show it."""
        return [f"+ {item.marked_signature() if item.name in self.marked_on_card else item.save()}" for item in self.properties]

    def take_arrow(self, target: str, kind: str, label: str = '', unmarked: str = '') -> None:
        """An arrow of kind drawn to target is the properties its label names, of those whose type names the target; an
        arrow whose label names none of them is every property whose type names the target. A property the arrow lists
        as unmarked stays as it is: nobody wrote a relationship on it, and the arrow only shows what its type already
        says. Inheritance and a dependency stand for no property."""
        if (kind or "").lower() in {"inheritance", "dependency"}:
            return
        named = self._names_in(_INTERACTION_WORDS.sub('', label))
        reaching = [prop for prop in self.properties if target in pascal_type_names(prop.type_hint or "")]
        for prop in [prop for prop in reaching if prop.name in named] or reaching:
            if prop.name not in self._names_in(unmarked):
                prop.arrow.take_kind(kind)

    def _names_in(self, listed: str) -> List[str]:
        """The property names an arrow lists, written `lines, history`."""
        return [name.strip() for name in listed.split(',') if name.strip()]


class ImportedClass(DiagramClass):
    """Compact card for a class owned by another aggregate."""

    def __init__(self, name: str = '', sequential_order: int = 1, from_module: str = '') -> None:
        super().__init__(name, sequential_order)
        self.from_module = from_module

    def clone(self):
        cloned = super().clone()
        cloned.from_module = self.from_module
        return cloned

    def height(self) -> int:
        line_count = min(IMPORTED_KEY_PROPERTIES, len(self.properties)) + IMPORTED_HEADER_LINES
        return max(CELL_MIN_HEIGHT - IMPORTED_HEIGHT_TRIM, CLASS_TITLE_HEIGHT + line_count * LINE_HEIGHT + 2 * SECTION_PAD)

    def key_properties(self):
        return self.properties[:IMPORTED_KEY_PROPERTIES]


class DiagramModule(Module, DiagramNode):
    """Module on a page: purpose, seam, nesting, height. Channel fills the label."""

    # How many seam terms the card lists before it ends the list with `...`.
    seam_bullets = MODULE_MAX_SEAM_BULLETS
    # The box a module with nothing nested in it starts as; a format whose words take more room sets its own.
    cell_width = MODULE_CELL_WIDTH
    cell_min_height = MODULE_CELL_MIN_HEIGHT

    def __init__(self, name: str = '', sequential_order: int = 1, graph: Optional[Graph] = None) -> None:
        Module.__init__(self, name, sequential_order, graph)
        self.nested = False
        # The words written on the arrow to each dependency, by the dependency's name; most arrows carry none.
        self.dependency_labels: Dict[str, str] = {}
        DiagramNode.__init__(self, MODULE_CELL_WIDTH)

    def height(self) -> int:
        return self.header_height()

    def header_height(self) -> int:
        terms = self.public_terms()
        if not terms:
            return MODULE_HEADER_HEIGHT + MODULE_LINE_HEIGHT
        line_count = min(self.seam_bullets, len(terms))
        if len(terms) > self.seam_bullets:
            line_count += 1
        return max(MODULE_CELL_MIN_HEIGHT, MODULE_HEADER_HEIGHT + line_count * MODULE_LINE_HEIGHT + MODULE_FOOTER_PAD)

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

    def __init__(self, by_name: Dict[str, Module]) -> None:
        self.by_name = by_name
        self.children_of: Dict[str, List[str]] = {}
        self.roots: List[str] = []
        self.synthetic: set = set()
        self._depth_cache: Dict[str, int] = {}
        self._visiting: set = set()

    @classmethod
    def build(cls, modules: List[Module], synthesize_parents: bool = False) -> 'ContainmentForest':
        forest = cls({module.name: module for module in modules})
        if synthesize_parents:
            forest._synthesize_parents()
        forest._nest_by_path()
        return forest

    def _synthesize_parents(self) -> None:
        needed: List[str] = []
        for name in list(self.by_name):
            parent = path_parent(name)
            while parent:
                if parent not in self.by_name:
                    needed.append(parent)
                parent = path_parent(parent)
        for prefix in sorted(set(needed), key=lambda path: path.count('/')):
            nesting = Module(name=prefix, sequential_order=0)
            nesting.description = 'nested modules'
            self.by_name[prefix] = nesting
            self.synthetic.add(prefix)

    def _nest_by_path(self) -> None:
        self.children_of = {name: [] for name in self.by_name}
        for name in self.by_name:
            parent = path_parent(name)
            if parent and parent in self.by_name:
                self.children_of[parent].append(name)
            else:
                self.roots.append(name)
        for children in self.children_of.values():
            children.sort(key=self._model_order)
        self.roots.sort(key=self._model_order)

    def _model_order(self, name: str) -> tuple:
        return (self.by_name[name].sequential_order or 0, name)

    def in_model_order(self, names: List[str]) -> List[str]:
        """The modules named and everything nested in them, each parent before its children, in the model's order, so
        a drawing reads the modules back in the order the model lists them."""
        ordered: List[str] = []
        for name in names:
            ordered.append(name)
            ordered.extend(self.in_model_order(self.children_of.get(name, [])))
        return ordered

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

    writes_prose = False
    class_links: Optional[ClassModelLinks] = None
    """Where the class cards of a diagram written in a folder link, set when it is rendered there."""

    def load_module_cell(self, source: Module) -> DiagramModule:
        """A module of this channel's own kind for a container module the containment forest made, filled from it."""
        loaded = self.load_module(source)
        loaded.translate_from(source)
        return loaded


class ModulesView:
    """One modules view a diagram channel draws: the containment forest of the channel's modules, and the module each
    is drawn as, the channel's own or a copy of a container the forest made. Each channel's view writes it its own way."""

    def __init__(self, channel: DiagramCleanEngineeringModel) -> None:
        self._channel = channel
        self._forest = ContainmentForest.build(list(channel.modules), synthesize_parents=True)
        self._cells: Dict[str, DiagramModule] = {
            name: module if isinstance(module, DiagramModule) else channel.load_module_cell(module)
            for name, module in self._forest.by_name.items()
        }
