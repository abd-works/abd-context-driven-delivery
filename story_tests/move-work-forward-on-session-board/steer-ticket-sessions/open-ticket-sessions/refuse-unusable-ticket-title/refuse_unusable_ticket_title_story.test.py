from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Open Ticket Sessions
# Map: ../../../../.context/story-map.md#s-board-app----refuse-unusable-ticket-title
# Model: ../../../../.context/kanban-model.md
# Realizations: ../../../../.context/session-board-scenario-realization.md

# Story: Refuse Unusable Ticket Title
# Actor: Board App
with story("Refuse Unusable Ticket Title"):
    with scenario("Refuse a title that gives a ticket no name"):
        # Evidence: tested by steer-ticket-sessions.story.shared.py, replayed by the domain spec.
        with given("the [board](../../../../.context/kanban-model.md#board) shows checkout-flow"):
            pass
        with when("the Person opens a new ticket whose title is empty, or 日本語"):
            # Person -> Ticket.create(title)
            # CardPlacement -> CardName.for_new_card() <- TitleNamesNothingError
            pass
        with then("the board says the title gives no name, naming the title"):
            pass
        with and_("no session file is written in .sessions itself"):
            pass
    with scenario("Refuse a title whose name a ticket already has"):
        # Evidence: tested by steer-ticket-sessions.story.shared.py, replayed by the domain spec.
        with given("the [ticket](../../../../.context/kanban-model.md#ticket--card) pet-visits is titled Pet visits"):
            pass
        with when("the Person opens a new ticket titled PET VISITS"):
            # Person -> Ticket.create('PET VISITS')
            # CardPlacement -> CardPlacement.free_name_for('PET VISITS') <- TicketNameTakenError
            pass
        with then("the board says a ticket named pet-visits already exists"):
            pass
        with and_("pet-visits is still titled Pet visits"):
            pass
        with when("the Person opens a new ticket titled main"):
            # Person -> Ticket.create('main')
            # CardPlacement -> CardPlacement.free_name_for('main') <- TicketNameTakenError
            pass
        with then("the board says a ticket named main already exists"):
            pass
    with scenario("Refuse a title too long for a name"):
        # Evidence: tested by steer-ticket-sessions.story.shared.py, replayed by the domain spec.
        with given("the [board](../../../../.context/kanban-model.md#board) shows checkout-flow"):
            pass
        with when("the Person opens a new ticket whose title makes a name longer than 64 characters"):
            # Person -> Ticket.create(title)
            # CardPlacement -> CardName.for_new_card() <- TitleTooLongError
            pass
        with then("the board says the title makes too long a name, naming the limit"):
            pass
        with and_("no session folder is made for it"):
            pass
