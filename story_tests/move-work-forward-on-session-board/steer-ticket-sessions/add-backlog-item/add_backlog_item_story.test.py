from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../.context/story-map.md#s-person----add-backlog-item
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Add Backlog Item
# Actor: Person
#
# Acceptance criteria:
# - Start Backlog Item: the → arrow on a backlog card opens a ticket in Discovery, and a ticket that was moved to the Backlog comes back with its work. Observed: `BacklogItem.start`.
with story("Add Backlog Item"):
    with scenario("Add an idea to the Backlog"):
        # Evidence: observed: kanban_tools_spec 'that adds a backlog item' — 'should show the item in the Backlog with its text', 'should write the title and text to one markdown file'; backlog-item-client.spec 'with a title and text typed'.
        with given("the Backlog [column](../../../.context/kanban-model.md#column) has no [backlog item](../../../.context/kanban-model.md#backlogitem--card) titled Gift cards"):
            pass
        with when("the Person adds the backlog item Gift cards with the text Sell gift cards."):
            # Person -> BacklogItem.create('Gift cards', 'Sell gift cards.')
            # BacklogItem -> .sessions/_backlog/gift-cards.md: # Gift cards / Sell gift cards.
            # BacklogItem <- BacklogItem Gift cards
            # Board page -> Board.show()
            pass
        with then("the Backlog shows Gift cards with the text Sell gift cards."):
            pass
        with and_("Gift cards is selected and the form is closed"):
            pass
        with and_("a toast says Gift cards added to Backlog"):
            pass
    with scenario("Keep Add off with no title"):
        # Evidence: observed: backlog-item-client.spec 'should stay off with no title'; story-actions.spec 'should keep Add off with no title'.
        with given("the new backlog item form is open"):
            pass
        with but_("the Person has typed no title"):
            pass
        with when("the Person tries to add the item"):
            # Person -> BacklogDraftClient.add() <- nothing, with no title
            pass
        with then("Add stays off"):
            pass
        with and_("no [backlog item](../../../.context/kanban-model.md#backlogitem--card) is written"):
            pass
    with scenario("Refuse an idea whose title another idea's file has"):
        # Evidence: tested by maintain-tickets.story.shared.py, replayed by the domain spec.
        with given("the Backlog keeps the idea Gift cards, with the text Sell gift cards."):
            pass
        with when("the Person adds an idea titled Gift cards with another text"):
            # Person -> BacklogItem.create('Gift cards', text) <- BacklogItemTakenError
            pass
        with then("the board says the Backlog already keeps an idea in .sessions/_backlog/gift-cards.md"):
            pass
        with and_("that file still says Sell gift cards."):
            pass
    with scenario("Refuse an idea whose title gives its file no name"):
        # Evidence: tested by maintain-tickets.story.shared.py, replayed by the domain spec.
        with given("the [board](../../../.context/kanban-model.md#board) shows the Backlog"):
            pass
        with when("the Person adds an idea whose title is empty, or 日本語"):
            # Person -> BacklogItem.create(title, text)
            # BacklogItem -> CardName.for_new_card() <- TitleNamesNothingError
            pass
        with then("the board says the title gives no name"):
            pass
        with and_("no file named .md is written in the Backlog"):
            pass
