"""Claude Whiteboard channel for Clean Engineering: the modules view and the class view drawn on a board, and read back.

The board is drawn as the drawio channel draws its diagram, through the same diagram layer: the modules view stands its
modules where ``ModuleLayout`` puts them, and the class view decides its pages, cards, arrows and their routes through
``ClassView`` and the shared card placement and arrow router. Only what a board draws differently is its own: a module
that holds others is a section with its purpose and seam terms written under its title, each card is sized for the
board's words, an arrow's route is written as the board's ``bends``, and a class view too big for one page puts each
module's page in a section of its own, side by side.

Element ids name what an element draws (``module.``, ``class.``, ``imported.``, ``about.``, an arrow's kind) and a key of
the node's name, so the same module or class keeps its id from one render to the next.
"""

from __future__ import annotations

import math
import re
from typing import Dict, List, Optional, Tuple

from harness.whiteboard import MAX_SIDE, Arrow, BoardElement, Box, ElementId, Label, Section, UnreadableBoard, Whiteboard, WhiteboardNode

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass, UnreadableSource
from cdd_guidance.practices.clean_engineering.model.diagram.class_layout import PAGE_MARGIN, ArrowRouter, DiagramArrow
from cdd_guidance.practices.clean_engineering.model.diagram.class_view import DEPENDENCY_LABEL, ClassView, ClassViewPage
from cdd_guidance.practices.clean_engineering.model.diagram.diagram_node import (
    DiagramClass,
    DiagramCleanEngineeringModel,
    DiagramModule,
    ImportedClass,
    ModulesView,
)
from cdd_guidance.practices.clean_engineering.model.diagram.geometry import MODULE_CELL_WIDTH
from cdd_guidance.practices.clean_engineering.model.diagram.module_layout import ModuleLayout
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property
from harness.guidance.practice_formats import Written

RULE = "---"
LINE_ROOM = 21
"""The height one line of small text takes on a board, with room to spare: a board grows a block too small for its
words over its neighbours."""
LETTER_ROOM = 7.5
TEXT_PAD = 24
MIN_WIDTH = 200
WIDTH_STEP = 20
TITLE_ROOM = 80
"""How far above the first card or module the board's title stands."""
SUBTITLE_ROOM = 56
SUBTITLE_WRAP = 600
"""How wide the line under a modules view's title runs before it wraps."""
"""How far a modules view's title stands above the line under it that says how to read the view."""
MODULES_SUBTITLE = (
    "Independent modules with one-way dependencies. Arrows point toward the depended-on module (build before). "
    "Path nesting = containment; shared base terms live on the parent."
)
PAGE_GAP = 200
"""The room between two module pages of a class view, each drawn as a section side by side."""
PAGE_ROW_WIDTH = 12000
"""The widest a row of module pages runs before the next page starts a row under it."""
PAGE_INSET = 48
"""The room between a module page's section and the cards in it."""
GROUP_INSET = 24
"""The room between the section drawn round a group of module pages and the pages' sections."""
SECTION_TITLE_ROOM = 28
"""How far above its box a section's title stands, so a section nested in another needs this room above it."""
NESTED_TITLE_ROOM = 44
"""The room above a section nested in another for its title, which a board writes over the section's top edge."""
ABOUT_INSET_X = 16
ABOUT_INSET_Y = 12
"""How far in from a section's left and top edges its purpose and seam terms are written, below its title."""
INHERITANCE = "inheritance"
KINDS = ("inheritance", "composition", "aggregation", "association", "dependency")


def _element(role: str, *names: str, parts: Tuple[str, ...] = ()) -> ElementId:
    """The element id of what names name, keyed as every Clean Engineering board keys its elements
    (``_PlacedOnBoard.KEY_LENGTH``)."""
    return ElementId.of(role, *names, length=_PlacedOnBoard.KEY_LENGTH, parts=parts)


def _text_box(text: str) -> Tuple[float, float]:
    """The width and height a block needs for text in the board's small words."""
    lines = text.splitlines() or [""]
    width = max(MIN_WIDTH, max(len(line) for line in lines) * LETTER_ROOM + TEXT_PAD)
    return (math.ceil(width / WIDTH_STEP) * WIDTH_STEP, len(lines) * LINE_ROOM + TEXT_PAD)


class _BoardText:
    """The words on a module box or a class card, read back line by line: the module tag, the italic line above or
    below the bold name, the bulleted seam terms, and the member lines under each rule."""

    BOLD = re.compile(r"^\*\*(.+)\*\*$")
    ITALIC = re.compile(r"^\*([^*].*)\*$")
    TAG = re.compile(r"^`(.+)`$")
    MARK = re.compile(r"«([^»]+)»")

    def __init__(self, text: str) -> None:
        self.lines = [line.strip() for line in text.splitlines() if line.strip()]
        self.at = next((index for index, line in enumerate(self.lines) if self.BOLD.match(line)), -1)

    @property
    def name(self) -> str:
        return self.BOLD.match(self.lines[self.at]).group(1).strip() if self.at >= 0 else ""

    @property
    def module(self) -> str:
        """The module a class card's tag names, on its first line."""
        found = self.TAG.match(self.lines[0]) if self.lines else None
        return found.group(1).strip() if found else ""

    @property
    def stereotypes(self) -> List[str]:
        above = self.lines[:self.at] if self.at > 0 else []
        return [mark for line in above if self.ITALIC.match(line) for mark in self.MARK.findall(line)]

    @property
    def purpose(self) -> str:
        """The italic line under the bold name, or the first italic line of words with no name, as under a section."""
        below = self.lines[self.at + 1:self.at + 2]
        found = self.ITALIC.match(below[0]) if below else None
        return found.group(1).strip() if found else ""

    @property
    def terms(self) -> List[str]:
        return [line[2:].strip() for line in self.lines[self.at + 1:] if line.startswith("- ") and line[2:].strip() != "..."]

    def folded_parts(self) -> List["_BoardText"]:
        """The words of each class drawn inside this card below its own operations: each from its italic stereotype
        line, or its bold name, to the next one's."""
        names = [index for index, line in enumerate(self.lines) if index > self.at >= 0 and self.BOLD.match(line)]
        starts = [index - 1 if self.ITALIC.match(self.lines[index - 1]) else index for index in names]
        return [_BoardText("\n".join(self.lines[start:end])) for start, end in zip(starts, [*starts[1:], len(self.lines)])]

    def members(self, part: int) -> List[str]:
        """The member lines under rule number part (0 for the properties, 1 for the operations), without their mark."""
        rules = [index for index, line in enumerate(self.lines) if line == RULE]
        if len(rules) <= part:
            return []
        end = rules[part + 1] if len(rules) > part + 1 else len(self.lines)
        return [line[2:] for line in self.lines[rules[part] + 1:end] if line[:2] in ("+ ", "- ")]


class _PlacedOnBoard(WhiteboardNode):
    """A diagram node drawn on a board in the box the shared diagram layout placed it in. Clean Engineering's element
    ids hash a name to twelve hex digits, enough that two modules or classes of one model never share one."""

    KEY_LENGTH = 12

    def board_box(self) -> Box:
        geometry = self.geometry
        return Box(geometry.x, geometry.y, geometry.width, geometry.height)


class WhiteboardClass(DiagramClass, _PlacedOnBoard):
    """A class card: its module's tag, its stereotypes, its name in bold, then its properties and its operations, each
    part under a rule; as wide and tall as its words."""

    fill_color = ""
    owning_module = ""

    @property
    def shown_text(self) -> str:
        lines = [f"`{self.owning_module}`"] if self.owning_module else []
        lines.extend(self.own_lines())
        for folded in self.folded:
            lines.append(RULE)
            lines.extend(folded.own_lines())
        return "\n".join(lines)

    def own_lines(self) -> List[str]:
        """Its stereotypes, its name in bold, then its properties and its operations, each part under a rule: the
        whole card, or its part of the card of a class it is folded into."""
        lines = [f"*{' '.join(f'«{item}»' for item in self.stereotypes)}*"] if self.stereotypes else []
        lines.extend([f"**{self.name}**", RULE])
        lines.extend(self.property_lines())
        lines.append(RULE)
        lines.extend(
            f"{'- ' if item.name.startswith('_') else '+ '}{item.name}({', '.join(parameter.save() for parameter in item.parameters)})"
            f"{(': ' + item.return_type) if item.return_type else ''}"
            for item in self.operations
        )
        return lines

    def width(self) -> int:
        return int(_text_box(self.shown_text)[0])

    def height(self) -> int:
        return int(_text_box(self.shown_text)[1])

    def card(self, element_id: str) -> BoardElement:
        return self.board_shape(element_id, kind="rect", color=self.fill_color or "white", size="small",
                                text=self.shown_text, text_align="left")

    def take_text(self, text: _BoardText) -> "WhiteboardClass":
        """Become the class a card's words show: its stereotypes, properties and operations."""
        self.stereotypes = text.stereotypes
        self.properties = [Property.from_signature(line) or Property(name=line.strip()) for line in text.members(0)]
        self.operations = [found for found in (Operation.from_signature(line) for line in text.members(1)) if found is not None]
        for part in text.folded_parts():
            self.fold(WhiteboardClass(name=part.name, sequential_order=1).take_text(part))
        return self


class WhiteboardImportedClass(ImportedClass, WhiteboardClass):
    """The card of a class another module's page owns: the module it is from, its name and its first properties."""

    from_module = ""

    def width(self) -> int:
        return int(_text_box(self.shown_text)[0])

    def height(self) -> int:
        return int(_text_box(self.shown_text)[1])

    @property
    def shown_text(self) -> str:
        lines = [f"*«from: {self.from_module}»*", f"**{self.name}**", RULE]
        lines.extend(f"+ {item.name}{(': ' + item.type_hint) if item.type_hint else ''}" for item in self.key_properties())
        lines.append(RULE)
        return "\n".join(lines)

    def card(self, element_id: str) -> BoardElement:
        return self.board_shape(element_id, kind="rect", color="white", stroke="#666666", size="small",
                                text=self.shown_text, text_align="left")


class WhiteboardModule(DiagramModule, _PlacedOnBoard):
    """A module: in the modules view a box with its name, purpose and seam terms, or, when it holds other modules, a
    section titled with its name and its purpose and seam terms written under the title; in the class view the
    classes it holds."""

    class_type = WhiteboardClass
    ROLE = "module"
    """What the module's element id starts with, so a board reads it back as the module type that drew it."""
    TOP_COLOR = "blue"
    NESTED_COLOR = "#dae8fc"
    holds_modules = False
    """Whether the module holds others on the board, so it is drawn as a section; the modules view says."""
    holds_sections = False
    """Whether a module it holds is a section too, whose title needs room above it in this module's header."""

    only_groups = False
    """Whether the module is a box nobody wrote, drawn only to group the modules whose paths it holds; the modules
    view says. Its element id starts with `nest`, as its draw.io cell's does, so a board reads it back as no module."""
    GROUPING_ROLE = "nest"

    @property
    def element_id(self) -> str:
        return _element(self.GROUPING_ROLE if self.only_groups else self.ROLE, self.name)

    @property
    def about_id(self) -> str:
        return _element("about", self.name)

    @property
    def about_text(self) -> str:
        """The purpose and seam terms, as a section writes them under its title."""
        return "\n".join([f"*{self.purpose_line()}*", *(f"- {term}" for term in self.shown_seam_terms())])

    @property
    def shown_text(self) -> str:
        return f"**{self.name}**\n{self.about_text}"

    @property
    def cell_width(self) -> float:
        return max(MODULE_CELL_WIDTH, _text_box(self.shown_text)[0])

    @property
    def cell_min_height(self) -> float:
        return _text_box(self.shown_text)[1]

    def header_height(self) -> int:
        """The words at the top of the module: under a section's title, its purpose and seam terms, with room for the
        title of a section nested under them."""
        if not self.holds_modules:
            return int(_text_box(self.shown_text)[1])
        return int(_text_box(self.about_text)[1] + (NESTED_TITLE_ROOM if self.holds_sections else 0))

    def board_elements(self) -> List[BoardElement]:
        color = self.NESTED_COLOR if self.nested else self.TOP_COLOR
        if not self.holds_modules:
            return [self.board_shape(self.element_id, kind="rounded", color=color, size="small", text=self.shown_text, text_align="left")]
        box = self.board_box()
        return [
            Section(self.element_id, box=box, color=color, text=self.name),
            Label(self.about_id, x=box.x + ABOUT_INSET_X, y=box.y + ABOUT_INSET_Y, text=self.about_text, size="small", wrap=box.w - 2 * ABOUT_INSET_X),
        ]

    def dependency_arrows(self, modules: Dict[str, "WhiteboardModule"]) -> List[BoardElement]:
        """An arrow to each module this one depends on, but the one it sits in, named by the words on the dependency."""
        return [
            Arrow(_element("needs", self.name, dependency), from_id=self.element_id,
                  to_id=modules[dependency].element_id, label=self.dependency_labels.get(dependency, ""))
            for dependency in self.dependencies if dependency in modules and dependency != self.path_parent
        ]

    def take_text(self, text: _BoardText) -> "WhiteboardModule":
        """Become the module a box's words show: its purpose and seam terms."""
        self.description = text.purpose
        self.seam_terms = text.terms
        return self


class _WhiteboardModuleLayout(ModuleLayout):
    """The modules layout, with room between modules stacked in a column for the title a section writes above its box."""

    row_gap = ModuleLayout.row_gap + NESTED_TITLE_ROOM


class _ModulesBoard(ModulesView):
    """Draws one modules view: the modules where the shared modules layout stands them, and their dependencies."""

    def draw(self) -> Whiteboard:
        for name, cell in self._cells.items():
            cell.holds_modules = bool(self._forest.children_of.get(name))
            cell.only_groups = name in self._forest.synthetic
        for name, cell in self._cells.items():
            cell.holds_sections = any(self._cells[child].holds_modules for child in self._forest.children_of.get(name, []))
        layout = _WhiteboardModuleLayout(self._forest, self._cells).lay_out()
        board = Whiteboard(self._channel.modules_title)
        board.add(Label(ElementId("title"), x=layout.start_x, y=layout.start_y - TITLE_ROOM - SUBTITLE_ROOM, text=board.title, size="large"))
        board.add(Label(ElementId("subtitle"), x=layout.start_x, y=layout.start_y - TITLE_ROOM, text=MODULES_SUBTITLE, size="small", wrap=SUBTITLE_WRAP))
        for name in self._forest.in_model_order(self._forest.roots):
            cell = self._cells[name]
            cell.nested = layout.parent_of.get(name) is not None
            cell.geometry = layout.page_box(name)
            for element in cell.board_elements():
                board.add(element)
        for cell in self._cells.values():
            for arrow in cell.dependency_arrows(self._cells):
                board.add(arrow)
        return board


class ClassBoard(ClassView):
    """Draws one class view as the drawio channel decides it: one page, or one page per module. A drawio diagram
    keeps each module's page on a tab of its own; a board has one canvas, so each page is a section, the sections
    side by side in rows no wider than PAGE_ROW_WIDTH, each row under the last. A model whose modules fall into
    groups, such as the aggregates of one bounded context, draws a larger section round each group's pages, titled
    with the group's name, the groups side by side in rows the same way."""

    page_inset = PAGE_INSET
    """The room between a module page's section and the cards in it."""
    group_role = "group"
    """What the id of the section drawn round a group of pages starts with."""
    links_across_pages = False
    """True when an arrow from one page's class to another page's is drawn between the two cards themselves; else
    each page shows the other page's class as a dashed «from:» copy and the arrow ends on that."""

    @property
    def draws_one_page(self) -> bool:
        return self.on_one_page

    def page_groups(self) -> List[Tuple[str, List[Module]]]:
        """The module pages in the order the board draws them, each group under the name of the section drawn round
        it; one group with no name when no section is drawn round the pages."""
        return [("", self.named_modules)]

    def page_title(self, module: Module) -> str:
        """The words a module page's section is titled with."""
        return module.name.strip()

    def draw(self) -> Whiteboard:
        board = Whiteboard("Classes")
        board.add(Label(ElementId("title"), x=PAGE_MARGIN, y=PAGE_MARGIN - TITLE_ROOM, text=f"{self.channel.name or 'Model'} - Classes", size="large"))
        if self.draws_one_page:
            _ClassBoardPage(self).draw_on(board, Box(0.0, PAGE_MARGIN, 0, 0))
            return board
        groups = [_PageGroup(self, name, modules) for name, modules in self.page_groups()]
        corners = [Box(left, top + PAGE_MARGIN, 0, 0) for left, top in _flowed([group.size() for group in groups], PAGE_ROW_WIDTH)]
        # Every group's section goes on the board before any page's, so each lies behind the pages it holds.
        for group, corner in zip(groups, corners):
            group.draw_section_on(board, corner)
        for group, corner in zip(groups, corners):
            group.draw_pages_on(board, corner)
        if self.links_across_pages:
            for arrow in self._arrows_across_pages():
                board.add(_arrow_element(arrow, (arrow.source, arrow.target), _element("class", arrow.source), _element("class", arrow.target), parts=("across",)))
        return board

    def _arrows_across_pages(self) -> List[DiagramArrow]:
        """The arrows of the whole model whose two classes sit on different pages, each straight from card to card."""
        every = ClassViewPage(self)._arrows()
        page_of = {cell_id: id(self.module_of.get(id(oclass))) for cell_id, oclass in self.classes_by_cell.items()}
        return [arrow for arrow in every if page_of.get(arrow.source) != page_of.get(arrow.target)]


def _flowed(sizes: List[Tuple[float, float]], row_width: float) -> List[Tuple[float, float]]:
    """The top-left corner of each box of sizes, laid left to right PAGE_GAP apart, a new row PAGE_GAP under the last
    when a box would run the row wider than row_width; the first box at (0, 0)."""
    corners: List[Tuple[float, float]] = []
    left, top, row_bottom = 0.0, 0.0, 0.0
    for width, height in sizes:
        if left > 0 and left + width > row_width:
            left, top = 0.0, row_bottom + PAGE_GAP
        corners.append((left, top))
        left += width + PAGE_GAP
        row_bottom = max(row_bottom, top + height)
    return corners


class _PageGroup:
    """The module pages of one group on a board, laid out in rows, and, when the group has a name, the section drawn
    round them: GROUP_INSET in from its edges, with SECTION_TITLE_ROOM above the first row for the pages' own titles,
    and rows no wider than a board draws one section, so the section is never cut into pieces."""

    def __init__(self, view: ClassBoard, name: str, modules: List[Module]) -> None:
        self._view = view
        self.name = name
        self._pages = [_ClassBoardPage(view, module) for module in modules]
        row_width = MAX_SIDE - 2 * GROUP_INSET if name else PAGE_ROW_WIDTH
        self._corners = _flowed([page.size() for page in self._pages], row_width)

    @property
    def _inset(self) -> Tuple[float, float]:
        """How far the first page stands in from the group's left and top edges."""
        return (GROUP_INSET, GROUP_INSET + SECTION_TITLE_ROOM) if self.name else (0.0, 0.0)

    def size(self) -> Tuple[float, float]:
        """The width and height the group fills: its pages, and round them its section's edges when it has one."""
        if not self._pages:
            return (0.0, 0.0)
        right = max(left + page.size()[0] for page, (left, _) in zip(self._pages, self._corners))
        bottom = max(top + page.size()[1] for page, (_, top) in zip(self._pages, self._corners))
        if not self.name:
            return (right, bottom)
        return (right + 2 * GROUP_INSET, bottom + GROUP_INSET + SECTION_TITLE_ROOM + GROUP_INSET)

    def draw_section_on(self, board: Whiteboard, corner: Box) -> None:
        if self.name and self._pages:
            width, height = self.size()
            board.add(Section(_element(self._view.group_role, self.name), box=Box(corner.x, corner.y, width, height), text=self.name))

    def draw_pages_on(self, board: Whiteboard, corner: Box) -> None:
        inset_x, inset_y = self._inset
        for page, (left, top) in zip(self._pages, self._corners):
            page.draw_on(board, Box(corner.x + inset_x + left, corner.y + inset_y + top, 0, 0))


class _ClassBoardPage(ClassViewPage):
    """One page of a class view on a board: its cards where the shared placement puts them and its arrows routed by
    the shared router, the whole page in a section when it is one module's page."""

    def __init__(self, view: ClassBoard, module: Optional[Module] = None) -> None:
        super().__init__(view, module)
        if view.links_across_pages and self._local_ids is not None:
            # The board draws the links to other pages itself, so this page shows only its own classes.
            self._import_ids = []
            self._page_ids = set(self._local_ids)
        self._view = view
        self._name = module.name.strip() if module is not None else ""
        self._title = view.page_title(module) if module is not None else ""
        self._laid = self.laid_out({})

    @property
    def _inset(self) -> float:
        return self._view.page_inset if self._name else 0

    def size(self) -> Tuple[float, float]:
        """The width and height the page fills: its cards as they are laid out, inset from the page's edges."""
        cards = self._laid[0].values()
        if not cards:
            return (0.0, 0.0)
        width = max(card.geometry.x + card.geometry.width for card in cards) - min(card.geometry.x for card in cards)
        height = max(card.geometry.y + card.geometry.height for card in cards) - min(card.geometry.y for card in cards)
        return (width + 2 * self._inset, height + 2 * self._inset)

    def draw_on(self, board: Whiteboard, corner: Box) -> Box:
        """Draw the page with its top-left corner at corner, and answer the box it fills."""
        cards, arrows = self._laid
        routed = ArrowRouter(list(cards.values()), arrows).route()
        if not cards:
            return Box(corner.x, corner.y, 0, 0)
        # The routes are written from the cards' middles, so they are worked out before the page moves.
        lines = [self._board_arrow(arrow, cards, self._name) for arrow in routed]
        filled = self._moved_to(cards, corner, self._inset)
        if self._name:
            board.add(Section(_element("page", self._name), box=filled, text=self._title))
        for cell_id, card in cards.items():
            board.add(card.card(self._element_id(cell_id, self._name)))
        for line in lines:
            board.add(line)
        return filled

    def _moved_to(self, cards: Dict[str, WhiteboardClass], corner: Box, inset: float) -> Box:
        """Move the cards so the page's top-left corner is at corner, inset from it; answer the box the page fills."""
        shift_x = corner.x - min(card.geometry.x for card in cards.values()) + inset
        shift_y = corner.y - min(card.geometry.y for card in cards.values()) + inset
        for card in cards.values():
            card.geometry = card.geometry.shifted(shift_x, shift_y)
        right = max(card.geometry.x + card.geometry.width for card in cards.values()) + inset
        bottom = max(card.geometry.y + card.geometry.height for card in cards.values()) + inset
        return Box(corner.x, corner.y, right - corner.x, bottom - corner.y)

    def _element_id(self, cell_id: str, page_name: str) -> ElementId:
        if self.is_imported(cell_id):
            return _element("imported", page_name, cell_id)
        return _element("class", cell_id)

    def _board_arrow(self, arrow: DiagramArrow, cards: Dict[str, DiagramClass], page_name: str) -> BoardElement:
        """The board's arrow for a routed arrow: its kind in its id, the ends it leaves and reaches by, and its route."""
        return _arrow_element(
            arrow, (page_name, arrow.source, arrow.target),
            self._element_id(arrow.source, page_name), self._element_id(arrow.target, page_name),
            from_side=arrow.exit_side, to_side=arrow.entry_side,
            bends=None if arrow.straight else arrow.bends_from_middles(cards[arrow.source].geometry, cards[arrow.target].geometry),
        )


def _arrow_element(arrow: DiagramArrow, names: Tuple[str, ...], from_id: ElementId, to_id: ElementId, parts: Tuple[str, ...] = (), **route: object) -> BoardElement:
    """The board's arrow for arrow between the elements from_id and to_id name: its kind in its id, then parts, then the
    key names hash to, its words, its dash and its heads, and the route, when one is given; with none, the board draws
    it straight."""
    kind = arrow.kind if arrow.kind in KINDS else "association"
    label = "extends" if kind == INHERITANCE and not arrow.label else arrow.label
    heads = ["circle", "arrow"] if kind in ("composition", "aggregation") else None
    return Arrow(_element(kind, *names, parts=parts), from_id=from_id, to_id=to_id, label=label, dash=kind == "dependency", heads=heads, **route)



class WhiteboardCleanEngineeringModel(DiagramCleanEngineeringModel):
    """Clean Engineering whiteboard I/O: render draws the model on a board, parse reads one back."""

    module_type = WhiteboardModule
    suffixes = (Whiteboard.SUFFIX,)

    class_board_type: type = ClassBoard
    """What draws the model's class view; a model that groups its module pages names its own."""

    module_cell_types: Tuple[type, ...] = (WhiteboardModule,)
    """The module types a modules view reads its elements back as, each picked by the role its id starts with; a model
    that draws modules of its own kinds names their types first."""

    def save(self) -> str:
        return self.render(self)

    def imported_class(self, source: OoadClass, from_module: str = "") -> WhiteboardImportedClass:
        loaded = WhiteboardImportedClass(name=source.name, sequential_order=source.sequential_order, from_module=from_module)
        loaded.translate_from(source)
        return loaded

    def render(self, canonical: CleanEngineeringModel, written: Written = Written()) -> str:
        """Become the canonical model once, as whiteboard modules and classes, then draw it; the elements a previous
        board held stay where people put them."""
        if canonical is not self:
            self.translate_from(canonical)
        return self.board().drawn_over(str(written.previous))

    def board(self) -> Whiteboard:
        """The model drawn: its modules view, or its class view."""
        return _ModulesBoard(self).draw() if self.is_modules_view else self.class_board_type(self).draw()

    def parse(self, text: str, file: str = "") -> "WhiteboardCleanEngineeringModel":
        """The modules view or class view a saved board's text holds, read into this model's own modules. Text that is
        not a saved board raises UnreadableSource, as a draw.io diagram that is not XML does; a saved board that draws
        no module and no class, such as a Stories story map, raises UnreadableBoard from ``take_board``."""
        try:
            board = Whiteboard.from_text(text)
        except UnreadableBoard as unreadable:
            raise UnreadableSource(str(unreadable)) from unreadable
        return self.take_board(board)

    def take_board(self, board: Whiteboard) -> "WhiteboardCleanEngineeringModel":
        """Read a modules view or a class view drawn on board into this model's own modules, and return it."""
        self.modules = []
        module_roles = {kind.ROLE for kind in self.module_cell_types}
        board.holding(module_roles | {"class"}, "module and no class")
        if {element.role for element in board.whole_elements} & module_roles:
            _ModulesReader(self, board).read()
        else:
            _ClassReader(self, board).read()
        return self


class _ModulesReader:
    """Reads a modules view back: each box or section of a module role is a module of the type that drew it; a module
    depends on the module it sits in and on each module its arrows reach, keeping the words on each arrow."""

    def __init__(self, model: WhiteboardCleanEngineeringModel, board: Whiteboard) -> None:
        self._model = model
        self._board = board
        self._types = {kind.ROLE: kind for kind in model.module_cell_types}

    def read(self) -> None:
        by_id: Dict[str, WhiteboardModule] = {}
        abouts = {element.id.key: element for element in self._board.labels if element.role == "about"}
        for element in [*self._board.sections, *self._board.shapes]:
            kind = self._types.get(element.role)
            if kind is None:
                continue
            module = self._module(kind, element, abouts)
            if module is not None:
                by_id[element.id] = module
                self._model.modules.append(module)
        self._take_nesting(by_id)
        self._take_arrows(by_id)

    def _module(self, kind: type, element: BoardElement, abouts: Dict[str, BoardElement]) -> Optional[WhiteboardModule]:
        if element.HOLDS_OTHERS:
            about = abouts.get(element.id.key)
            text = _BoardText(f"**{element.text.strip()}**\n{about.text if about is not None else ''}")
        else:
            text = _BoardText(element.text)
        if not text.name:
            return None
        return kind(name=text.name, sequential_order=len(self._model.modules) + 1).take_text(text)

    def _take_nesting(self, by_id: Dict[str, WhiteboardModule]) -> None:
        """A module depends on the smallest section it sits in, as the drawio channel reads a nested cell."""
        sections = [element for element in self._board.sections if element.id in by_id]
        for element in [*sections, *self._board.shapes]:
            if element.id not in by_id:
                continue
            around = [section for section in sections if section is not element and section.holds(element)]
            if around:
                parent = by_id[min(around, key=lambda section: section.box.w * section.box.h).id]
                self._depend(by_id[element.id], parent.name, "")

    def _take_arrows(self, by_id: Dict[str, WhiteboardModule]) -> None:
        for arrow in self._board.arrows:
            source, target = by_id.get(arrow.from_id), by_id.get(arrow.to_id)
            if source is not None and target is not None:
                self._depend(source, target.name, arrow.label)

    def _depend(self, module: WhiteboardModule, name: str, label: str) -> None:
        if name not in module.dependencies:
            module.dependencies.append(name)
        if label:
            module.dependency_labels[name] = label


class _ClassReader:
    """Reads a class view back: each class card is a class of the module its tag names, or of the page section it
    sits in; a card imported from another module's page only names the class its arrows reach."""

    def __init__(self, model: WhiteboardCleanEngineeringModel, board: Whiteboard) -> None:
        self._model = model
        self._board = board
        self._modules: Dict[str, WhiteboardModule] = {}
        self._classes: Dict[str, WhiteboardClass] = {}
        self._names: Dict[str, str] = {}

    def read(self) -> None:
        pages = [element for element in self._board.sections if element.role == "page"]
        for card in (element for element in self._board.shapes if element.role in ("class", "imported")):
            text = _BoardText(card.text)
            if not text.name:
                continue
            self._names[card.id] = text.name
            if card.role == "class":
                page = next((section.text.strip() for section in pages if section.holds(card)), "")
                self._take_class(card.id, text, text.module or page)
        self._take_arrows()

    def _take_class(self, card_id: str, text: _BoardText, module_name: str) -> None:
        module = self._modules.get(module_name)
        if module is None:
            module = self._modules[module_name] = WhiteboardModule(name=module_name, sequential_order=len(self._modules) + 1)
            self._model.modules.append(module)
        oclass = WhiteboardClass(name=text.name, sequential_order=len(self._classes) + 1).take_text(text)
        module.classes.append(oclass)
        self._classes[card_id] = oclass

    def _take_arrows(self) -> None:
        """Each arrow marks the property it stands for with its kind, as the drawio channel reads its edges."""
        for arrow in self._board.arrows:
            source = self._classes.get(arrow.from_id)
            target_name = self._names.get(arrow.to_id)
            if source is None or target_name is None or arrow.role not in KINDS:
                continue
            if arrow.role == INHERITANCE and target_name not in source.bases:
                source.bases.append(target_name)
            for label in DEPENDENCY_LABEL.findall(arrow.label):
                source.arrows.depend_on(target_name, label.strip())
            source.take_arrow(target_name, arrow.role, arrow.label)
        for oclass in self._classes.values():
            for prop in oclass.properties:
                prop.arrow.derive()
