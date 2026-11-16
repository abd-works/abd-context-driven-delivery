"""Mamba spec: a Claude Whiteboard board as a practice draws it, saves it, and sends it to the board's store."""

from mamba import description, context, it


with description("a whiteboard"):
    with context("with a shape drawn by a node at its box"):
        with it("should write the shape at the box's x, y, width and height"):
            pass

        with it("should write the shape's kind, colour, size and text"):
            pass

    with context("with a section and the shapes it holds"):
        with it("should list the section before the shapes it holds in board order"):
            pass

    with context("with an arrow between two shapes"):
        with it("should join the shapes by their element ids and sides"):
            pass

        with it("should carry the arrow's label"):
            pass

    with context("that is saved and loaded again"):
        with it("should load the same title, elements and order"):
            pass

    with context("that is loaded from text that is not a board"):
        with it("should refuse it as an unreadable board"):
            pass

    with context("with a previous board on which a person moved a shape"):
        with it("should keep the moved shape at the person's place"):
            pass

        with it("should keep a new shape where the render placed it"):
            pass

    with context("that writes itself against the previous board"):
        with it("should set the board meta with the title and order"):
            pass

        with it("should set each element the previous board did not hold"):
            pass

        with it("should update only the changed fields of a changed element"):
            pass

        with it("should delete each element the board no longer holds"):
            pass

        with it("should write nothing for an element that did not change"):
            pass

    with context("with more writes than one store batch takes"):
        with it("should split the writes into batches of at most fifty"):
            pass
