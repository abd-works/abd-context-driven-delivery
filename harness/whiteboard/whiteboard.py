"""A Claude Whiteboard board as a practice draws it: its elements, its file, and the store writes that update a board.

A board in Claude is a Whiteboard artifact whose store holds ``board/meta`` (``{v, title, order}``) and one
``elements/<id>`` record per element. A practice draws its diagram as a *Whiteboard*, saves it as a ``.whiteboard``
file beside its other formats, and an agent sends ``Whiteboard.batches(previous)`` to the artifact's store.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, fields, replace
from typing import ClassVar, Dict, Iterable, List, Optional

ID_PATTERN = re.compile(r"^[A-Za-z0-9_.~:@+-]{1,40}$")
BATCH_SIZE = 50
"""The most writes the artifact store takes in one batch."""


class UnreadableBoard(ValueError):
    """Text that is not a saved board, so no practice reads a model from it."""


@dataclass(frozen=True)
class Box:
    """Where an element is drawn: its top-left corner, width and height in board units."""

    x: float
    y: float
    w: float
    h: float

    def holds(self, other: "Box") -> bool:
        """Whether other's middle lies inside this box, as a card inside the section drawn round it does."""
        middle_x, middle_y = other.x + other.w / 2, other.y + other.h / 2
        return self.x <= middle_x <= self.x + self.w and self.y <= middle_y <= self.y + self.h


@dataclass
class BoardElement:
    """One record on a board, under its element id; each kind writes the fields the Whiteboard type reads."""

    id: str
    TYPE: ClassVar[str] = ""
    STORE_NAMES: ClassVar[Dict[str, str]] = {
        "from_id": "from", "to_id": "to", "from_side": "fromSide", "to_side": "toSide", "text_align": "textAlign",
    }

    def __post_init__(self) -> None:
        if not ID_PATTERN.match(self.id):
            raise ValueError(f"Element id {self.id!r} is not 1-40 of [A-Za-z0-9_.~:@+-]")

    @property
    def record(self) -> Dict[str, object]:
        """The element as the store keeps it: its type and every field that is set, without its id."""
        written: Dict[str, object] = {"type": self.TYPE}
        for item in fields(self):
            value = getattr(self, item.name)
            if item.name == "id" or value is None or value is False or value == "":
                continue
            written[self.STORE_NAMES.get(item.name, item.name)] = value
        return written

    @classmethod
    def from_record(cls, element_id: str, record: Dict[str, object]) -> "BoardElement":
        """The element a store record holds; a record of a type no practice draws, such as a person's note, is kept as
        an *OtherElement* so a board read back loses nothing."""
        kind = ELEMENT_KINDS.get(str(record.get("type", "")))
        if kind is None:
            return OtherElement(element_id, dict(record))
        field_names = {store: name for name, store in cls.STORE_NAMES.items()}
        known = {item.name for item in fields(kind)}
        values = {field_names.get(name, name): value for name, value in record.items()}
        return kind(id=element_id, **{name: value for name, value in values.items() if name in known and name != "id"})

    @property
    def place(self) -> Optional[Box]:
        """Where a person sees the element; none for an element placed by what it joins."""
        return None


@dataclass
class Label(BoardElement):
    """Words with no box, such as a board's title; the board sizes it from its text."""

    TYPE: ClassVar[str] = "text"
    x: float = 0
    y: float = 0
    text: str = ""
    size: str = ""
    wrap: float = 0

    @property
    def place(self) -> Optional[Box]:
        return Box(self.x, self.y, 0, 0)

    def placed_at(self, place: Box) -> "Label":
        return replace(self, x=place.x, y=place.y)


@dataclass
class Block(BoardElement):
    """An element with a box of its own, a colour and words."""

    x: float = 0
    y: float = 0
    w: float = 0
    h: float = 0
    color: str = ""
    text: str = ""

    @property
    def place(self) -> Optional[Box]:
        return Box(self.x, self.y, self.w, self.h)

    def placed_at(self, place: Box) -> "Block":
        return replace(self, x=place.x, y=place.y, w=place.w, h=place.h)


@dataclass
class Shape(Block):
    """A block: an epic bar, a story card, a class or module box."""

    TYPE: ClassVar[str] = "shape"
    kind: str = "rect"
    stroke: str = ""
    size: str = ""
    text_align: str = ""


@dataclass
class Section(Block):
    """A container that holds other elements under its title; it lies behind what it holds."""

    TYPE: ClassVar[str] = "container"


@dataclass
class Arrow(BoardElement):
    """A line from one element to another, by their ids."""

    TYPE: ClassVar[str] = "arrow"
    from_id: str = ""
    to_id: str = ""
    from_side: str = ""
    to_side: str = ""
    label: str = ""
    dash: bool = False
    head: str = ""


@dataclass
class OtherElement(BoardElement):
    """A record of a type no practice draws, such as a note, sticker or embed a person added; kept as it was read."""

    fields_read: Dict[str, object] = field(default_factory=dict)

    @property
    def record(self) -> Dict[str, object]:
        return dict(self.fields_read)


ELEMENT_KINDS: Dict[str, type] = {kind.TYPE: kind for kind in (Shape, Section, Label, Arrow)}
"""The element kinds a practice draws, by the type the store names them with."""


@dataclass(frozen=True)
class StoreWrite:
    """One write to the Whiteboard artifact's store: ``set`` a record, ``update`` its changed fields, or ``delete`` it."""

    action: str
    key: str
    data: Optional[Dict[str, object]] = None

    @property
    def entry(self) -> Dict[str, object]:
        """The write as one entry of an ArtifactData ``batch``."""
        written: Dict[str, object] = {"action": self.action, "key": self.key}
        if self.data is not None:
            written["data"] = self.data
        return written


class WhiteboardNode:
    """What a practice's diagram node mixes in to be drawn on a board. The node says the box it is drawn in and the
    elements it draws there; the board places them back to front as the nodes are drawn."""

    def board_box(self) -> Box:
        """The box the diagram placed this node in."""
        raise NotImplementedError

    def board_elements(self) -> List[BoardElement]:
        """The elements this node draws, back to front."""
        raise NotImplementedError

    def board_shape(self, element_id: str, **drawn: str) -> Shape:
        """A shape with this element id at this node's box."""
        box = self.board_box()
        return Shape(element_id, x=box.x, y=box.y, w=box.w, h=box.h, **drawn)


class Whiteboard:
    """A board: its title and its elements in back-to-front order."""

    SUFFIX = ".whiteboard"

    def __init__(self, title: str = "", elements: Iterable[BoardElement] = ()) -> None:
        self.title = title
        self._elements: Dict[str, BoardElement] = {}
        for element in elements:
            self.add(element)

    @property
    def elements(self) -> List[BoardElement]:
        return list(self._elements.values())

    @property
    def order(self) -> List[str]:
        return list(self._elements)

    def add(self, element: BoardElement) -> BoardElement:
        """Put element in front of every element already on the board; a section goes behind every element but other
        sections, so it never covers what it holds."""
        if element.id in self._elements:
            raise ValueError(f"The board already holds an element {element.id!r}")
        if not isinstance(element, Section):
            self._elements[element.id] = element
            return element
        sections = {key: held for key, held in self._elements.items() if isinstance(held, Section)}
        rest = {key: held for key, held in self._elements.items() if key not in sections}
        self._elements = {**sections, element.id: element, **rest}
        return element

    def put(self, element: BoardElement) -> BoardElement:
        """Put element in place of the element with its id, where that one lay; a new id is added as ``add`` adds."""
        if element.id not in self._elements:
            return self.add(element)
        self._elements[element.id] = element
        return element

    def draw(self, node: WhiteboardNode) -> None:
        """Add every element node draws."""
        for element in node.board_elements():
            self.add(element)

    def element(self, element_id: str) -> Optional[BoardElement]:
        return self._elements.get(element_id)

    @property
    def meta(self) -> Dict[str, object]:
        return {"v": 1, "title": self.title, "order": self.order}

    def save(self) -> str:
        """The board as a ``.whiteboard`` file: its meta and every element's record."""
        board = dict(self.meta)
        board["elements"] = {element.id: element.record for element in self.elements}
        return json.dumps(board, indent=1, ensure_ascii=False)

    @classmethod
    def load(cls, text: str) -> "Whiteboard":
        """The board a ``.whiteboard`` file holds, or a store read of ``board/meta`` and ``elements`` saved as one."""
        try:
            board = json.loads(text)
        except (TypeError, ValueError) as error:
            raise UnreadableBoard(f"Not a whiteboard file: {error}") from error
        if not isinstance(board, dict) or not isinstance(board.get("elements"), dict):
            raise UnreadableBoard("Not a whiteboard file: it holds no elements")
        records = board["elements"]
        order = [key for key in board.get("order", []) if key in records]
        order += [key for key in records if key not in order]
        loaded = cls(str(board.get("title", "")))
        for key in order:
            loaded._elements[key] = BoardElement.from_record(key, records[key])
        return loaded

    def keep_places(self, previous: Optional["Whiteboard"]) -> "Whiteboard":
        """This board with every element previous also held put back where it was on previous, so a place a person
        moved an element to survives the next render; new elements stay where the render put them."""
        for key, element in list(self._elements.items()):
            before = previous.element(key) if previous is not None else None
            if before is not None and before.place is not None and type(before) is type(element):
                self._elements[key] = element.placed_at(before.place)
        return self

    def writes(self, previous: Optional["Whiteboard"] = None) -> List[StoreWrite]:
        """The store writes that turn previous, the board as it is in Claude, into this board: its meta, each new
        element set, each changed element updated with only its changed fields, and each element a practice drew that
        this board no longer holds deleted. Elements a person added, of a kind no practice draws, are left alone and
        kept at the back of the order."""
        before = previous or Whiteboard()
        kept = [element.id for element in before.elements if isinstance(element, OtherElement)]
        meta = {**self.meta, "order": kept + self.order}
        return [StoreWrite("set", "board/meta", meta), *self._element_writes(before), *self._deletes(before)]

    def batches(self, previous: Optional["Whiteboard"] = None) -> List[List[Dict[str, object]]]:
        """The writes against previous as ArtifactData ``batch`` entries, at most fifty a batch, in order."""
        entries = [write.entry for write in self.writes(previous)]
        return [entries[start:start + BATCH_SIZE] for start in range(0, len(entries), BATCH_SIZE)]

    def _element_writes(self, before: "Whiteboard") -> List[StoreWrite]:
        found: List[StoreWrite] = []
        for element in self.elements:
            had = before.element(element.id)
            if had is None:
                found.append(StoreWrite("set", f"elements/{element.id}", element.record))
                continue
            changed = {name: value for name, value in element.record.items() if had.record.get(name) != value}
            if changed:
                found.append(StoreWrite("update", f"elements/{element.id}", changed))
        return found

    def _deletes(self, before: "Whiteboard") -> List[StoreWrite]:
        return [
            StoreWrite("delete", f"elements/{element.id}") for element in before.elements
            if self.element(element.id) is None and not isinstance(element, OtherElement)
        ]
