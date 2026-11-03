from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Display Board And Details For Repo
# Map: ../../../story-map.md#s-person----arrange-board-and-details
# Model: ../../../kanban-model.md
# Realizations: ../../../session-board-realization.md

# Story: Arrange Board And Details
# Actor: Person
with story("Arrange Board And Details"):
    with scenario("Give the board more height"):
        # Evidence: observed: board-client.spec 'should give the board the height a drag asks for'; story-actions.spec 'should give the board more height on a drag, and never close the details'.
        with given("the page is 900 pixels high"):
            pass
        with when("the Person resizes the board to 300 pixels"):
            # Person -> BoardLayoutClient.setBoardHeight(300, 900)
            pass
        with then("the [board](../../../kanban-model.md#board) region is 300 pixels high and the details take the rest"):
            pass
    with scenario("Keep both regions open"):
        # Evidence: observed: board-client.spec 'should not let a drag close the board', 'should not let a drag close the details'.
        with given("the page is 900 pixels high"):
            pass
        with when("the Person resizes the board to 10 pixels"):
            # Person -> BoardLayoutClient.setBoardHeight(10, 900)
            pass
        with then("the [board](../../../kanban-model.md#board) region stays 160 pixels high"):
            pass
        with when("the Person resizes the board to 5000 pixels"):
            # Person -> BoardLayoutClient.setBoardHeight(5000, 900)
            pass
        with then("the board region stops at 650 pixels, so the details stay open"):
            pass
    with scenario("Expand one region and show both again"):
        # Evidence: observed: board-client.spec 'should give one region the page', 'should bring the other back on a second press'; story-actions.spec 'should give a region the whole page and bring the other back'.
        with given("the board and the details share the page"):
            pass
        with when("the Person expands the board"):
            # Person -> BoardLayoutClient.toggleRegion('board')
            pass
        with then("the [board](../../../kanban-model.md#board) takes the whole page"):
            pass
        with when("the Person collapses the board"):
            # Person -> BoardLayoutClient.toggleRegion('board')
            pass
        with then("the board and the details share the page again"):
            pass
