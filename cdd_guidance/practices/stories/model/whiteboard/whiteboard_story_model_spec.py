"""Mamba spec: a story map drawn on a Claude Whiteboard reads back as the same map.

A whiteboard story map holds epics, stories, their kind, and their actors; scenarios live in the story files, as they
do for drawio and miro."""

from mamba import description, context, it


with description("a story map drawn on a Claude whiteboard"):
    with it("should read back every epic, story held by any epic, kind, and actor"):
        pass

    with it("should copy itself as a whiteboard story map"):
        pass

    with context("with a story under a sub-epic"):
        with it("should draw the story as a card below its sub-epic's bar"):
            pass

        with it("should draw the story's actor above the card"):
            pass

    with context("that is drawn twice"):
        with it("should give each epic and story the same element id both times"):
            pass

    with context("that is read from a board with no story-map elements"):
        with it("should refuse the board"):
            pass
