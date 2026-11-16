"""Claude Whiteboard channel for Clean Engineering: the modules view and the class view drawn on a board, and read back.

A modules view draws each module as a box with its purpose and seam terms, and each dependency as an arrow. A class view
draws each module as a section holding its class cards, each base as an arrow labelled ``extends``, each relationship a
property stands for as an arrow labelled with its kind, and each dependency as an arrow labelled ``<<label>>``. Like the
drawio channel, it extends the channel-agnostic diagram nodes; only the elements it writes are its own.

Element ids name what an element draws (``module.``, ``section.``, ``class.``, ``extends.``, ``has.``, ``uses.``,
``needs.``) and a key of the node's name, so the same module or class keeps its id from one render to the next.
"""

from __future__ import annotations

import hashlib
import re
from typing import Dict, List, Optional, Tuple

from harness.whiteboard import Arrow, BoardElement, Section, Shape, UnreadableBoard, Whiteboard, WhiteboardNode

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.diagram.geometry import Geometry
from cdd_guidance.practices.clean_engineering.model.diagram.diagram_node import (
    DiagramClass,
    DiagramCleanEngineeringModel,
    DiagramModule,
)
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property

RULE = "---"
COLUMNS = 3
GAP = 64
SECTION_INSET = 24
SECTION_TITLE_ROOM = 52
_BOLD = re.compile(r"^\*\*(.+)\*\*$")
_ITALIC = re.compile(r"^\*(.+)\*$")
_MARK = re.compile(r"«([^»]+)»")
_DEPENDENCY_LABEL = re.compile(r"^<<(.+)>>$")


LINE_ROOM = 21
"""The height one line of small text takes on a board, with room to spare: a board grows a block too small for its
words over its neighbours."""
LETTER_ROOM = 7.5
TEXT_PAD = 24
MIN_WIDTH = 200


def _key(*names: str) -> str:
    return hashlib.sha1("/".join(names).encode("utf-8")).hexdigest()[:12]


class _SizedByText(WhiteboardNode):
    """A node whose box is as big as the words it shows, sized from them before the diagram places it."""

    @property
    def shown_text(self) -> str:
        raise NotImplementedError

    def board_size(self) -> Tuple[float, float]:
        lines = self.shown_text.splitlines() or [""]
        width = max(MIN_WIDTH, max(len(line) for line in lines) * LETTER_ROOM + TEXT_PAD)
        return (float(round(width / 20) * 20), float(len(lines) * LINE_ROOM + TEXT_PAD))

    def board_box(self):
        geometry = self.geometry
        return (geometry.x, geometry.y, geometry.width, geometry.height)


class WhiteboardClass(DiagramClass, _SizedByText):
    """A class card: its stereotypes, its name in bold, then its properties and its operations, each part under a rule."""

    owning_module = ""

    @property
    def element_id(self) -> str:
        return f"class.{_key(self.owning_module, self.name)}"

    def board_elements(self) -> List[BoardElement]:
        return [self.board_shape(self.element_id, kind="rect", color="white", size="small", text=self.shown_text, text_align="left")]

    @property
    def shown_text(self) -> str:
        lines = [f"*{' '.join(f'«{item}»' for item in self.stereotypes)}*"] if self.stereotypes else []
        lines.append(f"**{self.name}**")
        lines.append(RULE)
        lines.extend(f"+ {item.name}{(': ' + item.type_hint) if item.type_hint else ''}" for item in self.properties)
        lines.append(RULE)
        lines.extend(
            f"{'- ' if item.name.startswith('_') else '+ '}{item.name}({', '.join(parameter.save() for parameter in item.parameters)})"
            f"{(': ' + item.return_type) if item.return_type else ''}"
            for item in self.operations
        )
        return "\n".join(lines)

    @classmethod
    def from_card(cls, text: str) -> Optional["WhiteboardClass"]:
        """The class a card shows; none for text that names no class in bold."""
        lines = [line.strip() for line in text.splitlines()]
        stereotypes: List[str] = []
        if lines and _ITALIC.match(lines[0]) and not _BOLD.match(lines[0]):
            stereotypes = _MARK.findall(lines.pop(0))
        name = _BOLD.match(lines[0]) if lines else None
        if name is None:
            return None
        parts = _parts(lines[1:])
        properties = [Property.from_signature(line[2:]) or Property(name=line[2:].strip()) for line in parts[0]]
        operations = [found for found in (Operation.from_signature(line[2:]) for line in parts[1]) if found is not None]
        read = cls(name=name.group(1).strip(), sequential_order=1, properties=properties, operations=operations)
        read.stereotypes = stereotypes
        return read


def _parts(lines: List[str]) -> Tuple[List[str], List[str]]:
    """The member lines under the first rule and under the second."""
    parts: List[List[str]] = [[], [], []]
    index = -1
    for line in lines:
        if line == RULE:
            index = min(index + 1, 2)
        elif index >= 0 and line[:2] in ("+ ", "- "):
            parts[index].append(line)
    return parts[0], parts[1]


class WhiteboardModule(DiagramModule, _SizedByText):
    """A module: in the modules view a box with its name, purpose and seam terms; in the class view the section that
    holds its classes."""

    class_type = WhiteboardClass

    @property
    def element_id(self) -> str:
        return f"module.{_key(self.name)}"

    @property
    def section_id(self) -> str:
        return f"section.{_key(self.name)}"

    @property
    def shown_text(self) -> str:
        lines = [f"**{self.name}**", f"*{self.purpose_line()}*"]
        lines.extend(f"- {term}" for term in self.shown_seam_terms())
        return "\n".join(lines)

    def board_elements(self) -> List[BoardElement]:
        return [self.board_shape(self.element_id, kind="rounded", color="blue", size="small", text=self.shown_text, text_align="left")]

    @classmethod
    def from_box(cls, text: str, sequential_order: int) -> Optional["WhiteboardModule"]:
        """The module a modules-view box shows; none for text that names no module in bold."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        name = _BOLD.match(lines[0]) if lines else None
        if name is None:
            return None
        purpose = _ITALIC.match(lines[1]) if len(lines) > 1 else None
        terms = [line[2:].strip() for line in lines[1:] if line.startswith("- ") and line[2:].strip() != "..."]
        return cls(
            name=name.group(1).strip(), sequential_order=sequential_order,
            description=purpose.group(1).strip() if purpose else "", seam_terms=terms,
        )


class WhiteboardCleanEngineeringModel(DiagramCleanEngineeringModel):
    """Clean Engineering whiteboard I/O: render draws the model on a board, parse reads one back."""

    module_type = WhiteboardModule
    suffixes = (Whiteboard.SUFFIX,)

    def save(self) -> str:
        return self.render(self)

    def render(self, canonical: CleanEngineeringModel, previous: Optional[str] = None) -> str:
        """Become the canonical model once, as whiteboard modules and classes, then draw it; the elements a previous
        board held stay where people put them."""
        if canonical is not self:
            self.translate_from(canonical)
        board = self._modules_board() if self.is_modules_view else self._class_board()
        if previous:
            board.keep_places(Whiteboard.load(previous))
        return board.save()

    def parse(self, text: str) -> "WhiteboardCleanEngineeringModel":
        """Read a modules view or a class view drawn on a board into this model's own modules, and return it."""
        board = Whiteboard.load(text)
        self.modules = []
        boxes = [element for element in board.elements if isinstance(element, Shape) and element.id.startswith("module.")]
        if boxes:
            self._read_modules(board, boxes)
            return self
        sections = [element for element in board.elements if isinstance(element, Section) and element.id.startswith("section.")]
        if not sections:
            raise UnreadableBoard("The board holds no module and no class")
        self._read_classes(board, sections)
        return self

    def _modules_board(self) -> Whiteboard:
        board = Whiteboard("Modules")
        modules = self._all_modules()
        _grid(modules, origin=(0, 0))
        for module in modules:
            board.draw(module)
        by_name = {module.name: module for module in modules}
        for module in modules:
            for dependency in module.external_deps():
                if dependency in by_name:
                    board.add(Arrow(
                        f"needs.{_key(module.name, dependency)}", from_id=module.element_id,
                        to_id=by_name[dependency].element_id,
                    ))
        return board

    def _class_board(self) -> Whiteboard:
        board = Whiteboard("Classes")
        cards: Dict[str, WhiteboardClass] = {}
        top = 0.0
        for module in self._all_modules():
            if not module.classes:
                continue
            for oclass in module.classes:
                oclass.owning_module = module.name
                cards.setdefault(oclass.name, oclass)
            width, height = _grid(module.classes, origin=(SECTION_INSET, top + SECTION_TITLE_ROOM + SECTION_INSET))
            board.add(Section(module.section_id, x=0, y=top + SECTION_TITLE_ROOM, w=width + 2 * SECTION_INSET,
                              h=height + 2 * SECTION_INSET, text=module.name))
            for oclass in module.classes:
                board.draw(oclass)
            top += SECTION_TITLE_ROOM + height + 2 * SECTION_INSET + GAP
        for oclass in cards.values():
            for arrow in _arrows_of(oclass, cards):
                board.add(arrow)
        return board

    def _all_modules(self) -> List[WhiteboardModule]:
        found: List[WhiteboardModule] = []
        pending = list(self.modules)
        while pending:
            module = pending.pop(0)
            found.append(module)
            pending[:0] = module.modules
        return found

    def _read_modules(self, board: Whiteboard, boxes: List[Shape]) -> None:
        by_id: Dict[str, WhiteboardModule] = {}
        for box in boxes:
            module = WhiteboardModule.from_box(box.text, len(self.modules) + 1)
            if module is not None:
                self.modules.append(module)
                by_id[box.id] = module
        for arrow in (element for element in board.elements if isinstance(element, Arrow)):
            source, target = by_id.get(arrow.from_id), by_id.get(arrow.to_id)
            if source is not None and target is not None and target.name not in source.dependencies:
                source.dependencies.append(target.name)

    def _read_classes(self, board: Whiteboard, sections: List[Section]) -> None:
        by_id: Dict[str, WhiteboardClass] = {}
        for section in sections:
            module = WhiteboardModule(name=section.text.strip(), sequential_order=len(self.modules) + 1)
            self.modules.append(module)
            for card in board.elements:
                if isinstance(card, Shape) and card.id.startswith("class.") and _inside(card, section):
                    oclass = WhiteboardClass.from_card(card.text)
                    if oclass is not None:
                        oclass.sequential_order = len(module.classes) + 1
                        module.classes.append(oclass)
                        by_id[card.id] = oclass
        for arrow in (element for element in board.elements if isinstance(element, Arrow)):
            source, target = by_id.get(arrow.from_id), by_id.get(arrow.to_id)
            if source is None or target is None:
                continue
            kind = arrow.id.split(".")[0]
            if kind == "extends" and target.name not in source.bases:
                source.bases.append(target.name)
            elif kind == "uses":
                label = _DEPENDENCY_LABEL.match(arrow.label or "")
                source.depend_on(target.name, label.group(1) if label else arrow.label)
            elif kind == "has":
                source.take_arrow(target.name, arrow.label)
        for oclass in by_id.values():
            for prop in oclass.properties:
                prop.derive_relationship()


def _arrows_of(oclass: WhiteboardClass, cards: Dict[str, WhiteboardClass]) -> List[Arrow]:
    """The arrows a class card starts: one to each base, each class a property's relationship names, and each class it
    depends on, each only to a class on the board."""
    arrows: List[Arrow] = []
    for base in oclass.declared_bases(cards):
        if base in cards:
            arrows.append(Arrow(f"extends.{_key(oclass.element_id, base)}", from_id=oclass.element_id,
                                to_id=cards[base].element_id, label="extends"))
    for prop in oclass.properties:
        relationship = prop.relationship
        if relationship is not None and relationship.target in cards:
            arrows.append(Arrow(f"has.{_key(oclass.element_id, prop.name)}", from_id=oclass.element_id,
                                to_id=cards[relationship.target].element_id, label=relationship.kind))
    for dependency in oclass.dependencies:
        if dependency.target in cards:
            arrows.append(Arrow(f"uses.{_key(oclass.element_id, dependency.target, dependency.label)}",
                                from_id=oclass.element_id, to_id=cards[dependency.target].element_id,
                                label=f"<<{dependency.label}>>", dash=True))
    return arrows


def _grid(nodes: List[_SizedByText], origin: Tuple[float, float]) -> Tuple[float, float]:
    """Place each node on a grid of COLUMNS columns from origin, each box as big as its text and each row as tall as its
    tallest box, and answer the grid's width and height."""
    x0, y0 = origin
    sizes = [node.board_size() for node in nodes]
    widths = [0.0] * COLUMNS
    rows: List[float] = []
    for index, (width, height) in enumerate(sizes):
        widths[index % COLUMNS] = max(widths[index % COLUMNS], width)
        if index % COLUMNS == 0:
            rows.append(0.0)
        rows[-1] = max(rows[-1], height)
    for index, (node, (width, height)) in enumerate(zip(nodes, sizes)):
        column, row = index % COLUMNS, index // COLUMNS
        node.geometry = Geometry(x0 + sum(widths[:column]) + GAP * column, y0 + sum(rows[:row]) + GAP * row, width, height)
    used = [width for width in widths if width]
    return (sum(used) + GAP * max(len(used) - 1, 0), sum(rows) + GAP * max(len(rows) - 1, 0))


def _inside(card: Shape, section: Section) -> bool:
    x, y = card.x + card.w / 2, card.y + card.h / 2
    return section.x <= x <= section.x + section.w and section.y <= y <= section.y + section.h
