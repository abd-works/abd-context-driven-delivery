"""The class view every diagram format draws: which classes go on which page, the arrows between them, and where
each card stands. A format writes the cards and arrows in its own way; what it draws is decided here once.

A model of more than CLASSES_ON_ONE_PAGE classes in two or more modules draws one page per module, with a dashed card
for each class of another module that a class on the page reaches. One arrow joins each pair of classes, of the
strongest kind between them, naming every property it stands for.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from harness.annotations.name import Name

from cdd_guidance.practices.clean_engineering.model.base_class_model import Module, OoadClass
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import without_marks
from cdd_guidance.practices.clean_engineering.model.diagram.class_layout import (
    GROUP_FILL_COLORS,
    SMALLEST_PORT_SPACING,
    CardPlacement,
    DiagramArrow,
)
from cdd_guidance.practices.clean_engineering.model.diagram.diagram_node import (
    DiagramClass,
    DiagramCleanEngineeringModel,
    module_tab_label,
)
from harness.whiteboard import Box
from cdd_guidance.practices.clean_engineering.model.field_types import RELATIONSHIP_STRENGTH, Relationship
from cdd_guidance.practices.clean_engineering.model.property import Property

CLASSES_ON_ONE_PAGE = 40
# The interaction a dependency names, written on its arrow as `«runs»` on `Repo ---<<runs>>--> Git`.
DEPENDENCY_LABEL = re.compile("«([^»]+)»")

Relationships = List[Tuple[str, str, str]]


class ClassView:
    """What one class view draws, in any diagram format: a single page, or one page per module when the model is large.

    Holds what every page needs: a cell id per class, the relationships between those ids, and each class's module."""

    def __init__(self, channel: DiagramCleanEngineeringModel) -> None:
        self.channel = channel
        self.classes = [oclass for module in channel.modules for oclass in module.classes]
        self._assign_cell_ids()
        self._collect_relationships()
        self.module_labels = {
            self.cell_ids[id(oclass)]: module_tab_label(module.name) for module in channel.modules for oclass in module.classes
        }
        self.named_modules = [module for module in channel.modules if module.classes]
        self.module_fills = self._module_fill_colors()
        # Each page of the diagram this render replaces, by name, when it keeps positions: a module page keeps the cards
        # and arrows of the page with its name.
        self.previous_pages = self._previous_pages()

    @property
    def on_one_page(self) -> bool:
        """True when every class fits one page: one module, or no more than CLASSES_ON_ONE_PAGE classes."""
        return len(self.named_modules) < 2 or len(self.classes) <= CLASSES_ON_ONE_PAGE

    def module_page_ids(self, module: Module) -> Tuple[set[str], List[str]]:
        """The ids of the classes a module's own page holds, and of the classes of other modules it shows dashed."""
        local_ids = {self.cell_ids[id(oclass)] for oclass in module.classes}
        return local_ids, self._direct_import_ids(local_ids, module_tab_label(module.name.strip()))

    def _previous_pages(self) -> Dict[str, object]:
        """The pages of the drawing this render replaces, by name, in the format's own form; none by default."""
        return {}

    def resolve_target(self, source: OoadClass, target_name: str) -> Optional[str]:
        """The cell id of the class target_name names, preferring one in source's own module."""
        module = self.module_of.get(id(source))
        if module is not None:
            for oclass in module.classes:
                names = {oclass.name, plain_class_name(oclass.name), *(item.name for item in oclass.folded)}
                if target_name in names:
                    return self.cell_ids[id(oclass)]
        ids = self._cell_ids_by_name.get(target_name) or []
        return ids[0] if ids else None

    def _assign_cell_ids(self) -> None:
        """One cell id per class. The same name in two modules is two boxes."""
        self.cell_ids: dict[int, str] = {}
        self.classes_by_cell: dict[str, OoadClass] = {}
        self.module_of: dict[int, Module] = {}
        self._cell_ids_by_name: dict[str, list[str]] = {}
        for module in self.channel.modules:
            for oclass in module.classes:
                cell_id = f"{cell_slug(module.name)}--{cell_slug(oclass.name)}"
                if cell_id in self.classes_by_cell:
                    cell_id = f"{cell_id}-{oclass.sequential_order}"
                self.cell_ids[id(oclass)] = cell_id
                self.classes_by_cell[cell_id] = oclass
                self.module_of[id(oclass)] = module
                self._cell_ids_by_name.setdefault(oclass.name, []).append(cell_id)
                plain = plain_class_name(oclass.name)
                if plain and plain != oclass.name:
                    self._cell_ids_by_name.setdefault(plain, []).append(cell_id)
                # A class folded into this one has no card of its own, so an arrow to it lands on this card.
                for folded in oclass.folded:
                    self._cell_ids_by_name.setdefault(folded.name, []).append(cell_id)

    def _module_fill_colors(self) -> Dict[str, str]:
        """One colour per module, so a reader sees where a class lives. One module needs no colour."""
        if len(self.named_modules) < 2:
            return {}
        return {
            module_tab_label(module.name): GROUP_FILL_COLORS[index % len(GROUP_FILL_COLORS)]
            for index, module in enumerate(self.named_modules)
        }

    def _collect_relationships(self) -> None:
        """The arrows between the classes' cells, with the words each carries."""
        self.arrow_labels: Dict[Tuple[str, str], str] = {}
        # The properties each pair's arrow stands for that carry no written relationship: their type alone draws it.
        self.unmarked_properties: Dict[Tuple[str, str], List[str]] = {}
        # The interactions each pair's dependencies name, in model order: `stops`, `reads sections with`.
        self.dependency_labels: Dict[Tuple[str, str], List[str]] = {}
        self.relationships: Relationships = []
        for oclass in self.classes:
            source = self.cell_ids.get(id(oclass))
            if not source:
                continue
            for prop in oclass.properties:
                self._collect_property_relationship(oclass, prop)
            for dependency in oclass.dependencies:
                self._collect_dependency(oclass, dependency)
            for base in self._base_names(oclass):
                target = self.resolve_target(oclass, base)
                if target and (source, target, 'inheritance') not in self.relationships:
                    self.relationships.append((source, target, 'inheritance'))

    def _collect_property_relationship(self, oclass: OoadClass, prop: Property) -> None:
        relationship = getattr(prop, 'relationship', None)
        target = self.resolve_target(oclass, relationship.target) if relationship is not None else None
        if not target:
            if prop.stereotype:
                oclass.marked_on_card.add(prop.name)
            return
        source = self.cell_ids[id(oclass)]
        self.relationships.append((source, target, relationship.kind or 'association'))
        named = self.arrow_labels.get((source, target))
        self.arrow_labels[(source, target)] = f'{named}, {prop.name}' if named else prop.name
        if not prop.stereotype:
            self.unmarked_properties.setdefault((source, target), []).append(prop.name)

    def _collect_dependency(self, oclass: OoadClass, dependency: Relationship) -> None:
        source = self.cell_ids[id(oclass)]
        target = self.resolve_target(oclass, dependency.target)
        if not target or target == source:
            return
        if (source, target, 'dependency') not in self.relationships:
            self.relationships.append((source, target, 'dependency'))
        labels = self.dependency_labels.setdefault((source, target), [])
        if dependency.label and dependency.label not in labels:
            labels.append(dependency.label)

    def arrow_label(self, pair: Tuple[str, str]) -> str:
        """The arrow's words: the properties it stands for, then each interaction its dependencies name, as `«runs»`."""
        named = [self.arrow_labels.get(pair, '')] + [f'«{label}»' for label in self.dependency_labels.get(pair, [])]
        return ' '.join(part for part in named if part)

    def _base_names(self, oclass: OoadClass) -> List[str]:
        return list(oclass.bases)

    def _direct_import_ids(self, local_ids: set[str], local_label: str) -> List[str]:
        """Foreign class ids with a direct link from this module's page.

        Imports are the targets of edges that leave a local class, and foreign subtypes that inherit into a local base.
        Inbound association sources stay on the other module's page."""
        imports: set[str] = set()
        for source, target, kind in self.relationships:
            inbound_inheritance = target in local_ids and source not in local_ids and (kind or 'association').lower() == 'inheritance'
            if source in local_ids and target not in local_ids and self.module_labels.get(target, '') != local_label:
                imports.add(target)
            elif inbound_inheritance and self.module_labels.get(source, '') != local_label:
                imports.add(source)
        return sorted(imports)



class ClassViewPage:
    """One page of a class diagram: which classes it shows, which of them it owns, and which it imports."""

    def __init__(self, writer: ClassView, module: Optional[Module] = None) -> None:
        """The page of module's classes, with the classes of other modules it uses shown dashed; with no module, the
        single page that shows every class."""
        self._writer = writer
        # None on a single page, where every class is local.
        self._local_ids: Optional[set[str]] = None
        self._import_ids: List[str] = []
        if module is None:
            self._page_ids = set(writer.classes_by_cell)
            return
        self._local_ids, self._import_ids = writer.module_page_ids(module)
        self._page_ids = self._local_ids | set(self._import_ids)

    def is_imported(self, cell_id: str) -> bool:
        """True for the dashed card of a class another module's page owns."""
        return cell_id in self._import_ids

    def laid_out(self, positions: Dict[str, Tuple[float, float]]) -> Tuple[Dict[str, DiagramClass], List[DiagramArrow]]:
        """The page's cards, each placed, keeping those already placed at positions, and the arrows between them, not
        yet routed."""
        arrows = self._arrows()
        cards = self._cards(arrows)
        self._place_cards_keeping(cards, arrows, positions)
        return cards, arrows

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
            if not self._repeats_inherited_arrow(arrow, arrows) and not is_weaker_than_opposite(pair, arrows)
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
        name = plain_class_name(oclass.name)
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

    def _cards(self, arrows: List[DiagramArrow]) -> Dict[str, DiagramClass]:
        """One card per class on the page, in the model's order so the diagram reads back in that order, wide enough
        to give every arrow on it its own port."""
        cards: Dict[str, DiagramClass] = {}
        for cell_id in (cell_id for cell_id in self._writer.classes_by_cell if cell_id in self._page_ids):
            node = self._card_node(cell_id)
            arrow_count = sum(1 for arrow in arrows if cell_id in (arrow.source, arrow.target))
            width = max(node.width(), SMALLEST_PORT_SPACING * (arrow_count + 1))
            node.cell_id = cell_id
            node.group = self._writer.module_labels.get(cell_id, '')
            node.geometry = Box(0, 0, width, node.height())
            cards[cell_id] = node
        return cards

    def _card_node(self, cell_id: str) -> DiagramClass:
        writer = self._writer
        oclass = writer.classes_by_cell[cell_id]
        if cell_id in self._import_ids:
            return writer.channel.imported_class(oclass, writer.module_labels.get(cell_id, 'other'))
        node = oclass
        node.fill_color = writer.module_fills.get(writer.module_labels.get(cell_id, ''), '')
        node.owning_module = writer.module_of[id(oclass)].name.strip() if id(oclass) in writer.module_of else ''
        return node

    def _place_cards_keeping(self, cards: Dict[str, DiagramClass], arrows: List[DiagramArrow], positions: Dict[str, Tuple[float, float]]) -> None:
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
        bottom = max(card.geometry.y + card.geometry.h for card in kept)
        for card in new_cards:
            card.geometry = card.geometry.shifted(0, bottom)



def is_weaker_than_opposite(pair: Tuple[str, str], arrows: Dict[Tuple[str, str], DiagramArrow]) -> bool:
    """A field drawn both ways keeps the stronger end. A dependency says what one class does to the other, so it stays."""
    if arrows[pair].kind == 'dependency':
        return False
    opposite = arrows.get((pair[1], pair[0]))
    return opposite is not None and RELATIONSHIP_STRENGTH[opposite.kind] > RELATIONSHIP_STRENGTH[arrows[pair].kind]


def plain_class_name(name: str) -> str:
    """A card's name without bold marks or `<<Mark>>`s, as diagrams drawn by hand sometimes write it."""
    return without_marks(name.replace('*', ''))


def cell_slug(name: str) -> str:
    """A name as a cell id spells it: `cart-repository` for `Cart repository`, as Name spells every title."""
    return Name(name).title_slug
