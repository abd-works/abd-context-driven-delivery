"""A Claude Whiteboard board as a practice draws it: its elements, its file, and the store writes that update a board.

A board in Claude is a Whiteboard artifact whose store holds ``board/meta`` (``{v, title, order}``) and one
``elements/<id>`` record per element. A practice draws its diagram as a *Whiteboard*, saves it as a ``.whiteboard``
file beside its other formats, and an agent sends ``Whiteboard.batches(previous)`` to the artifact's store.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from dataclasses import dataclass, field, fields, replace
from typing import ClassVar, Collection, Dict, Iterable, List, Optional

ID_PATTERN = re.compile(r"^[A-Za-z0-9_.~:@+-]{1,40}$")
BATCH_SIZE = 50
"""The most writes the artifact store takes in one batch."""
MAX_SIDE = 8000
"""The widest or tallest block a board draws; the Whiteboard page draws a block over it at its default size."""
CLEARED = {"__delete__": True}
"""What an update writes for a field the element no longer has, so the store drops it."""
PIECE_MARK = "~"
"""What joins a block's id to the number of each further piece of it."""
DrawnField = str | float | bool | list[str | float] | None
"""What one drawn field of an element holds: its words, colour or size, a measure, a flag such as an arrow's dash, or
the list of an arrow's heads or bends."""


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
    HOLDS_OTHERS: ClassVar[bool] = False
    """Whether the element is a container drawn round other elements, so it lies behind them."""
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
    def shape(cls, element_id: str, box: Box, **drawn: DrawnField) -> "BoardElement":
        """A block drawn in box: an epic bar, a story card, a class or module box."""
        return Shape(element_id, box=box, **drawn)

    @classmethod
    def section(cls, element_id: str, box: Box, **drawn: DrawnField) -> "BoardElement":
        """A container drawn in box, titled with its text, that holds the elements drawn inside it."""
        return Section(element_id, box=box, **drawn)

    @classmethod
    def words(cls, element_id: str, corner: Box, **drawn: DrawnField) -> "BoardElement":
        """A label: words with no box, starting at corner's top left; the board sizes it from its text."""
        return Label(element_id, x=corner.x, y=corner.y, **drawn)

    @classmethod
    def arrow(cls, element_id: str, **drawn: DrawnField) -> "BoardElement":
        """A line from the element ``from_id`` names to the one ``to_id`` names."""
        return Arrow(element_id, **drawn)

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
        if "box" in known:
            values["box"] = Box(*(float(values.pop(edge, 0)) for edge in ("x", "y", "w", "h")))
        return kind(id=element_id, **{name: value for name, value in values.items() if name in known and name != "id"})

    @property
    def role(self) -> str:
        """What the element draws, as the first part of its id names it: ``story`` for ``story.user.a1``."""
        return self.id.split(".", 1)[0]

    @property
    def whole_id(self) -> str:
        """The id of the element this one is a piece of; its own id when it is whole."""
        return self.id.split(PIECE_MARK, 1)[0]

    def pieces(self) -> List["BoardElement"]:
        """The elements a board draws this one as: itself, unless it is too big for one."""
        return [self]

    def joined(self, piece: "BoardElement") -> "BoardElement":
        """This element with another piece of it joined on; an element in no pieces is itself."""
        return self

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
    wrap: Optional[float] = None
    """The width the words wrap at; none, so they run on one line. A wrap of 0 would set every word on a line of its
    own, so a label that wraps nowhere writes none."""

    @property
    def place(self) -> Optional[Box]:
        return Box(self.x, self.y, 0, 0)

    def placed_at(self, place: Box) -> "Label":
        return replace(self, x=place.x, y=place.y)


@dataclass
class Block(BoardElement):
    """An element with a box of its own, a colour and words. The store keeps its box as four flat fields."""

    box: Box = Box(0, 0, 0, 0)
    color: str = ""
    text: str = ""

    @property
    def record(self) -> Dict[str, object]:
        written = super().record
        del written["box"]
        return {**written, "x": self.box.x, "y": self.box.y, "w": self.box.w, "h": self.box.h}

    @property
    def place(self) -> Optional[Box]:
        return self.box

    def placed_at(self, place: Box) -> "Block":
        return replace(self, box=place)

    def holds(self, other: "Block") -> bool:
        """Whether other sits inside this block, as a card inside the section drawn round it does."""
        return self.box.holds(other.box)

    def pieces(self) -> List[BoardElement]:
        """This block as the board draws it: a board draws no block wider than MAX_SIDE, so a wider one, such as the bar
        of an epic over many stories, is cut into equal pieces side by side, the first under the block's own id with its
        words and the rest under ``<id>~2``, ``<id>~3``, ... with none, so the words show once."""
        if self.box.h > MAX_SIDE:
            raise ValueError(f"Element {self.id!r} is {self.box.h} tall; a board draws none taller than {MAX_SIDE}")
        count = math.ceil(self.box.w / MAX_SIDE)
        if count <= 1:
            return [self]
        width = self.box.w / count
        return [
            replace(self, id=self.id if index == 0 else f"{self.id}{PIECE_MARK}{index + 1}",
                    box=Box(self.box.x + index * width, self.box.y, width, self.box.h), text=self.text if index == 0 else "")
            for index in range(count)
        ]

    def joined(self, piece: BoardElement) -> "Block":
        """This block stretched over another piece of it."""
        if not isinstance(piece, Block):
            return self
        left, top = min(self.box.x, piece.box.x), min(self.box.y, piece.box.y)
        right = max(self.box.x + self.box.w, piece.box.x + piece.box.w)
        bottom = max(self.box.y + self.box.h, piece.box.y + piece.box.h)
        return replace(self, id=self.whole_id, box=Box(left, top, right - left, bottom - top))


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
    HOLDS_OTHERS: ClassVar[bool] = True


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
    heads: Optional[List[str]] = None
    """What each end draws, from end first: ``none``, ``arrow`` or ``circle``."""
    bends: Optional[List[str | float]] = None
    """The route the arrow takes: the way it leaves its first element (``h`` or ``v``), then where each middle leg runs,
    the first half from the middle of the element it leaves, the rest from the middle of the one it reaches."""


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
    """One write to the Whiteboard artifact's store: ``set`` a record, ``update`` its changed fields, or ``delete`` it.
    A write to a record the board already holds is pinned to the version it was read at, so it writes nothing when a
    person changed the record since."""

    op: str
    collection: str
    doc_id: str
    data: Optional[Dict[str, object]] = None
    if_version: Optional[int] = None

    @property
    def entry(self) -> Dict[str, object]:
        """The write as one entry of an ArtifactData ``batch``."""
        written: Dict[str, object] = {"op": self.op, "collection": self.collection, "doc_id": self.doc_id}
        if self.data is not None:
            written["data"] = self.data
        if self.if_version is not None:
            written["if_version"] = self.if_version
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

    def board_shape(self, element_id: str, **drawn: DrawnField) -> BoardElement:
        """A shape with this element id at this node's box."""
        return BoardElement.shape(element_id, self.board_box(), **drawn)


class Whiteboard:
    """A board: its title and its elements in back-to-front order."""

    SUFFIX = ".whiteboard"

    def __init__(self, title: str = "", elements: Iterable[BoardElement] = ()) -> None:
        self.title = title
        # The store version each record was read at, by element id and ``meta``; a board drawn by a practice has none.
        self._versions: Dict[str, int] = {}
        self._elements: Dict[str, BoardElement] = {}
        for element in elements:
            self.add(element)

    @property
    def elements(self) -> List[BoardElement]:
        return list(self._elements.values())

    @property
    def order(self) -> List[str]:
        return list(self._elements)

    @property
    def whole_elements(self) -> List[BoardElement]:
        """The elements as a practice drew them: a block written as several pieces, because it is wider than a board
        draws one, is one block again, spanning all its pieces."""
        wholes: Dict[str, BoardElement] = {}
        for element in self.elements:
            whole = element.whole_id
            wholes[whole] = element if whole not in wholes else wholes[whole].joined(element)
        return list(wholes.values())

    @property
    def sections(self) -> List[BoardElement]:
        """The whole containers on the board, back to front."""
        return self._whole_of(Section)

    @property
    def shapes(self) -> List[BoardElement]:
        """The whole blocks on the board that are no container, back to front."""
        return self._whole_of(Shape)

    @property
    def labels(self) -> List[BoardElement]:
        return self._whole_of(Label)

    @property
    def arrows(self) -> List[BoardElement]:
        return self._whole_of(Arrow)

    def _whole_of(self, kind: type) -> List[BoardElement]:
        return [element for element in self.whole_elements if isinstance(element, kind)]

    def holding(self, roles: Collection[str], missing: str) -> "Whiteboard":
        """This board, when an element on it draws one of roles. A board with none is not the drawing a practice reads,
        so it raises *UnreadableBoard*, saying the board holds no missing."""
        if not any(element.role in roles for element in self.whole_elements):
            raise UnreadableBoard(f"The board holds no {missing}")
        return self

    def add(self, element: BoardElement) -> BoardElement:
        """Put element in front of every element already on the board; a section goes behind every element but other
        sections, so it never covers what it holds. A block wider than a board draws one goes on as its pieces."""
        for piece in element.pieces():
            self._add_one(piece)
        return element

    def _add_one(self, element: BoardElement) -> None:
        if element.id in self._elements:
            raise ValueError(f"The board already holds an element {element.id!r}")
        if not element.HOLDS_OTHERS:
            self._elements[element.id] = element
            return
        sections = {key: held for key, held in self._elements.items() if held.HOLDS_OTHERS}
        rest = {key: held for key, held in self._elements.items() if key not in sections}
        self._elements = {**sections, element.id: element, **rest}

    def draw(self, node: WhiteboardNode) -> None:
        """Add every element node draws."""
        for element in node.board_elements():
            self.add(element)

    def element(self, element_id: str) -> Optional[BoardElement]:
        return self._elements.get(element_id)

    @property
    def _meta(self) -> Dict[str, object]:
        return {"v": 1, "title": self.title, "order": self.order}

    def save(self) -> str:
        """The board as a ``.whiteboard`` file: its meta, every element's record, and the versions they were read at."""
        board = dict(self._meta)
        board["elements"] = {element.id: element.record for element in self.elements}
        if self._versions:
            board["versions"] = dict(self._versions)
        return json.dumps(board, indent=1, ensure_ascii=False)

    @classmethod
    def from_text(cls, text: str) -> "Whiteboard":
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
        loaded._versions = {str(key): int(value) for key, value in board.get("versions", {}).items()}
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

    def _writes(self, previous: Optional["Whiteboard"] = None) -> List[StoreWrite]:
        """The store writes that turn previous, the board as it is in Claude, into this board: its meta, then each
        element a practice drew that this board no longer holds deleted, then each new element set and each changed
        element updated with only its changed fields. The deletes go first so a board people watch while the writes
        land never shows the old drawing under the new one. Elements a person added, of a kind no practice draws, are
        left alone and kept at the back of the order."""
        before = previous or Whiteboard()
        kept = [element.id for element in before.elements if isinstance(element, OtherElement)]
        meta = {**self._meta, "order": kept + self.order}
        return [StoreWrite("set", "board", "meta", meta, before._versions.get("meta")), *self._deletes(before), *self._element_writes(before)]

    def batches(self, previous: Optional["Whiteboard"] = None) -> List[List[Dict[str, object]]]:
        """The writes against previous as ArtifactData ``batch`` entries, at most fifty a batch, in order."""
        entries = [write.entry for write in self._writes(previous)]
        return [entries[start:start + BATCH_SIZE] for start in range(0, len(entries), BATCH_SIZE)]

    def _element_writes(self, before: "Whiteboard") -> List[StoreWrite]:
        found: List[StoreWrite] = []
        for element in self.elements:
            had = before.element(element.id)
            if had is None:
                found.append(StoreWrite("set", "elements", element.id, element.record))
                continue
            changed = {name: value for name, value in element.record.items() if had.record.get(name) != value}
            changed.update({name: CLEARED for name in had.record if name not in element.record})
            if changed:
                found.append(StoreWrite("update", "elements", element.id, changed, before._versions.get(element.id)))
        return found

    def _deletes(self, before: "Whiteboard") -> List[StoreWrite]:
        return [
            StoreWrite("delete", "elements", element.id, None, before._versions.get(element.id)) for element in before.elements
            if self.element(element.id) is None and not isinstance(element, OtherElement)
        ]


class BoardLinks:
    """The address of the board in Claude each ``.whiteboard`` file in one folder was published to, by the file's name,
    kept beside the files in the folder's ``whiteboards.json``, as a design canvas keeps its versions' links in
    ``versions.json``: the next render updates the same board, and a page opens the board instead of the file."""

    RECORD = "whiteboards.json"

    def __init__(self, folder: Path) -> None:
        self._record = folder / self.RECORD

    @classmethod
    def beside(cls, file: Path) -> "BoardLinks":
        """The addresses kept in the folder file is in."""
        return cls(file.parent)

    def of(self, file: Path) -> str:
        """The address of the board file was published to; none while it was never published."""
        return self._all().get(file.name, "")

    def file_published_to(self, url: str) -> Optional[Path]:
        """The whiteboard file in this folder whose board is at url; none when no file here was published to it."""
        name = next((name for name, kept in self._all().items() if kept == url), "")
        return self._record.parent / name if name else None

    def record(self, file: Path, url: str) -> None:
        """Keep url as the address of the board file was published to."""
        self._record.write_text(json.dumps({**self._all(), file.name: url}, indent=2), encoding="utf-8")

    def _all(self) -> Dict[str, str]:
        """Every address kept; none when the folder keeps none, or keeps something that is no record of them."""
        try:
            kept = json.loads(self._record.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        return {str(name): str(url) for name, url in kept.items()} if isinstance(kept, dict) else {}
