"""Mamba spec: a Claude Whiteboard board as a practice draws it, saves it, and sends it to the board's store."""

from expects import be_above, be_below, contain, equal, expect, raise_error
from mamba import before, context, description, it

import json
import tempfile
from pathlib import Path

from harness.whiteboard import Arrow, BoardElement, Box, ElementId, KeepsDocumentOnBoard, Label, Section, Shape, UnreadableBoard, Whiteboard, WhiteboardNode
from harness.markdown.format import Format, SourceDocument
from harness.installation.data_class import data_of
from harness.whiteboard.whiteboard import STORE_RECORD_BYTES, StoreWrite


class CardNode(WhiteboardNode):
    """A node a diagram placed at a box, drawn as one card."""

    def __init__(self, element_id: str, box, text: str = "Submit Order") -> None:
        self.element_id = element_id
        self.box = Box(*box)
        self.text = text

    def board_box(self):
        return self.box

    def board_elements(self):
        return [self.board_shape(self.element_id, kind="rounded", color="yellow", size="small", text=self.text)]


def board_of_two_cards(first_box: tuple[float, float, float, float] = (20, 40, 60, 50), second_text: str = "Submit Order") -> Whiteboard:
    """Two cards joined by an arrow; the first drawn at first_box, the second with second_text."""
    board = Whiteboard("Orders")
    board.draw(CardNode("story.a1", first_box))
    board.draw(CardNode("story.b2", (100, 40, 60, 50), second_text))
    board.add(Arrow("arrow.ab", from_id="story.a1", to_id="story.b2", from_side="right", to_side="left", label="then"))
    return board


def read_at(board: Whiteboard, versions: dict[str, int]) -> Whiteboard:
    """The board as it is read from Claude, each record at the store version given for it."""
    return Whiteboard.from_text(json.dumps({**json.loads(board.save()), "versions": versions}))


with description("a whiteboard") as self:
    with context("with a shape drawn by a node at its box"):
        with before.each:
            board = Whiteboard("Orders")
            board.draw(CardNode("story.a1", (20, 40, 60, 50)))
            self.record = board.element("story.a1").record

        with it("should write the shape at the box's x, y, width and height"):
            expect([self.record[name] for name in ("x", "y", "w", "h")]).to(equal([20, 40, 60, 50]))

        with it("should write the shape's kind, colour, size and text"):
            expect([self.record[name] for name in ("type", "kind", "color", "size", "text")]).to(
                equal(["shape", "rounded", "yellow", "small", "Submit Order"])
            )

    with context("with a section and the shapes it holds"):
        with it("should list the section before the shapes it holds in board order"):
            board = Whiteboard("Orders")
            board.draw(CardNode("story.a1", (20, 40, 60, 50)))
            board.add(Section("epic.e1", box=Box(0, 0, 200, 120), text="Place Order"))
            expect(board.order).to(equal(["epic.e1", "story.a1"]))

    with context("with an arrow between two shapes"):
        with before.each:
            self.record = board_of_two_cards().element("arrow.ab").record

        with it("should join the shapes by their element ids and sides"):
            expect([self.record[name] for name in ("from", "to", "fromSide", "toSide")]).to(
                equal(["story.a1", "story.b2", "right", "left"])
            )

        with it("should carry the arrow's label"):
            expect(self.record["label"]).to(equal("then"))

    with context("with a title that wraps nowhere"):
        with it("should write no wrap, so its words run on one line rather than one word to a line"):
            expect("wrap" in Label("title", x=0, y=0, text="Shop - Classes", size="large").record).to(equal(False))

    with context("that is saved and loaded again"):
        with it("should load the same title, elements and order"):
            board = board_of_two_cards()
            loaded = Whiteboard.from_text(board.save())
            expect((loaded.title, loaded.order, [element.record for element in loaded.elements])).to(
                equal((board.title, board.order, [element.record for element in board.elements]))
            )

    with context("read back by kind"):
        with before.each:
            self.board = board_of_two_cards()
            self.board.add(Section("lane.l1", box=Box(0, 0, 300, 120), text="Release 1"))
            self.board.add(Label("title", x=0, y=-40, text="Orders"))

        with it("should answer its containers as its sections"):
            expect([element.id for element in self.board.sections]).to(equal(["lane.l1"]))

        with it("should answer its other blocks as its shapes"):
            expect([element.id for element in self.board.shapes]).to(equal(["story.a1", "story.b2"]))

        with it("should answer its words as its labels"):
            expect([element.id for element in self.board.labels]).to(equal(["title"]))

        with it("should answer its lines as its arrows"):
            expect([element.id for element in self.board.arrows]).to(equal(["arrow.ab"]))

    with context("read by a practice that needs an element of a role"):
        with it("should answer the board when an element draws that role"):
            board = board_of_two_cards()
            expect(board.holding({"story"}, "story")).to(equal(board))

        with it("should refuse a board with none as unreadable, naming what it lacks"):
            expect(lambda: board_of_two_cards().holding({"epic"}, "story-map epic")).to(
                raise_error(UnreadableBoard, "The board holds no story-map epic")
            )

    with context("that is loaded from text that is not a board"):
        with it("should refuse it as an unreadable board"):
            expect(lambda: Whiteboard.from_text("<mxfile/>")).to(raise_error(UnreadableBoard))

    with context("with a previous board on which a person moved a shape"):
        with before.each:
            previous = board_of_two_cards(first_box=(500, 300, 60, 50))
            board = board_of_two_cards()
            board.draw(CardNode("story.c3", (180, 40, 60, 50)))
            self.board = board.keep_places(previous)

        with it("should keep the moved shape at the person's place"):
            expect(self.board.element("story.a1").box).to(equal(Box(500, 300, 60, 50)))

        with it("should keep a new shape where the render placed it"):
            expect(self.board.element("story.c3").box).to(equal(Box(180, 40, 60, 50)))

    with context("that writes itself against the previous board"):
        with before.each:
            previous = board_of_two_cards()
            previous.draw(CardNode("story.gone", (260, 40, 60, 50)))
            previous = read_at(previous, {"meta": 3, "story.b2": 7, "story.gone": 9})
            board = board_of_two_cards(second_text="Pay Order")
            board.draw(CardNode("story.new", (180, 40, 60, 50)))
            self.board = board
            self.entries = board.batches(previous)[0]
            self.by_key = {f"{entry['collection']}/{entry['doc_id']}": entry for entry in self.entries}

        with it("should set the board meta with the title and order, pinned to the version read"):
            expect(self.entries[0]).to(equal(StoreWrite(
                "set", "board", "meta", {"v": 1, "title": "Orders", "order": ["story.a1", "story.b2", "arrow.ab", "story.new"]}, 3,
            ).entry))

        with it("should set each element the previous board did not hold as a store batch entry"):
            expect(self.by_key["elements/story.new"]).to(equal({
                "op": "set", "collection": "elements", "doc_id": "story.new", "data": self.board.element("story.new").record,
            }))

        with it("should update only the changed fields of a changed element, pinned to the version read"):
            expect(self.by_key["elements/story.b2"]).to(equal(StoreWrite("update", "elements", "story.b2", {"text": "Pay Order"}, 7).entry))

        with it("should delete each element the board no longer holds, pinned to the version read"):
            expect(self.by_key["elements/story.gone"]).to(equal(StoreWrite("delete", "elements", "story.gone", None, 9).entry))

        with it("should delete before it sets or updates, so a watched board never shows both drawings"):
            ops = [entry["op"] for entry in self.entries[1:]]
            expect(ops.index("delete")).to(be_below(min(ops.index("set"), ops.index("update"))))

        with it("should clear a field the element no longer has"):
            previous = Whiteboard("Orders")
            previous.add(Section("lane.l1", box=Box(0, 0, 200, 120), text="Release 1"))
            previous = read_at(previous, {"meta": 1, "lane.l1": 4})
            board = Whiteboard("Orders")
            board.add(Section("lane.l1", box=Box(0, 0, 200, 120)))
            expect(board.batches(previous)[0][1]).to(equal(StoreWrite("update", "elements", "lane.l1", {"text": {"__delete__": True}}, 4).entry))

        with it("should write nothing for an element that did not change"):
            expect("elements/story.a1" in self.by_key).to(equal(False))

    with context("with more writes than one store batch takes"):
        with it("should split the writes into batches of at most fifty"):
            board = Whiteboard("Orders")
            for index in range(60):
                board.draw(CardNode(f"story.s{index}", (index * 70, 40, 60, 50)))
            expect([len(batch) for batch in board.batches()]).to(equal([50, 11]))

    with context("with a block wider than a board draws one"):
        with before.each:
            self.board = Whiteboard("Orders")
            self.board.add(Shape("epic.e1", box=Box(100, 0, 20000, 60), text="Move Work Forward"))

        with it("should draw it as equal pieces side by side, none wider than a board draws"):
            expect([(element.id, element.box) for element in self.board.elements]).to(equal([
                ("epic.e1", Box(100, 0, 20000 / 3, 60)),
                ("epic.e1~2", Box(100 + 20000 / 3, 0, 20000 / 3, 60)),
                ("epic.e1~3", Box(100 + 2 * 20000 / 3, 0, 20000 / 3, 60)),
            ]))

        with it("should write the block's words on its first piece only"):
            expect([element.text for element in self.board.elements]).to(equal(["Move Work Forward", "", ""]))

        with it("should read the pieces back as the one block they draw"):
            read = Whiteboard.from_text(self.board.save()).whole_elements
            expect([(element.id, element.box) for element in read]).to(equal([("epic.e1", Box(100, 0, 20000, 60))]))

    with context("with a block taller than a board draws one"):
        with it("should refuse it"):
            board = Whiteboard("Orders")
            expect(lambda: board.add(Shape("lane.l1", box=Box(0, 0, 100, 9000)))).to(raise_error(ValueError))


_STORY_MAP = SourceDocument(Format("markdown"), "# Story Map\n\n## Order\n\nA customer orders books.\n")


with description("a whiteboard that keeps the document it was drawn from") as self:
    with before.each:
        board = board_of_two_cards()
        board.kept_document = _STORY_MAP
        self.board = board
        self.loaded = Whiteboard.from_text(board.save())

    with it("should give back the document, its format and every line of its text, once saved and loaded"):
        expect(self.loaded.kept_document).to(equal(_STORY_MAP))

    with it("should name the document's format and its number of parts in the board's meta"):
        meta = self.board.batches()[0][0]
        expect(meta["data"]["document"]).to(equal({"format": "markdown", "parts": 1}))

    with it("should keep the document's text on the board in Claude, in a record of its own"):
        expect(_parts_written(self.board.batches())).to(equal({"document-0": {"text": _STORY_MAP.text}}))

    with it("should draw nothing more"):
        expect(self.loaded.order).to(equal(board_of_two_cards().order))

    with context("that keeps none"):
        with it("should answer no document"):
            expect(Whiteboard.from_text(board_of_two_cards().save()).kept_document).to(equal(None))

    # The board's store takes a record of at most 262,144 bytes, and the story map's markdown outgrew one: the document
    # is kept in numbered parts, each under the limit, that read back whole. Cutting a document this large takes a while,
    # so the board, its writes and the boards it is drawn over are made once, before the examples, which only read them.
    with context("larger than a record of the board's store holds"):
        with before.all:
            board = board_of_two_cards()
            board.kept_document = _LARGE_MAP
            saved = board.save()
            batches = board.batches()
            longer = board_of_two_cards()
            longer.kept_document = SourceDocument(Format("markdown"), _LARGE_MAP.text * 2)
            self.saved = saved
            self.parts = _parts_written(batches)
            self.meta = batches[0][0]["data"]
            self.written_again = _parts_written(Whiteboard.from_text(saved).batches(Whiteboard.from_text(saved)))
            self.taken_away = [entry["doc_id"] for batch in board.batches(longer) for entry in batch
                               if entry["op"] == "delete" and entry["collection"] == "board"]
            self.longer_parts = len(_parts_written(longer.batches()))

        with it("should keep it in several numbered parts"):
            expect(sorted(self.parts)).to(equal([f"document-{number}" for number in range(len(self.parts))]))
            expect(len(self.parts)).to(be_above(1))

        with it("should keep every part under the store's limit for a record"):
            expect(max(len(json.dumps(part, ensure_ascii=False).encode("utf-8")) for part in self.parts.values())).to(be_below(STORE_RECORD_BYTES))

        with it("should name as many parts in the board's meta as it writes"):
            expect(self.meta["document"]).to(equal({"format": "markdown", "parts": len(self.parts)}))

        with it("should read the parts back as the whole document, from the board in Claude saved as one"):
            read = {**self.meta, "elements": {}, "document_parts": [self.parts[f"document-{number}"]["text"] for number in range(len(self.parts))]}
            expect(Whiteboard.from_text(json.dumps(read)).kept_document).to(equal(_LARGE_MAP))

        with it("should keep the whole document in the .whiteboard file"):
            expect(Whiteboard.from_text(self.saved).kept_document).to(equal(_LARGE_MAP))

        with context("drawn again over the board that keeps it already"):
            with it("should write no part again"):
                expect(self.written_again).to(equal({}))

        with context("drawn over a board that kept a longer document"):
            with it("should take away the parts it no longer needs"):
                expect(self.taken_away).to(equal([f"document-{number}" for number in range(len(self.parts), self.longer_parts)]))


def _parts_written(batches) -> dict:
    """The document parts batches set on the board, by record id."""
    return {entry["doc_id"]: entry["data"] for batch in batches for entry in batch
            if entry["op"] == "set" and entry["collection"] == "board" and entry["doc_id"] != "meta"}


_LARGE_MAP = SourceDocument(Format("markdown"), "".join(f"### (S) Person --> Story {number} with \"quotes\" — and a dash\n\nBuilt.\n\n" for number in range(9000)))


with description("a practice's whiteboard format that keeps the document a board was drawn from") as self:
    with before.each:
        self.format = KeepsDocumentOnBoard()
        self.kept = self.format.keeping(board_of_two_cards().save(), _STORY_MAP)

    with it("should read back the document the board it rendered keeps"):
        expect(self.format.document_kept_in(self.kept)).to(equal(_STORY_MAP))

    with it("should answer no document for text that is no board"):
        expect(self.format.document_kept_in("# Story Map")).to(equal(None))


with description("a whiteboard file's board in Claude") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp())
        self.file = self.folder / "story-map.whiteboard"
        self.file.write_text(Whiteboard("Story Map").save(), encoding="utf-8")

    with context("that was published"):
        with before.each:
            self.file.write_text(Whiteboard.published_to(self.file.read_text(encoding="utf-8"), "https://claude.ai/artifact/StoryMapBoard"), encoding="utf-8")

        with it("should answer the board's address, kept in the file itself"):
            expect(Whiteboard.board_of(self.file)).to(equal("https://claude.ai/artifact/StoryMapBoard"))

        with it("should keep the board the file holds"):
            expect(Whiteboard.from_text(self.file.read_text(encoding="utf-8")).title).to(equal("Story Map"))

        with it("should keep the address when the board is drawn over the file again"):
            expect(Whiteboard.board_in(Whiteboard("Story Map").drawn_over(self.file.read_text(encoding="utf-8")))).to(
                equal("https://claude.ai/artifact/StoryMapBoard"))

        with it("should send the address to no record of the board's store"):
            stored = [write for batch in Whiteboard.from_text(self.file.read_text(encoding="utf-8")).batches() for write in batch]
            expect([write for write in stored if "StoryMapBoard" in json.dumps(write)]).to(equal([]))

    with context("that was never published"):
        with it("should answer no address"):
            expect(Whiteboard.board_of(self.file)).to(equal(""))

    with context("that is not on disk"):
        with it("should answer no address"):
            expect(Whiteboard.board_of(self.folder / "missing.whiteboard")).to(equal(""))

    with context("that holds text that is not a whiteboard file"):
        with it("should refuse to keep a board in it"):
            expect(lambda: Whiteboard.published_to("not json", "https://claude.ai/artifact/X")).to(raise_error(UnreadableBoard))


with description("an element's id"):
    with it("should hash a node's names to the length its practice keeps, after its role and its parts"):
        expect(ElementId.of("story", "epic:Order", "story:Pay", length=10, parts=("user",))).to(equal("story.user.341c6ae06a"))

    with it("should keep each practice's key length, so a board already published keeps its ids"):
        expect([len(ElementId.of("class", "Cart", length=length).key) for length in (10, 12)]).to(equal([10, 12]))

    with it("should name what it draws and what it names after that"):
        read = ElementId.read("region.body.9f8e7d6c5b")
        expect((read.role, read.parts, read.key)).to(equal(("region", ("body", "9f8e7d6c5b"), "9f8e7d6c5b")))

    with it("should be the id an element read back from a board holds"):
        board = Whiteboard.from_text(board_of_two_cards().save())
        expect(board.element("story.a1").id.role).to(equal("story"))


with description("a board drawn over the file it replaces"):
    with it("should keep each element where the file had it"):
        moved = board_of_two_cards(first_box=(500, 400, 60, 50)).save()
        expect(json.loads(board_of_two_cards().drawn_over(moved))["elements"]["story.a1"]["x"]).to(equal(500))

    with it("should be the board as drawn when there is no file yet"):
        expect(board_of_two_cards().drawn_over("")).to(equal(board_of_two_cards().save()))


with description("a whiteboard file's title") as self:
    with it("should be the file's name without its .whiteboard ending"):
        expect(Whiteboard.title_of(Path("tests/.context/story-map.whiteboard"))).to(equal("story-map"))

    with it("should keep a versioned file's version"):
        expect(Whiteboard.title_of(Path("story-map.version-2.whiteboard"))).to(equal("story-map.version-2"))

    with it("should keep a scoped file's scope in front"):
        expect(Whiteboard.title_of(Path("src/ordering/.context/ordering-model.whiteboard"))).to(equal("ordering-model"))

    with context("written into the file's text"):
        with before.each:
            board = Whiteboard("Orders")
            board.add(Label("title", x=0, y=-40, text="Orders"))
            self.saved = Whiteboard.from_text(Whiteboard.titled_for(board.save(), Path("orders-model.whiteboard")))

        with it("should title the board with the file's name"):
            expect(self.saved.title).to(equal("orders-model"))

        with it("should keep everything else the board holds"):
            expect([label.text for label in self.saved.labels]).to(equal(["Orders"]))

        with it("should refuse text that is no whiteboard file"):
            expect(lambda: Whiteboard.titled_for("<mxfile/>", Path("orders-model.whiteboard"))).to(raise_error(UnreadableBoard))
