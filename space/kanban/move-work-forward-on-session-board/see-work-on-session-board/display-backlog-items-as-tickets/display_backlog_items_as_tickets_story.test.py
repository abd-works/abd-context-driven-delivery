from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: See Work On Session Board
# Map: ../../../.context/story-map.md#s-board-app----display-backlog-items-as-tickets
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Display Backlog Items As Tickets
# Actor: Board App
with story("Display Backlog Items As Tickets"):
    with scenario("Show each idea file in the Backlog"):
        # Evidence: observed: kanban_spec 'should show each backlog item in the Backlog column'; kanban_tools_spec 'should give a backlog item its text', 'should say when a backlog item last changed'.
        with given("the [repository](../../../.context/kanban-model.md#repo)'s .sessions/_backlog/ holds search-the-catalog.md headed Search the catalog with the text An idea."):
            pass
        with when("the session board reads the [board](../../../.context/kanban-model.md#board)"):
            # Board page -> Board.show()
            # Board -> Board.backlog_items
            # BacklogItem -> BacklogItem.title, BacklogItem.text, BacklogItem.last_activity
            pass
        with then("the Backlog [column](../../../.context/kanban-model.md#column) shows the [backlog item](../../../.context/kanban-model.md#backlogitem--card) Search the catalog"):
            pass
        with and_("selecting it shows its text An idea. in the details"):
            pass
        with and_("its last activity is when search-the-catalog.md last changed"):
            pass
    with scenario("Show a ticket kept in the Backlog under its own file"):
        # Evidence: observed: kanban_spec 'that is kept as a folder holding a file of its own name' — 'should be in the Backlog under the heading of that file', 'should show the text of that file'; 'should be off the stages'.
        with given("the Backlog folder holds the folder gift-cards with its session log and gift-cards.md headed Gift cards"):
            pass
        with and_("gift-cards.md holds the text Sell them at the till."):
            pass
        with when("the session board reads the [board](../../../.context/kanban-model.md#board)"):
            # Board -> Board.backlog_items
            # Board <- one BacklogItem for gift-cards/gift-cards.md
            # Board -> Board.tickets
            # Board <- no ticket for gift-cards
            pass
        with then("the Backlog [column](../../../.context/kanban-model.md#column) shows one [backlog item](../../../.context/kanban-model.md#backlogitem--card) Gift cards with the text Sell them at the till."):
            pass
        with but_("no [stage](../../../.context/kanban-model.md#stage--column) shows a [ticket](../../../.context/kanban-model.md#ticket--card) for gift-cards"):
            pass
    with scenario("Name an item that has no heading by its file name"):
        # Evidence: inferred: BacklogItem.title in space/kanban/backlog_item.py; no spec writes an item without a heading.
        with given("the Backlog folder holds returns-and-refunds.md with no # heading"):
            pass
        with when("the session board reads the [board](../../../.context/kanban-model.md#board)"):
            # Board -> Board.backlog_items
            # BacklogItem -> BacklogItem.title
            # BacklogItem <- the file name in words
            pass
        with then("the Backlog [column](../../../.context/kanban-model.md#column) shows the [backlog item](../../../.context/kanban-model.md#backlogitem--card) Returns and refunds"):
            pass
