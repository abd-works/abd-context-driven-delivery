"""A Claude Whiteboard board as a practice draws it: its elements, its file, and the store writes that update a board.

A board in Claude is a Whiteboard artifact whose store holds ``board/meta`` (``{v, title, order}``) and one
``elements/<id>`` record per element. A practice draws its diagram as a *Whiteboard*, saves it as a ``.whiteboard``
file beside its other formats, and an agent sends ``Whiteboard.batches(previous)`` to the artifact's store. The file
keeps the address of the board it was published to in its own ``board`` field, which the store never holds.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from dataclasses import dataclass, field, fields, replace
from typing import ClassVar, Collection, Dict, Iterable, List, Optional

from harness.markdown.format import Format, SourceDocument

ID_PATTERN = re.compile(r"^[A-Za-z0-9_.~:@+-]{1,40}$")
BATCH_SIZE = 50
"""The most writes the artifact store takes in one batch."""
MAX_SIDE = 8000
"""The widest or tallest block a board draws; the Whiteboard page draws a block over it at its default size."""
STORE_RECORD_BYTES = 262_144
"""The largest record the artifact store keeps, in bytes of its JSON."""
DOCUMENT_PART_BYTES = 200_000
"""The most bytes of JSON one part of a kept document is written as, well under a store record, so each part is kept."""
DOCUMENT_PART = "document-{}"
"""The id of each numbered part of the kept document among the board's records, beside its meta."""
BATCH_BYTES = 900_000
"""The most bytes of JSON one batch of writes is sent as, under the store's 1 MiB for a batch."""
CLEARED = {"__delete__": True}
"""What an update writes for a field the element no longer has, so the store drops it."""
PIECE_MARK = "~"
"""What joins a block's id to the number of each further piece of it."""
DrawnField = str | float | bool | list[str | float] | None
"""What one drawn field of an element holds: its words, colour or size, a measure, a flag such as an arrow's dash, or
the list of an arrow's heads or bends."""


class UnreadableBoard(ValueError):
    """Text that is not a saved board, so no practice reads a model from it."""


class ElementId(str):
    """An element's id on a board, which is how a board already published in Claude is updated in place: its role, then
    its parts, joined by dots, such as ``story.user.a1b2c3d4e5`` or ``region.body.9f8e7d6c5b``. A node a practice draws
    keeps one id from one render to the next because its last part is a key hashed from the node's names
    (``ElementId.of``), whose length each practice keeps (``WhiteboardNode.KEY_LENGTH``), so no published board is
    redrawn."""

    SEPARATOR = "."

    def __new__(cls, role: str, *parts: str) -> ElementId:
        return super().__new__(cls, cls.SEPARATOR.join([role, *parts]))

    @classmethod
    def of(cls, role: str, *names: str, length: int, parts: tuple[str, ...] = ()) -> ElementId:
        """The id of the node names name, in order from the map's root, as role, then parts, then the first length hex
        digits of the hash of those names: the one hash every practice keys its elements with."""
        return cls(role, *parts, hashlib.sha1("/".join(names).encode("utf-8")).hexdigest()[:length])

    @classmethod
    def read(cls, written: str) -> ElementId:
        """The id written as written, such as an element's key in a saved board."""
        role, *parts = str(written).split(cls.SEPARATOR)
        return cls(role, *parts)

    @property
    def role(self) -> str:
        """What the element draws: ``story`` for ``story.user.a1``."""
        return self.split(self.SEPARATOR, 1)[0]

    @property
    def parts(self) -> tuple[str, ...]:
        """What the id names after its role: ``("user", "a1")`` for ``story.user.a1``."""
        return tuple(self.split(self.SEPARATOR)[1:])

    @property
    def key(self) -> str:
        """The id's last part, the key a drawn node's names hash to; the role for an id of one part."""
        return self.rsplit(self.SEPARATOR, 1)[-1]


@dataclass(frozen=True)
class Box:
    """Where a drawn thing sits: its top-left corner, width and height, in board units or a drawing's pixels. The one
    rectangle a whiteboard element, a draw.io cell, and a laid-out diagram card are each placed in."""

    x: float
    y: float
    w: float
    h: float

    def holds(self, other: "Box") -> bool:
        """Whether other's middle lies inside this box, as a card inside the section drawn round it does."""
        middle_x, middle_y = other.center
        return self.x <= middle_x <= self.x + self.w and self.y <= middle_y <= self.y + self.h

    def overlaps(self, other: "Box") -> bool:
        """Whether this box and other share any area; boxes that only touch do not."""
        return not (
            self.x + self.w <= other.x
            or other.x + other.w <= self.x
            or self.y + self.h <= other.y
            or other.y + other.h <= self.y
        )

    def shifted(self, rightward: float, downward: float) -> "Box":
        """This box moved rightward and downward."""
        return Box(self.x + rightward, self.y + downward, self.w, self.h)

    def moved_to(self, left: float, top: float) -> "Box":
        """This box with its top-left corner at left and top."""
        return Box(left, top, self.w, self.h)

    def clear_gap_to(self, other: "Box") -> float:
        """The empty space between this box and other, corner to corner when they are apart both ways; 0 when they
        touch or overlap."""
        across = max(0.0, self.x - (other.x + other.w), other.x - (self.x + self.w))
        down = max(0.0, self.y - (other.y + other.h), other.y - (self.y + self.h))
        if across == 0.0 or down == 0.0:
            return across + down
        return (across ** 2 + down ** 2) ** 0.5

    @property
    def center(self) -> tuple[float, float]:
        """The middle of the box."""
        return (self.x + self.w / 2, self.y + self.h / 2)


@dataclass
class BoardElement:
    """One record on a board, under its element id; each kind writes the fields the Whiteboard type reads."""

    id: ElementId
    TYPE: ClassVar[str] = ""
    HOLDS_OTHERS: ClassVar[bool] = False
    """Whether the element is a container drawn round other elements, so it lies behind them."""
    STORE_NAMES: ClassVar[Dict[str, str]] = {
        "from_id": "from", "to_id": "to", "from_side": "fromSide", "to_side": "toSide", "text_align": "textAlign",
    }

    def __post_init__(self) -> None:
        if not ID_PATTERN.match(self.id):
            raise ValueError(f"Element id {self.id!r} is not 1-40 of [A-Za-z0-9_.~:@+-]")
        if not isinstance(self.id, ElementId):
            self.id = ElementId.read(self.id)

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
        if "box" in known:
            values["box"] = Box(*(float(values.pop(edge, 0)) for edge in ("x", "y", "w", "h")))
        return kind(id=element_id, **{name: value for name, value in values.items() if name in known and name != "id"})

    @property
    def role(self) -> str:
        """What the element draws, as its id names it: ``story`` for ``story.user.a1``."""
        return self.id.role

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
    elements it draws there; the board places them back to front as the nodes are drawn. Each practice keeps the length
    of the key its element ids hash a node's names to (``KEY_LENGTH``): Clean Engineering 12, the others 10, so a
    board already published keeps its ids."""

    KEY_LENGTH: ClassVar[int] = 10

    def board_box(self) -> Box:
        """The box the diagram placed this node in."""
        raise NotImplementedError

    def board_elements(self) -> List[BoardElement]:
        """The elements this node draws, back to front."""
        raise NotImplementedError

    def board_shape(self, element_id: ElementId, **drawn: DrawnField) -> Shape:
        """A shape with this element id at this node's box."""
        return Shape(element_id, box=self.board_box(), **drawn)


class Whiteboard:
    """A board: its title and its elements in back-to-front order."""

    SUFFIX = ".whiteboard"
    # The field of a ``.whiteboard`` file that keeps the address of the board in Claude the file was published to.
    BOARD = "board"

    @classmethod
    def board_in(cls, text: str) -> str:
        """The address of the board in Claude the ``.whiteboard`` file text was published to; empty for a file not
        published yet, and for text that is no whiteboard file, which no board was published from."""
        try:
            saved = json.loads(text)
        except (TypeError, ValueError):
            return ""
        return str(saved.get(cls.BOARD) or "") if isinstance(saved, dict) else ""

    @classmethod
    def board_of(cls, file: Path) -> str:
        """The address of the board in Claude the ``.whiteboard`` file at file was published to, kept in the file
        itself: the next render updates that board, and a page opens it instead of the file. Empty for a file not
        published yet, or not on disk."""
        return cls.board_in(file.read_text(encoding="utf-8")) if file.is_file() else ""

    @classmethod
    def published_to(cls, text: str, board: str) -> str:
        """The ``.whiteboard`` file text with board kept as the address it was published to, first in the file, and
        everything else it holds as it was. Text that is no whiteboard file is refused as an *UnreadableBoard*, since
        no board is published from it."""
        try:
            saved = json.loads(text)
        except (TypeError, ValueError) as error:
            raise UnreadableBoard(f"Not a whiteboard file: {error}") from error
        if not isinstance(saved, dict) or not isinstance(saved.get("elements"), dict):
            raise UnreadableBoard("Not a whiteboard file: it holds no elements")
        rest = {key: value for key, value in saved.items() if key != cls.BOARD}
        return json.dumps({cls.BOARD: board, **rest} if board else rest, indent=1, ensure_ascii=False)

    def __init__(self, title: str = "", elements: Iterable[BoardElement] = ()) -> None:
        self._title = title
        # The address of the board in Claude the file was published to, kept in the file and never sent to the board.
        self.board = ""
        # The document the board was drawn from, kept in its meta, where the board draws none of it.
        self.kept_document: Optional[SourceDocument] = None
        # The store version each record was read at, by element id and ``meta``; a board drawn by a practice has none.
        self._versions: Dict[str, int] = {}
        self._elements: Dict[str, BoardElement] = {}
        for element in elements:
            self.add(element)

    @property
    def title(self) -> str:
        return self._title

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
    def sections(self) -> List[Section]:
        """The whole containers on the board, back to front."""
        return [element for element in self.whole_elements if isinstance(element, Section)]

    @property
    def shapes(self) -> List[Shape]:
        """The whole blocks on the board that are no container, back to front."""
        return [element for element in self.whole_elements if isinstance(element, Shape)]

    @property
    def labels(self) -> List[Label]:
        return [element for element in self.whole_elements if isinstance(element, Label)]

    @property
    def arrows(self) -> List[Arrow]:
        return [element for element in self.whole_elements if isinstance(element, Arrow)]

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
        meta: Dict[str, object] = {"v": 1, "title": self.title, "order": self.order}
        if self.kept_document is not None:
            meta["document"] = {"format": str(self.kept_document.format), "text": self.kept_document.text}
        return meta

    def save(self) -> str:
        """The board as a ``.whiteboard`` file: the address of the board in Claude it was published to, when it was, its
        meta, every element's record, and the versions they were read at."""
        board: Dict[str, object] = {self.BOARD: self.board} if self.board else {}
        board.update(self._meta)
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
        loaded.board = str(board.get(cls.BOARD) or "")
        loaded.kept_document = _kept_document_in(board)
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

    def drawn_over(self, previous: str) -> str:
        """This board saved as a ``.whiteboard`` file, drawn over previous, the file's text before the render: every
        element previous also held stays where people put it (``keep_places``), and the board in Claude previous was
        published to stays its board; with no previous text, as drawn."""
        before = Whiteboard.from_text(previous) if previous else None
        self.board = self.board or (before.board if before is not None else "")
        return self.keep_places(before).save()

    def _writes(self, previous: Optional["Whiteboard"] = None) -> List[StoreWrite]:
        """The store writes that turn previous, the board as it is in Claude, into this board: its meta, then each
        element a practice drew that this board no longer holds deleted, then each new element set and each changed
        element updated with only its changed fields. The deletes go first so a board people watch while the writes
        land never shows the old drawing under the new one. Elements a person added, of a kind no practice draws, are
        left alone and kept at the back of the order."""
        before = previous or Whiteboard()
        kept = [element.id for element in before.elements if isinstance(element, OtherElement)]
        meta = {**self._meta, "order": kept + self.order}
        parts = _DocumentParts(self.kept_document)
        if self.kept_document is not None:
            meta["document"] = {"format": str(self.kept_document.format), "parts": len(parts.texts)}
        return [
            StoreWrite("set", "board", "meta", meta, before._versions.get("meta")),
            *parts.writes(_DocumentParts(before.kept_document), before._versions),
            *self._deletes(before),
            *self._element_writes(before),
        ]

    def batches(self, previous: Optional["Whiteboard"] = None) -> List[List[Dict[str, object]]]:
        """The writes against previous as ArtifactData ``batch`` entries, in order: at most fifty a batch, and no batch
        over the bytes the store takes in one, since a kept document's parts are each near a record's limit."""
        found: List[List[Dict[str, object]]] = [[]]
        size = 0
        for entry in (write.entry for write in self._writes(previous)):
            written = len(json.dumps(entry, ensure_ascii=False).encode("utf-8"))
            if found[-1] and (len(found[-1]) == BATCH_SIZE or size + written > BATCH_BYTES):
                found.append([])
                size = 0
            found[-1].append(entry)
            size += written
        return found if found[-1] else []

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


def _kept_document_in(board: Dict[str, object]) -> Optional[SourceDocument]:
    """The document a ``.whiteboard`` file keeps whole in its meta, or a store read keeps in the numbered parts its meta
    counts, saved beside it as ``document_parts``, in order; none when it keeps neither."""
    kept = board.get("document")
    if not isinstance(kept, dict):
        return None
    if isinstance(kept.get("text"), str):
        return SourceDocument(Format(str(kept.get("format", ""))), kept["text"])
    parts = board.get("document_parts")
    if not isinstance(parts, list) or len(parts) != kept.get("parts"):
        return None
    return SourceDocument(Format(str(kept.get("format", ""))), "".join(str(part) for part in parts))


class _DocumentParts:
    """A kept document's text cut into numbered parts at line ends, each written as one record of the board's store
    under ``DOCUMENT_PART_BYTES``, since the whole document outgrows a record. The same text always cuts the same way,
    so a render writes only the parts that changed."""

    def __init__(self, document: Optional[SourceDocument]) -> None:
        self.texts: List[str] = self._cut(document.text) if document is not None else []

    def writes(self, before: "_DocumentParts", versions: Dict[str, int]) -> List[StoreWrite]:
        """The writes that turn before's parts into these: each part that differs set, each part past the last taken
        away."""
        record = DOCUMENT_PART.format
        changed = [
            StoreWrite("set", "board", record(number), {"text": text}, versions.get(record(number)))
            for number, text in enumerate(self.texts) if number >= len(before.texts) or before.texts[number] != text
        ]
        gone = [StoreWrite("delete", "board", record(number), None, versions.get(record(number))) for number in range(len(self.texts), len(before.texts))]
        return changed + gone

    def _cut(self, text: str) -> List[str]:
        """Each character is written as JSON on its own, so a part's size is the sum of its pieces' sizes."""
        parts: List[List[str]] = [[]]
        size = self._bytes("")
        for piece in self._pieces(text):
            grows = self._bytes(piece) - self._bytes("")
            if parts[-1] and size + grows > DOCUMENT_PART_BYTES:
                parts.append([])
                size = self._bytes("")
            parts[-1].append(piece)
            size += grows
        return ["".join(part) for part in parts]

    def _pieces(self, text: str) -> List[str]:
        """text's lines, with a line too long for a part on its own cut where it fills one."""
        pieces: List[str] = []
        for line in text.splitlines(keepends=True):
            while self._bytes(line) > DOCUMENT_PART_BYTES:
                cut = self._longest_fitting(line)
                pieces.append(line[:cut])
                line = line[cut:]
            pieces.append(line)
        return pieces

    def _longest_fitting(self, line: str) -> int:
        low, high = 1, len(line)
        while low < high:
            middle = (low + high + 1) // 2
            low, high = (middle, high) if self._bytes(line[:middle]) <= DOCUMENT_PART_BYTES else (low, middle - 1)
        return low

    def _bytes(self, text: str) -> int:
        return len(json.dumps({"text": text}, ensure_ascii=False).encode("utf-8"))


class KeepsDocumentOnBoard:
    """What a practice's whiteboard format mixes in, ahead of its model, to keep the document a board was drawn from in
    the board's meta: the render writes it there (``keeping``) and a render of the board back into that document's
    format writes over it (``document_kept_in``), so the prose the board cannot show comes back."""

    def document_kept_in(self, text: str) -> Optional[SourceDocument]:
        """The document text, a board, keeps; none for a board that keeps none, or text that is no board."""
        try:
            return Whiteboard.from_text(text).kept_document
        except UnreadableBoard:
            return None

    def keeping(self, rendered: object, document: SourceDocument) -> object:
        """rendered, a board, keeping document; anything that is no board as it is."""
        if not isinstance(rendered, str) or not rendered.strip():
            return rendered
        try:
            board = Whiteboard.from_text(rendered)
        except UnreadableBoard:
            return rendered
        board.kept_document = document
        return board.save()
