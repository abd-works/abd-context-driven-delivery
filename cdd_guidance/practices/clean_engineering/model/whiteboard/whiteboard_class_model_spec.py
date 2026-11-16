"""Mamba spec: a Clean Engineering model drawn on a Claude Whiteboard reads back as the same model, as its drawio does."""

from mamba import description, context, it


with description("a class model drawn on a Claude whiteboard"):
    with it("should draw each module as a section holding its classes"):
        pass

    with it("should draw each class with its stereotypes, properties and operations"):
        pass

    with it("should draw each class's base as an arrow to the base"):
        pass

    with it("should read back every module, class, property, operation and base"):
        pass


with description("a modules view drawn on a Claude whiteboard"):
    with it("should draw each module with its purpose and seam terms"):
        pass

    with it("should draw each dependency as an arrow to the module it depends on"):
        pass

    with it("should read back every module with its purpose, seam terms and dependencies"):
        pass

    with context("that is read from a board with no modules or classes"):
        with it("should refuse the board as an unreadable source"):
            pass
