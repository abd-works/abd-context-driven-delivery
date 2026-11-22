"""Claude Whiteboard channel - a mockup drawn as a board, and the UX map a board reads back as.

Each screen is a section titled with its name. Inside it sit a card of what the screen serves (its stories, scenarios,
and steps, then its domain terms), and one section for each region, which holds a card for each control: the control's
name, its type, and the stories, scenarios, and steps it serves. A story, scenario, or step is written as the other
formats write it: a markdown link to the file and heading it is written at, or its key. A transition is an arrow from
its screen to the screen it goes to, labelled with its trigger.

Each element's id names what it draws (``screen.<key>``, ``region.<area>.<key>``, ``control.<key>``,
``serves.<key>``, ``transition.<key>``), where the key is a hash of the node's path, so a node keeps its id from one
render to the next. A board is read back by where its elements sit, because people move cards on a shared board: a
control belongs to the region its card sits in, and a region to the screen it sits in. The board draws no state,
interaction, or description.
"""

from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path
from typing import List, Optional

from harness.whiteboard import BoardElement, Box, Whiteboard, WhiteboardNode

from cdd_guidance.practices.ux.model.nodes import Control, Region, Screen, ServesStories, StoryDemoControl, Transition
from cdd_guidance.practices.ux.model.ux_map import UxMap
from cdd_guidance.practices.ux.model.ux_node import UxNode
from harness.guidance.practice_formats import Written

KEY_LENGTH = 10
"""Hex digits of a node's path hash in its element id: enough that two nodes of one map never share one."""
# What joins the things one line lists: the stories a card shows, the domain terms of a screen.
_BESIDE = " · "
# The heading each kind of thing served is listed under, in the order a card lists them.
_SERVED_HEADINGS = (("Stories", "Story"), ("Scenarios", "Scenario"), ("Steps", "Step"))
_TERMS_HEADING = "Domain terms"
_SERVES_TITLE = "**Serves**"
# A card's name line, `**Quantity**`, and its type line, `*number*`.
_BOLD = re.compile(r"^\*\*(?P<words>.+)\*\*$")
_ITALIC = re.compile(r"^\*(?P<words>[^*]+)\*$")
# A markdown link, which a card shows as its text alone.
_LINK = re.compile(r"\[([^\]]+)\]\([^)\s]+\)")
# An area a region's id can carry as it is; any other is not kept.
_AREA_IN_ID = re.compile(r"^[A-Za-z0-9_-]{1,16}$")
_NO_AREA = "-"
# A transition's label that names its kind of navigation before its trigger: `[top nav] Check out`.
_NAV_LABEL = re.compile(r"^\[(?P<nav>[^\]]+)\]\s*(?P<trigger>.*)$")
_ACTION, _TAB = "action", "tab"

SCREEN_WIDTH = 480
SCREEN_GAP = 96
INSET = 24
TITLE_HEIGHT = 56
"""The space a section leaves above what it holds, for its title."""
CARD_GAP = 12
LINE_HEIGHT = 24
CARD_PAD = 24
CHARACTERS_PER_LINE = 46
"""How many characters of the board's small text fit on one line of a control's card."""
EMPTY_REGION_HEIGHT = 72


class DrawnNode(UxNode, WhiteboardNode):
    """A node of the map drawn on a board: keyed by its path from the map, and placed in the box the board's layout
    gave it."""

    box = Box(0, 0, 0, 0)

    @property
    def board_key(self) -> str:
        names: List[str] = []
        node: Optional[UxNode] = self
        while node is not None and not isinstance(node, UxMap):
            names.append(f"{node.semantic_type()}:{node.name}")
            node = node.parent
        return hashlib.sha1("/".join(reversed(names)).encode("utf-8")).hexdigest()[:KEY_LENGTH]

    def board_box(self) -> Box:
        return self.box


class ServedOnCard(ServesStories):
    """What a screen or a control serves as a card lists it: one line for each kind, `Stories: ...`, each thing a
    markdown link when it has a target."""

    def served_lines(self) -> List[str]:
        listed = ((heading, self._keys(kind)) for heading, kind in _SERVED_HEADINGS)
        return [f"{heading}: {_BESIDE.join(keys)}" for heading, keys in listed if keys]

    def read_served_lines(self, lines: List[str]) -> None:
        """Serve each story, scenario, and step lines list under its heading."""
        for heading, kind in _SERVED_HEADINGS:
            for item in _listed(lines, heading):
                self._show(kind, item)


class WhiteboardControl(Control, ServedOnCard, DrawnNode):
    """A control's card: its name, its type, and what it serves."""

    @property
    def card_text(self) -> str:
        kind = [f"*{self.control_type}*"] if self.control_type else []
        return "\n".join([f"**{self.name}**", *kind, *self.served_lines()])

    @property
    def height(self) -> float:
        return _card_height(self.card_text)

    def board_elements(self) -> List[BoardElement]:
        return [self.board_shape(f"control.{self.board_key}", kind="rounded", color="yellow", size="small", text_align="left", text=self.card_text)]

    @classmethod
    def from_card(cls, card: BoardElement, order: int) -> "WhiteboardControl":
        """The control a card draws: named by its first line, typed by a line in italics, serving what its other
        lines list."""
        lines = _lines_of(card.text)
        name = _BOLD.match(lines[0]) if lines else None
        control = cls(name.group("words") if name else (lines[0] if lines else f"Control {order}"), order)
        kind = next((found for found in (_ITALIC.match(line) for line in lines[1:]) if found), None)
        control.control_type = kind.group("words").strip() if kind else ""
        control.read_served_lines(lines[1:])
        return control


class WhiteboardStoryDemoControl(StoryDemoControl, WhiteboardControl):
    """A Story Demo control's card, drawn as any control's: the board draws no story step a control runs."""


class WhiteboardRegion(Region, DrawnNode):
    """A region's section, which holds its controls' cards one under another."""

    @property
    def height(self) -> float:
        cards = [control.height for control in self.controls]
        if not cards:
            return EMPTY_REGION_HEIGHT
        return TITLE_HEIGHT + sum(cards) + CARD_GAP * (len(cards) - 1) + INSET

    def lay_out(self, box: Box) -> None:
        """Take box, and give each control a box of its own inside it."""
        self.box = box
        top = box.y + TITLE_HEIGHT
        for control in self.controls:
            control.box = Box(box.x + INSET, top, box.w - 2 * INSET, control.height)
            top += control.height + CARD_GAP

    def board_elements(self) -> List[BoardElement]:
        area = self.area if _AREA_IN_ID.match(self.area or "") else _NO_AREA
        section = BoardElement.section(f"region.{area}.{self.board_key}", self.box, color="white", text=self.name)
        return [section, *(element for control in self.controls for element in control.board_elements())]

    @classmethod
    def from_section(cls, section: BoardElement, order: int) -> "WhiteboardRegion":
        region = cls(section.text.strip() or f"Region {order}", order)
        area = section.id.split(".")[1] if section.id.count(".") >= 2 else _NO_AREA
        region.area = "" if area == _NO_AREA else area
        return region


class WhiteboardScreen(Screen, ServedOnCard, DrawnNode):
    """A screen's section: the card of what the screen serves, then its regions one under another."""

    _serves_box = Box(0, 0, 0, 0)
    """Where the card of what the screen serves is drawn, once the screen is laid out."""

    @property
    def serves_text(self) -> str:
        """The words of the card of what this screen serves and names; none for a screen that serves and names
        nothing."""
        terms = list(self.domain_terms or self.domain_concepts)
        lines = [*self.served_lines(), *([f"{_TERMS_HEADING}: {_BESIDE.join(terms)}"] if terms else [])]
        return "\n".join([_SERVES_TITLE, *lines]) if lines else ""

    @property
    def height(self) -> float:
        parts = [*([_card_height(self.serves_text)] if self.serves_text else []), *(region.height for region in self.regions)]
        return TITLE_HEIGHT + sum(parts) + CARD_GAP * max(0, len(parts) - 1) + INSET

    def lay_out(self, left: float, top: float) -> None:
        """Take the box at left and top, and give the card of what this screen serves and each region a box inside it."""
        self.box = Box(left, top, SCREEN_WIDTH, self.height)
        inner_left, inner_width, next_top = left + INSET, SCREEN_WIDTH - 2 * INSET, top + TITLE_HEIGHT
        self._serves_box = Box(inner_left, next_top, inner_width, _card_height(self.serves_text))
        if self.serves_text:
            next_top += self._serves_box.h + CARD_GAP
        for region in self.regions:
            region.lay_out(Box(inner_left, next_top, inner_width, region.height))
            next_top += region.height + CARD_GAP

    def board_elements(self) -> List[BoardElement]:
        drawn = [BoardElement.section(f"screen.{self.board_key}", self.box, color="blue", text=self.name)]
        if self.serves_text:
            drawn.append(BoardElement.shape(f"serves.{self.board_key}", self._serves_box, kind="rounded", color="green", size="small", text_align="left", text=self.serves_text))
        return [*drawn, *(element for region in self.regions for element in region.board_elements())]

    def read_serves_card(self, card: BoardElement) -> None:
        """Serve what the card lists, and attach each domain term it lists."""
        lines = _lines_of(card.text)
        self.read_served_lines(lines)
        for term in _listed(lines, _TERMS_HEADING):
            self.attach_domain_term(term)


class WhiteboardTransition(Transition, DrawnNode):
    """A transition's arrow, from its screen to the screen it goes to, labelled with its trigger; a transition that is
    no action names its kind of navigation first, as a sketch does: `[top nav] Check out`."""

    def board_elements(self) -> List[BoardElement]:
        if not isinstance(self.from_screen, WhiteboardScreen) or not isinstance(self.to_screen, WhiteboardScreen):
            return []
        label = self.trigger if self.nav_type in (_ACTION, _TAB, "") else f"[{self.nav_type}] {self.trigger}"
        key = hashlib.sha1(f"{self.from_screen.name}/{self.to_screen.name}/{self.trigger}".encode("utf-8")).hexdigest()[:KEY_LENGTH]
        return [BoardElement.arrow(
            f"transition.{key}", from_id=f"screen.{self.from_screen.board_key}", to_id=f"screen.{self.to_screen.board_key}",
            label=label, dash=self.nav_type == _TAB, head="arrow",
        )]

    def read_arrow(self, arrow: BoardElement) -> None:
        """Take the arrow's trigger and kind of navigation: the kind its label names, else a tab for a dashed arrow."""
        named = _NAV_LABEL.match(arrow.label.strip())
        self.trigger = named.group("trigger").strip() if named else arrow.label.strip()
        self.nav_type = named.group("nav").strip() if named else (_TAB if arrow.dash else _ACTION)


class WhiteboardUxMap(UxMap):
    """The ``whiteboard`` format of a UX map: render draws the map on a board, parse reads one back."""

    screen_type = WhiteboardScreen
    region_type = WhiteboardRegion
    control_type = WhiteboardControl
    story_demo_control_type = WhiteboardStoryDemoControl
    transition_type = WhiteboardTransition
    map_file_suffixes = (Whiteboard.SUFFIX,)
    first_left = 80
    first_top = 120

    def reads_file(self, file: Path, text: str) -> bool:
        """A board that draws a UX screen; any other board is another practice's, such as a story map."""
        return '"screen.' in text

    def render(self, canonical: UxMap, written: Written = Written()) -> str:
        """canonical drawn as a board. Drawn over a previous board, it loses nothing that board holds: each element
        stays where people put it, a card keeps the stories, scenarios, and steps a person wrote on it beside what
        canonical's control serves, and every element canonical does not draw (a card or a screen a person added or
        canonical has since lost, a note stuck on the board) stays as it was."""
        drawn = self.copy_of(canonical)
        if not written.previous:
            return drawn.board().save()
        before = Whiteboard.from_text(written.previous)
        if any(element.role == "screen" for element in before.sections):
            drawn.keep_served_by(self.parse(written.previous))
        board = drawn.board().keep_places(before)
        for element in before.elements:
            if board.element(element.id) is None:
                board.add(element)
        return board.save()

    def save(self) -> str:
        return self.board().save()

    def board(self) -> Whiteboard:
        """This map as a board: its screens side by side, then its transitions."""
        board = Whiteboard(self.name)
        left = self.first_left
        for screen in self.screens:
            screen.lay_out(left, self.first_top)
            board.draw(screen)
            left += SCREEN_WIDTH + SCREEN_GAP
        for transition in self.transitions:
            board.draw(transition)
        return board

    def parse(self, text: str, file: str = "") -> UxMap:
        """A new map of this format, read from a board's text by where its elements sit."""
        ux_map = type(self).create()
        ux_map._take_board(Whiteboard.from_text(text).holding({"screen"}, "UX screen"))
        return ux_map

    def _take_board(self, board: Whiteboard) -> None:
        """Read board into this map: its screens left to right, each with the regions that sit in it and the controls
        that sit in each region, what each serves, and the arrows between screens as transitions."""
        self.name = board.title.strip() or self.name
        drawn = _Drawn(board)
        with self.batch_schema_sync():
            screens: dict[str, WhiteboardScreen] = {}
            for section in drawn.sections("screen"):
                screen = self.screen_type(section.text.strip() or f"Screen {len(self.screens)}", len(self.screens))
                self.append_screen(screen)
                screens[section.id] = screen
                self._read_screen(screen, section, drawn)
            for arrow in (arrow for arrow in board.arrows if arrow.role == "transition"):
                origin, target = screens.get(arrow.from_id), screens.get(arrow.to_id)
                if origin is not None and target is not None:
                    transition = self.transition_type(arrow.label.strip(), len(self.transitions)).joining(origin, target)
                    transition.read_arrow(arrow)
                    transition.name = transition.trigger
                    self.transitions.append(transition)

    def _read_screen(self, screen: WhiteboardScreen, section: BoardElement, drawn: "_Drawn") -> None:
        for card in drawn.held_by(section, drawn.shapes("serves")):
            screen.read_serves_card(card)
        for region_section in drawn.held_by(section, drawn.sections("region")):
            region = self.region_type.from_section(region_section, len(screen.regions))
            for card in drawn.held_by(region_section, drawn.shapes("control")):
                region.append_control(self.control_type.from_card(card, len(region.controls)))
            screen.append_region(region)


class _Drawn:
    """A board's elements by what each draws, in reading order: left to right for screens, top to bottom inside one."""

    def __init__(self, board: Whiteboard) -> None:
        self._sections = board.sections
        self._shapes = board.shapes

    def sections(self, role: str) -> List[BoardElement]:
        found = [section for section in self._sections if section.role == role]
        return sorted(found, key=lambda section: (section.box.x, section.box.y) if role == "screen" else (section.box.y, section.box.x))

    def shapes(self, role: str) -> List[BoardElement]:
        return sorted((shape for shape in self._shapes if shape.role == role), key=lambda shape: (shape.box.y, shape.box.x))

    def held_by(self, section: BoardElement, elements: List[BoardElement]) -> List[BoardElement]:
        """The elements whose middle sits inside section."""
        return [element for element in elements if section.holds(element)]


def _lines_of(text: str) -> List[str]:
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


def _listed(lines: List[str], heading: str) -> List[str]:
    """What the line that starts with heading lists after it; nothing when no line does."""
    start = f"{heading.lower()}:"
    line = next((line for line in lines if line.lower().startswith(start)), "")
    return [item.strip() for item in line[len(start):].split(_BESIDE) if item.strip()]


def _card_height(text: str) -> float:
    """How tall a card of text is drawn: a line for every line of its words, and one more each time a line is longer
    than a card is wide. A link takes the room of its text alone."""
    shown = [_LINK.sub(r"\1", line) for line in text.splitlines()]
    return CARD_PAD + LINE_HEIGHT * sum(max(1, math.ceil(len(line) / CHARACTERS_PER_LINE)) for line in shown)
