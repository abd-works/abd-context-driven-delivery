"""Mamba spec: a Claude Whiteboard board as a practice draws it, saves it, and sends it to the board's store."""

from expects import be_below, equal, expect, raise_error
from mamba import before, context, description, it

import json
import tempfile
from pathlib import Path

from harness.whiteboard import BoardElement, BoardLinks, Box, UnreadableBoard, Whiteboard, WhiteboardNode
from harness.whiteboard.whiteboard import StoreWrite


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
    board.add(BoardElement.arrow("arrow.ab", from_id="story.a1", to_id="story.b2", from_side="right", to_side="left", label="then"))
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
            board.add(BoardElement.section("epic.e1", Box(0, 0, 200, 120), text="Place Order"))
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
            expect("wrap" in BoardElement.words("title", Box(0, 0, 0, 0), text="Shop - Classes", size="large").record).to(equal(False))

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
            self.board.add(BoardElement.section("lane.l1", Box(0, 0, 300, 120), text="Release 1"))
            self.board.add(BoardElement.words("title", Box(0, -40, 0, 0), text="Orders"))

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
            previous.add(BoardElement.section("lane.l1", Box(0, 0, 200, 120), text="Release 1"))
            previous = read_at(previous, {"meta": 1, "lane.l1": 4})
            board = Whiteboard("Orders")
            board.add(BoardElement.section("lane.l1", Box(0, 0, 200, 120)))
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
            self.board.add(BoardElement.shape("epic.e1", Box(100, 0, 20000, 60), text="Move Work Forward"))

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
            expect(lambda: board.add(BoardElement.shape("lane.l1", Box(0, 0, 100, 9000)))).to(raise_error(ValueError))


with description("a whiteboard file's board in Claude") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp())
        self.file = self.folder / "story-map.whiteboard"
        self.file.write_text(Whiteboard("Story Map").save(), encoding="utf-8")

    with context("that was published"):
        with before.each:
            BoardLinks.beside(self.file).record(self.file, "https://claude.ai/artifact/StoryMapBoard")

        with it("should answer the board's address, kept beside the file by its name"):
            expect(BoardLinks.beside(self.file).of(self.file)).to(equal("https://claude.ai/artifact/StoryMapBoard"))

    with context("that was never published"):
        with it("should answer no address"):
            expect(BoardLinks.beside(self.file).of(self.file)).to(equal(""))

    with context("with a record in the folder that is not one"):
        with it("should answer no address"):
            (self.folder / BoardLinks.RECORD).write_text("not json", encoding="utf-8")
            expect(BoardLinks.beside(self.file).of(self.file)).to(equal(""))
