"""Claude Whiteboard channel for Clean Engineering: the modules view and the class view drawn on a board, and read back.

A modules view draws each module as a box with its purpose and seam terms, and each dependency as an arrow. A class view
draws each module as a section holding its class cards, each base as an arrow labelled ``extends``, each relationship a
property stands for as an arrow labelled with its kind, and each dependency as a dashed arrow labelled ``<<label>>``.
Like the drawio channel, it extends the channel-agnostic diagram nodes; only the elements it writes are its own.

Element ids name what an element draws (``module.``, ``section.``, ``class.``, ``extends.``, ``has.``, ``uses.``,
``needs.``) and a key of the node's name, so the same module or class keeps its id from one render to the next.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Dict, List, Optional

from harness.whiteboard import Arrow, BoardElement, Box, Section, Shape, UnreadableBoard, Whiteboard, WhiteboardNode

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.diagram.diagram_node import (
    DiagramClass,
    DiagramCleanEngineeringModel,
    DiagramModule,
)
from cdd_guidance.practices.clean_engineering.model.diagram.geometry import Geometry
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property

RULE = "---"
COLUMNS = 3
GAP = 64
SECTION_INSET = 24
SECTION_TITLE_ROOM = 52
LINE_ROOM = 21
"""The height one line of small text takes on a board, with room to spare: a board grows a block too small for its
words over its neighbours."""
LETTER_ROOM = 7.5
TEXT_PAD = 24
MIN_WIDTH = 200
WIDTH_STEP = 20
KEY_LENGTH = 12
"""Hex digits of a name's hash in an element id: enough that two modules or classes of one model never share one."""


def _key(*names: str) -> str:
    return hashlib.sha1("/".join(names).encode("utf-8")).hexdigest()[:KEY_LENGTH]


class _BoardText:
    """The words on a module box or a class card, read back line by line: the italic line above or below the bold
    name, the bulleted seam terms, and the member lines under each rule."""

    BOLD = re.compile(r"^\*\*(.+)\*\*$")
    ITALIC = re.compile(r"^\*([^*].*)\*$")
    MARK = re.compile(r"«([^»]+)»")

    def __init__(self, text: str) -> None:
        self.lines = [line.strip() for line in text.splitlines() if line.strip()]
        self.at = next((index for index, line in enumerate(self.lines) if self.BOLD.match(line)), -1)

    @property
    def name(self) -> str:
        return self.BOLD.match(self.lines[self.at]).group(1).strip() if self.at >= 0 else ""

    @property
    def stereotypes(self) -> List[str]:
        above = self.lines[:self.at] if self.at > 0 else []
        return [mark for line in above if self.ITALIC.match(line) for mark in self.MARK.findall(line)]

    @property
    def purpose(self) -> str:
        below = self.lines[self.at + 1:self.at + 2]
        found = self.ITALIC.match(below[0]) if below else None
        return found.group(1).strip() if found else ""

    @property
    def terms(self) -> List[str]:
        return [line[2:].strip() for line in self.lines[self.at + 1:] if line.startswith("- ") and line[2:].strip() != "..."]

    def members(self, part: int) -> List[str]:
        """The member lines under rule number part (0 for the properties, 1 for the operations), without their mark."""
        rules = [index for index, line in enumerate(self.lines) if line == RULE]
        if len(rules) <= part:
            return []
        end = rules[part + 1] if len(rules) > part + 1 else len(self.lines)
        return [line[2:] for line in self.lines[rules[part] + 1:end] if line[:2] in ("+ ", "- ")]


class _SizedByText(WhiteboardNode):
    """A node whose box is as big as the words it shows, sized from them before the diagram places it."""

    @property
    def shown_text(self) -> str:
        raise NotImplementedError

    @property
    def board_size(self) -> Box:
        lines = self.shown_text.splitlines() or [""]
        width = max(MIN_WIDTH, max(len(line) for line in lines) * LETTER_ROOM + TEXT_PAD)
        return Box(0, 0, math.ceil(width / WIDTH_STEP) * WIDTH_STEP, len(lines) * LINE_ROOM + TEXT_PAD)

    def board_box(self) -> Box:
        geometry = self.geometry
        return Box(geometry.x, geometry.y, geometry.width, geometry.height)


class WhiteboardClass(DiagramClass, _SizedByText):
    """A class card: its stereotypes, its name in bold, then its properties and its operations, each part under a rule."""

    owning_module = ""

    @property
    def element_id(self) -> str:
        return f"class.{_key(self.owning_module, self.name)}"

    @property
    def shown_text(self) -> str:
        lines = [f"*{' '.join(f'«{item}»' for item in self.stereotypes)}*"] if self.stereotypes else []
        lines.extend([f"**{self.name}**", RULE])
        lines.extend(f"+ {item.name}{(': ' + item.type_hint) if item.type_hint else ''}" for item in self.properties)
        lines.append(RULE)
        lines.extend(
            f"{'- ' if item.name.startswith('_') else '+ '}{item.name}({', '.join(parameter.save() for parameter in item.parameters)})"
            f"{(': ' + item.return_type) if item.return_type else ''}"
            for item in self.operations
        )
        return "\n".join(lines)

    def board_elements(self) -> List[BoardElement]:
        return [self.board_shape(self.element_id, kind="rect", color="white", size="small", text=self.shown_text, text_align="left")]

    def take_text(self, text: _BoardText) -> "WhiteboardClass":
        """Become the class a card's words show: its stereotypes, properties and operations."""
        self.stereotypes = text.stereotypes
        self.properties = [Property.from_signature(line) or Property(name=line.strip()) for line in text.members(0)]
        self.operations = [found for found in (Operation.from_signature(line) for line in text.members(1)) if found is not None]
        return self

    def board_arrows(self, cards: Dict[str, "WhiteboardClass"]) -> List[Arrow]:
        """The arrows this card starts: one to each base, each class a property's relationship names, and each class it
        depends on, each only to a class on the board."""
        arrows = [
            Arrow(f"extends.{_key(self.element_id, base)}", from_id=self.element_id, to_id=cards[base].element_id, label="extends")
            for base in self.declared_bases(cards) if base in cards
        ]
        arrows.extend(
            Arrow(f"has.{_key(self.element_id, prop.name)}", from_id=self.element_id,
                  to_id=cards[prop.relationship.target].element_id, label=prop.relationship.kind)
            for prop in self.properties if prop.relationship is not None and prop.relationship.target in cards
        )
        arrows.extend(
            Arrow(f"uses.{_key(self.element_id, item.target, item.label)}", from_id=self.element_id,
                  to_id=cards[item.target].element_id, label=f"<<{item.label}>>", dash=True)
            for item in self.dependencies if item.target in cards
        )
        return arrows

    def take_board_arrow(self, arrow: Arrow, target: str) -> None:
        """Take what an arrow this card starts says about target: a base, a dependency, or the kind of the property
        whose type names it."""
        kind = arrow.id.split(".")[0]
        if kind == "extends" and target not in self.bases:
            self.bases.append(target)
        elif kind == "uses":
            self.depend_on(target, arrow.label.removeprefix("<<").removesuffix(">>"))
        elif kind == "has":
            self.take_arrow(target, arrow.label)


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

    def dependency_arrows(self, modules: Dict[str, "WhiteboardModule"]) -> List[Arrow]:
        return [
            Arrow(f"needs.{_key(self.name, dependency)}", from_id=self.element_id, to_id=modules[dependency].element_id)
            for dependency in self.external_deps() if dependency in modules
        ]

    def take_text(self, text: _BoardText) -> "WhiteboardModule":
        """Become the module a box's words show: its purpose and seam terms."""
        self.description = text.purpose
        self.seam_terms = text.terms
        return self


class _Grid:
    """Nodes laid out in rows of COLUMNS, each box as big as its words and each row as tall as its tallest box."""

    def __init__(self, nodes: List[_SizedByText]) -> None:
        self.nodes = nodes
        self.sizes = [node.board_size for node in nodes]
        self.widths = [max((size.w for size in self.sizes[column::COLUMNS]), default=0) for column in range(COLUMNS)]
        self.heights = [max(size.h for size in self.sizes[row:row + COLUMNS]) for row in range(0, len(self.sizes), COLUMNS)]

    def place_from(self, x: float, y: float) -> Box:
        """Give each node its place from (x, y) and answer the box the grid fills."""
        for index, (node, size) in enumerate(zip(self.nodes, self.sizes)):
            column, row = index % COLUMNS, index // COLUMNS
            node.geometry = Geometry(x + sum(self.widths[:column]) + GAP * column, y + sum(self.heights[:row]) + GAP * row, size.w, size.h)
        used = [width for width in self.widths if width]
        return Box(x, y, sum(used) + GAP * max(len(used) - 1, 0), sum(self.heights) + GAP * max(len(self.heights) - 1, 0))


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
        """The modules view or class view a saved board's text holds, read into this model's own modules."""
        return self.read_board(Whiteboard.load(text))

    def read_board(self, board: Whiteboard) -> "WhiteboardCleanEngineeringModel":
        """Read a modules view or a class view drawn on board into this model's own modules, and return it."""
        self.modules = []
        if any(element.id.startswith("module.") for element in board.elements):
            self._read_modules(board)
        elif any(isinstance(element, Section) for element in board.elements):
            self._read_classes(board)
        else:
            raise UnreadableBoard("The board holds no module and no class")
        return self

    def _modules_board(self) -> Whiteboard:
        board = Whiteboard("Modules")
        modules = self._all_modules()
        _Grid(modules).place_from(0, 0)
        for module in modules:
            board.draw(module)
        by_name = {module.name: module for module in modules}
        for module in modules:
            for arrow in module.dependency_arrows(by_name):
                board.add(arrow)
        return board

    def _class_board(self) -> Whiteboard:
        board = Whiteboard("Classes")
        cards: Dict[str, WhiteboardClass] = {}
        top = 0.0
        for module in (found for found in self._all_modules() if found.classes):
            for oclass in module.classes:
                oclass.owning_module = module.name
                cards.setdefault(oclass.name, oclass)
            filled = _Grid(module.classes).place_from(SECTION_INSET, top + SECTION_TITLE_ROOM + SECTION_INSET)
            board.add(Section(module.section_id, x=0, y=top + SECTION_TITLE_ROOM, w=filled.w + 2 * SECTION_INSET,
                              h=filled.h + 2 * SECTION_INSET, text=module.name))
            for oclass in module.classes:
                board.draw(oclass)
            top += SECTION_TITLE_ROOM + filled.h + 2 * SECTION_INSET + GAP
        for oclass in cards.values():
            for arrow in oclass.board_arrows(cards):
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

    def _read_modules(self, board: Whiteboard) -> None:
        by_id: Dict[str, WhiteboardModule] = {}
        for box in (element for element in board.elements if isinstance(element, Shape) and element.id.startswith("module.")):
            text = _BoardText(box.text)
            if text.name:
                by_id[box.id] = WhiteboardModule(name=text.name, sequential_order=len(self.modules) + 1).take_text(text)
                self.modules.append(by_id[box.id])
        for arrow in (element for element in board.elements if isinstance(element, Arrow)):
            source, target = by_id.get(arrow.from_id), by_id.get(arrow.to_id)
            if source is not None and target is not None and target.name not in source.dependencies:
                source.dependencies.append(target.name)

    def _read_classes(self, board: Whiteboard) -> None:
        by_id: Dict[str, WhiteboardClass] = {}
        for section in (element for element in board.elements if isinstance(element, Section)):
            by_id.update(self._read_section(board, section))
        for arrow in (element for element in board.elements if isinstance(element, Arrow)):
            source, target = by_id.get(arrow.from_id), by_id.get(arrow.to_id)
            if source is not None and target is not None:
                source.take_board_arrow(arrow, target.name)
        for oclass in by_id.values():
            for prop in oclass.properties:
                prop.derive_relationship()

    def _read_section(self, board: Whiteboard, section: Section) -> Dict[str, WhiteboardClass]:
        """The module a section draws, added to this model, with the classes on the cards inside it by their ids."""
        module = WhiteboardModule(name=section.text.strip(), sequential_order=len(self.modules) + 1)
        self.modules.append(module)
        read: Dict[str, WhiteboardClass] = {}
        cards = [element for element in board.elements if isinstance(element, Shape) and element.id.startswith("class.")]
        for card in (found for found in cards if section.place.holds(found.place)):
            text = _BoardText(card.text)
            if text.name:
                read[card.id] = WhiteboardClass(name=text.name, sequential_order=len(module.classes) + 1).take_text(text)
                module.classes.append(read[card.id])
        return read
