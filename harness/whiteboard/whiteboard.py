"""A Claude Whiteboard board as a practice draws it: its elements, its file, and the store writes that update a board.

A board in Claude is a Whiteboard artifact whose store holds ``board/meta`` (``{v, title, order}``) and one
``elements/<id>`` record per element. A practice draws its diagram as a *Whiteboard*, saves it as a ``.whiteboard``
file beside its other formats, and an agent sends ``Whiteboard.writes(previous)`` to the artifact's store.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, fields, replace
from typing import ClassVar, Dict, Iterable, List, Optional, Tuple

ID_PATTERN = re.compile(r"^[A-Za-z0-9_.~:@+-]{1,40}$")
BATCH_SIZE = 50
"""The most writes the artifact store takes in one batch."""

Box = Tuple[float, float, float, float]
"""Where a node is drawn: x, y, width, height."""


class UnreadableBoard(ValueError):
    """Text that is not a saved board, so no practice reads a model from it."""


@dataclass
class BoardElement:
    """One record on a board, under its element id; each kind writes the fields the Whiteboard type reads."""

    id: str
    TYPE: ClassVar[str] = ""
    KINDS: ClassVar[Dict[str, type]] = {}

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if cls.TYPE:
            BoardElement.KINDS[cls.TYPE] = cls

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
            written[_store_name(item.name)] = value
        return written

    @classmethod
    def from_record(cls, element_id: str, record: Dict[str, object]) -> "BoardElement":
        """The element a store record holds; a record of a type no practice draws, such as a person's note, is kept as
        an *OtherElement* so a board read back loses nothing."""
        kind = cls.KINDS.get(str(record.get("type", "")))
        if kind is None:
            return OtherElement(element_id, dict(record))
        known = {item.name for item in fields(kind)}
        values = {_field_name(name): value for name, value in record.items() if _field_name(name) in known}
        return kind(id=element_id, **values)

    @property
    def place(self) -> Optional[Box]:
        """Where a person sees the element; none for an element placed by what it joins."""
        return None

    def placed_at(self, place: Box) -> "BoardElement":
        return self


@dataclass
class Placed(BoardElement):
    """An element with a box of its own."""

    x: float = 0
    y: float = 0
    w: float = 0
    h: float = 0

    @property
    def place(self) -> Optional[Box]:
        return (self.x, self.y, self.w, self.h)

    def placed_at(self, place: Box) -> "BoardElement":
        x, y, w, h = place
        return replace(self, x=x, y=y, w=w, h=h)


@dataclass
class Shape(Placed):
    """A block: an epic bar, a story card, a class or module box."""

    TYPE: ClassVar[str] = "shape"
    kind: str = "rect"
    color: str = ""
    stroke: str = ""
    size: str = ""
    text: str = ""
    text_align: str = ""


@dataclass
class Section(Placed):
    """A container that holds other elements under its title; it lies behind what it holds."""

    TYPE: ClassVar[str] = "container"
    color: str = ""
    text: str = ""


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
        return (self.x, self.y, 0, 0)

    def placed_at(self, place: Box) -> "BoardElement":
        return replace(self, x=place[0], y=place[1])


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

    @property
    def joins(self) -> Tuple[str, str]:
        return (self.from_id, self.to_id)


@dataclass
class OtherElement(BoardElement):
    """A record of a type no practice draws, such as a note, sticker or embed a person added; kept as it was read."""

    fields_read: Dict[str, object] = field(default_factory=dict)

    @property
    def record(self) -> Dict[str, object]:
        return dict(self.fields_read)


_STORE_NAMES = {"from_id": "from", "to_id": "to", "from_side": "fromSide", "to_side": "toSide", "text_align": "textAlign"}
_FIELD_NAMES = {store: name for name, store in _STORE_NAMES.items()}


def _store_name(name: str) -> str:
    return _STORE_NAMES.get(name, name)


def _field_name(name: str) -> str:
    return _FIELD_NAMES.get(name, name)


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
    """What a practice's diagram node mixes in to be drawn on a board. The node says the box it is drawn in, its element
    id, and the elements it draws there; the board places them back to front as the nodes are drawn."""

    def board_box(self) -> Box:
        """The box the diagram placed this node in."""
        raise NotImplementedError

    def board_elements(self) -> List[BoardElement]:
        """The elements this node draws, back to front."""
        raise NotImplementedError

    def board_shape(self, element_id: str, **drawn) -> Shape:
        """A shape with this element id at this node's box."""
        x, y, w, h = self.board_box()
        return Shape(element_id, x=x, y=y, w=w, h=h, **drawn)


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
        if isinstance(element, Section):
            sections = [key for key, held in self._elements.items() if isinstance(held, Section)]
            rest = [key for key in self._elements if key not in sections]
            ordered = {key: self._elements[key] for key in sections}
            ordered[element.id] = element
            ordered.update({key: self._elements[key] for key in rest})
            self._elements = ordered
        else:
            self._elements[element.id] = element
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
        if previous is None:
            return self
        for key, element in self._elements.items():
            before = previous.element(key)
            if before is not None and before.place is not None and type(before) is type(element):
                self._elements[key] = element.placed_at(before.place)
        return self

    def writes(self, previous: Optional["Whiteboard"] = None) -> List[StoreWrite]:
        """The store writes that turn previous, the board as it is in Claude, into this board: its meta, each new
        element set, each changed element updated with only its changed fields, and each element previous held that a
        practice drew and this board no longer holds deleted. Elements a person added, of a kind no practice draws, are
        left alone and kept in the order."""
        before = previous or Whiteboard()
        kept = [element for element in before.elements if isinstance(element, OtherElement)]
        found: List[StoreWrite] = []
        for element in self.elements:
            had = before.element(element.id)
            if had is None:
                found.append(StoreWrite("set", f"elements/{element.id}", element.record))
                continue
            changed = {name: value for name, value in element.record.items() if had.record.get(name) != value}
            if changed:
                found.append(StoreWrite("update", f"elements/{element.id}", changed))
        for element in before.elements:
            if self.element(element.id) is None and not isinstance(element, OtherElement):
                found.append(StoreWrite("delete", f"elements/{element.id}"))
        meta = dict(self.meta)
        meta["order"] = [element.id for element in kept] + self.order
        return [StoreWrite("set", "board/meta", meta)] + found

    @staticmethod
    def batches(writes: List[StoreWrite]) -> List[List[Dict[str, object]]]:
        """The writes as ArtifactData ``batch`` entries, at most fifty a batch, in order."""
        entries = [write.entry for write in writes]
        return [entries[start:start + BATCH_SIZE] for start in range(0, len(entries), BATCH_SIZE)]
