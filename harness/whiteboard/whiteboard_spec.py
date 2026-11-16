"""Mamba spec: a Claude Whiteboard board as a practice draws it, saves it, and sends it to the board's store."""

from expects import be_below, equal, expect, raise_error
from mamba import before, context, description, it

from harness.whiteboard import Arrow, Box, Section, Shape, StoreWrite, UnreadableBoard, Whiteboard, WhiteboardNode


class CardNode(WhiteboardNode):
    """A node a diagram placed at a box, drawn as one card."""

    def __init__(self, element_id: str, box) -> None:
        self.element_id = element_id
        self.box = Box(*box)

    def board_box(self):
        return self.box

    def board_elements(self):
        return [self.board_shape(self.element_id, kind="rounded", color="yellow", size="small", text="Submit Order")]


def board_of_two_cards() -> Whiteboard:
    board = Whiteboard("Orders")
    board.draw(CardNode("story.a1", (20, 40, 60, 50)))
    board.draw(CardNode("story.b2", (100, 40, 60, 50)))
    board.add(Arrow("arrow.ab", from_id="story.a1", to_id="story.b2", from_side="right", to_side="left", label="then"))
    return board


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

    with context("that is saved and loaded again"):
        with it("should load the same title, elements and order"):
            board = board_of_two_cards()
            loaded = Whiteboard.from_text(board.save())
            expect((loaded.title, loaded.order, [element.record for element in loaded.elements])).to(
                equal((board.title, board.order, [element.record for element in board.elements]))
            )

    with context("that is loaded from text that is not a board"):
        with it("should refuse it as an unreadable board"):
            expect(lambda: Whiteboard.from_text("<mxfile/>")).to(raise_error(UnreadableBoard))

    with context("with a previous board on which a person moved a shape"):
        with before.each:
            previous = board_of_two_cards()
            previous.put(previous.element("story.a1").placed_at(Box(500, 300, 60, 50)))
            board = board_of_two_cards()
            board.draw(CardNode("story.c3", (180, 40, 60, 50)))
            self.board = board.keep_places(previous)

        with it("should keep the moved shape at the person's place"):
            expect(self.board.element("story.a1").place).to(equal(Box(500, 300, 60, 50)))

        with it("should keep a new shape where the render placed it"):
            expect(self.board.element("story.c3").place).to(equal(Box(180, 40, 60, 50)))

    with context("that writes itself against the previous board"):
        with before.each:
            previous = board_of_two_cards()
            previous.draw(CardNode("story.gone", (260, 40, 60, 50)))
            previous.versions = {"meta": 3, "story.b2": 7, "story.gone": 9}
            board = board_of_two_cards()
            moved = board.element("story.b2")
            board.put(Shape(
                moved.id, box=moved.box, kind=moved.kind, color=moved.color,
                size=moved.size, text="Pay Order",
            ))
            board.draw(CardNode("story.new", (180, 40, 60, 50)))
            self.board = board
            self.writes = board.writes(previous)
            self.by_key = {f"{write.collection}/{write.doc_id}": write for write in self.writes}

        with it("should set the board meta with the title and order, pinned to the version read"):
            expect(self.writes[0]).to(equal(StoreWrite(
                "set", "board", "meta", {"v": 1, "title": "Orders", "order": ["story.a1", "story.b2", "arrow.ab", "story.new"]}, 3,
            )))

        with it("should set each element the previous board did not hold as a store batch entry"):
            expect(self.by_key["elements/story.new"].entry).to(equal({
                "op": "set", "collection": "elements", "doc_id": "story.new", "data": self.board.element("story.new").record,
            }))

        with it("should update only the changed fields of a changed element, pinned to the version read"):
            expect(self.by_key["elements/story.b2"]).to(equal(StoreWrite("update", "elements", "story.b2", {"text": "Pay Order"}, 7)))

        with it("should delete each element the board no longer holds, pinned to the version read"):
            expect(self.by_key["elements/story.gone"]).to(equal(StoreWrite("delete", "elements", "story.gone", None, 9)))

        with it("should delete before it sets or updates, so a watched board never shows both drawings"):
            ops = [write.op for write in self.writes[1:]]
            expect(ops.index("delete")).to(be_below(min(ops.index("set"), ops.index("update"))))

        with it("should clear a field the element no longer has"):
            previous = Whiteboard("Orders")
            previous.add(Section("lane.l1", box=Box(0, 0, 200, 120), text="Release 1"))
            previous.versions = {"meta": 1, "lane.l1": 4}
            board = Whiteboard("Orders")
            board.add(Section("lane.l1", box=Box(0, 0, 200, 120)))
            expect(board.writes(previous)[1]).to(equal(StoreWrite("update", "elements", "lane.l1", {"text": {"__delete__": True}}, 4)))

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
